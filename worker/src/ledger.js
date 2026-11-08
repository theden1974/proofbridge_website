// LensLedger: the one place the lens door counts (audit 2026-11-08: no count, no key, no record of use).
// A Durable Object with SQLite, one instance named "ledger". It holds: addresses (one per client, minted by the client
// itself, no hand of the owner), events (what happened, when, how large, how long), invoices (bound to an address),
// returns (the reference readings, kept here first, mailed second, so a mail failure loses nothing).
// It holds no IP addresses: a caller's address is kept as a salted, truncated sha256 (salt made once inside this object), enough to bound minting per day.
import { DurableObject } from 'cloudflare:workers';

const DAY = 86_400_000;
const KEY = /^[a-z0-9]{24}$/;

export class LensLedger extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
      CREATE TABLE IF NOT EXISTS addresses (key TEXT PRIMARY KEY, created INTEGER, ip_hash TEXT, client TEXT, frames INTEGER DEFAULT 0, free_used INTEGER DEFAULT 0, credits INTEGER DEFAULT 0, paid_sats INTEGER DEFAULT 0, returns INTEGER DEFAULT 0, errors INTEGER DEFAULT 0, last_seen INTEGER, off INTEGER DEFAULT 0);
      CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER, key TEXT, kind TEXT, detail TEXT, size INTEGER, ms INTEGER);
      CREATE TABLE IF NOT EXISTS invoices (payment_hash TEXT PRIMARY KEY, key TEXT, created INTEGER, sats INTEGER, used INTEGER DEFAULT 0, bolt11 TEXT, expires_at INTEGER);
      CREATE TABLE IF NOT EXISTS returns (id TEXT PRIMARY KEY, ts INTEGER, key TEXT, seat TEXT, title TEXT, fingerprint TEXT, current INTEGER, reading TEXT, mailed INTEGER);
      CREATE INDEX IF NOT EXISTS ev_ts ON events (ts);
      CREATE INDEX IF NOT EXISTS ev_key ON events (key);
    `);
    if (!this.sql.exec(`SELECT v FROM meta WHERE k='since'`).toArray().length) this.sql.exec(`INSERT INTO meta VALUES ('since', ?)`, String(Date.now()));
    // a salt made once, kept only here: caller addresses are stored as salted hashes, not reversible from outside
    if (!this.sql.exec(`SELECT v FROM meta WHERE k='salt'`).toArray().length) this.sql.exec(`INSERT INTO meta VALUES ('salt', ?)`, [...crypto.getRandomValues(new Uint8Array(16))].map(b => b.toString(16).padStart(2, '0')).join(''));
    this.salt = this.sql.exec(`SELECT v FROM meta WHERE k='salt'`).one().v;
  }

  event(key, kind, detail = '', size = 0, ms = 0) {
    this.sql.exec(`INSERT INTO events (ts, key, kind, detail, size, ms) VALUES (?, ?, ?, ?, ?, ?)`, Date.now(), key || '', kind, String(detail).slice(0, 200), size | 0, ms | 0);
    if (key) {
      this.sql.exec(`UPDATE addresses SET last_seen=? WHERE key=?`, Date.now(), key);
      if (kind === 'error') this.sql.exec(`UPDATE addresses SET errors=errors+1 WHERE key=?`, key);
    }
    // keep the event table bounded: 90 days
    if (Math.random() < 0.02) this.sql.exec(`DELETE FROM events WHERE ts < ?`, Date.now() - 90 * DAY);
  }

  // anonymous counters (no row per call: the shared door and unknown addresses cannot fill the event table)
  count(kind) { this.sql.exec(`INSERT INTO meta VALUES (?, '1') ON CONFLICT(k) DO UPDATE SET v = CAST(CAST(v AS INTEGER) + 1 AS TEXT)`, 'n:' + kind); }
  counters() { const o = {}; for (const r of this.sql.exec(`SELECT k, v FROM meta WHERE k LIKE 'n:%'`).toArray()) o[r.k.slice(2)] = Number(r.v); return o; }

  // mint: one address per call, at most `perDay` per caller per day. No owner's hand. The caller is kept as a salted hash.
  async mint(ip, client, perDay) {
    const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(this.salt + '|' + ip));
    const ipHash = [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('').slice(0, 24);
    const since = Date.now() - DAY;
    const n = this.sql.exec(`SELECT COUNT(*) AS n FROM addresses WHERE ip_hash=? AND created>?`, ipHash, since).one().n;
    if (n >= perDay) { this.count('mint_refused'); return { ok: false, error: 'rate', detail: 'This caller already received ' + perDay + ' addresses today. Use one of them.' }; }
    const bytes = crypto.getRandomValues(new Uint8Array(24));
    const key = [...bytes].map(b => 'abcdefghijklmnopqrstuvwxyz0123456789'[b % 36]).join('');
    this.sql.exec(`INSERT INTO addresses (key, created, ip_hash, client, last_seen) VALUES (?, ?, ?, ?, ?)`, key, Date.now(), ipHash, String(client || '').slice(0, 80), Date.now());
    this.event(key, 'mint', client);
    return { ok: true, key };
  }

  address(key) {
    if (!KEY.test(key || '')) return null;
    const r = this.sql.exec(`SELECT * FROM addresses WHERE key=?`, key).toArray();
    return r.length ? r[0] : null;
  }

  // a frame: free while free_used < freeN, then one credit per frame. Returns what to do.
  frame(key, freeN, size, ms) {
    const a = this.address(key); if (!a) return { ok: false, error: 'unknown' };
    if (a.off) return { ok: false, error: 'off' };
    if (a.free_used < freeN) { this.sql.exec(`UPDATE addresses SET frames=frames+1, free_used=free_used+1 WHERE key=?`, key); this.event(key, 'frame', 'free', size, ms); return { ok: true, paid: false, free_left: freeN - a.free_used - 1 }; }
    if (a.credits > 0) { this.sql.exec(`UPDATE addresses SET frames=frames+1, credits=credits-1 WHERE key=?`, key); this.event(key, 'frame', 'credit', size, ms); return { ok: true, paid: true, credits_left: a.credits - 1 }; }
    this.event(key, 'frame_unpaid'); return { ok: false, error: 'payment_required', free_used: a.free_used };
  }
  invoice(key, payment_hash, sats, bolt11, expires_at) { this.sql.exec(`INSERT OR REPLACE INTO invoices VALUES (?, ?, ?, ?, 0, ?, ?)`, payment_hash, key, Date.now(), sats, bolt11 || '', expires_at | 0); this.event(key, 'invoice', payment_hash.slice(0, 12)); }
  pendingInvoice(key, maxAge) { const r = this.sql.exec(`SELECT * FROM invoices WHERE key=? AND used=0 AND created>? AND bolt11<>'' ORDER BY created DESC LIMIT 1`, key, Date.now() - maxAge).toArray(); return r.length ? r[0] : null; }
  invoicesSince(key, ms) { return this.sql.exec(`SELECT COUNT(*) AS n FROM invoices WHERE key=? AND created>?`, key, Date.now() - ms).one().n; }
  invoiceFor(key, payment_hash) { const r = this.sql.exec(`SELECT * FROM invoices WHERE payment_hash=? AND key=?`, payment_hash, key).toArray(); return r.length ? r[0] : null; }
  settle(key, payment_hash, sats, creditsPerPayment) {
    const inv = this.invoiceFor(key, payment_hash); if (!inv || inv.used) return false;
    this.sql.exec(`UPDATE invoices SET used=1 WHERE payment_hash=?`, payment_hash);
    this.sql.exec(`UPDATE addresses SET credits=credits+?, paid_sats=paid_sats+? WHERE key=?`, creditsPerPayment, sats, key);
    this.event(key, 'paid', sats + ' sats'); return true;
  }

  // a return is stored before any mail goes out
  storeReturn(key, { id, seat, title, fingerprint, current, reading }) {
    this.sql.exec(`INSERT INTO returns VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)`, id, Date.now(), key, seat, title, fingerprint, current ? 1 : 0, reading);
    this.sql.exec(`UPDATE addresses SET returns=returns+1 WHERE key=?`, key);
    this.event(key, 'return', seat, reading.length);
  }
  markMailed(id, ok) { this.sql.exec(`UPDATE returns SET mailed=? WHERE id=?`, ok ? 1 : 0, id); if (!ok) this.event('', 'mail_failed', id); }
  returnsSince(key, ms) { return this.sql.exec(`SELECT COUNT(*) AS n FROM returns WHERE key=? AND ts>?`, key, Date.now() - ms).one().n; }

  // public: alive and aggregate counts, nothing per client
  status() {
    const now = Date.now(), d1 = now - DAY, d7 = now - 7 * DAY;
    const c = (kind, since) => this.sql.exec(`SELECT COUNT(*) AS n FROM events WHERE kind=? AND ts>?`, kind, since).one().n;
    const last = this.sql.exec(`SELECT MAX(ts) AS t FROM returns`).one().t;
    const lastFrame = this.sql.exec(`SELECT MAX(ts) AS t FROM events WHERE kind='frame'`).one().t;
    return {
      since: new Date(Number(this.sql.exec(`SELECT v FROM meta WHERE k='since'`).one().v)).toISOString(),
      addresses: this.sql.exec(`SELECT COUNT(*) AS n FROM addresses`).one().n,
      frames: { today: c('frame', d1), week: c('frame', d7), all: c('frame', 0) },
      returns: { today: c('return', d1), week: c('return', d7), all: c('return', 0) },
      errors: { today: c('error', d1), week: c('error', d7) },
      mail_failed: { week: c('mail_failed', d7) },
      unpaid_frames: { week: c('frame_unpaid', d7) },
      refused: this.counters(),
      paid_sats: this.sql.exec(`SELECT COALESCE(SUM(paid_sats),0) AS s FROM addresses`).one().s,
      last_frame: lastFrame ? new Date(lastFrame).toISOString().slice(0, 16) + 'Z' : null,
      last_return: last ? new Date(last).toISOString().slice(0, 16) + 'Z' : null,
    };
  }
  // owner only (read token): per address, recent events, returns
  ledger(limit = 300) {
    return {
      addresses: this.sql.exec(`SELECT key, created, client, frames, free_used, credits, paid_sats, returns, errors, last_seen, off FROM addresses ORDER BY last_seen DESC LIMIT 500`).toArray(),
      events: this.sql.exec(`SELECT ts, key, kind, detail, size, ms FROM events ORDER BY id DESC LIMIT ?`, limit).toArray(),
      returns: this.sql.exec(`SELECT id, ts, key, seat, title, fingerprint, current, length(reading) AS size, mailed FROM returns ORDER BY ts DESC LIMIT 200`).toArray(),
    };
  }
  reading(id) { const r = this.sql.exec(`SELECT * FROM returns WHERE id=?`, id).toArray(); return r.length ? r[0] : null; }
  switchOff(key, off) { this.sql.exec(`UPDATE addresses SET off=? WHERE key=?`, off ? 1 : 0, key); this.event(key, off ? 'off' : 'on'); return this.address(key); }
}
