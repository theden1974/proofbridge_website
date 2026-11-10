// /mcp: the UX lens as a text any AI can load. Streamable HTTP, JSON-RPC.
//
// What this door does, in full (his line 2026-11-10: "Not your keys, manifesto and the proof of fact protocol needs to be in
// place for me and for an external user"):
//   1. It serves one text, the lens package. The same text to everyone. Its fingerprint is the sha256 of that text; the file
//      is worker/src/lens-package.txt in this public repository, so anyone can hash it and compare (don't trust, verify).
//   2. The reading is made by the user's own AI, in the user's own chat. Nothing from that chat comes back here. There is no
//      tool that sends material, quotes or readings to this door (removed 2026-11-10 after an outside security read: the
//      return was sent without asking; not your keys applies to the user's reasoning as much as to the owner's).
//   3. It counts. Per address: when it was made, when the package was loaded, payments. The caller's network address is kept
//      only as a salted hash, to bound how many addresses one caller can make per day. No model runs here. No material is read here.
//   4. Access is an address the user makes for themselves (no account). Payment, when on, is a Lightning invoice made by the
//      owner's own node through an invoice-only connection: this door can ask for money, it cannot spend any.
// Improving the lens happens elsewhere, on the owner's own material and reactions, never on a user's.
//
//   POST /mcp/address      the user makes an address; at most ADDRESSES_PER_DAY new ones per caller per day.
//   POST /mcp/k/<address>  the door: lens_about, lens_frame.
//   POST /mcp              shared: serves no package; says how to get an address.
//   GET  /mcp/status       alive: the fingerprint served, since when, counts, where the source is. No client detail.
//   GET  /mcp/ledger       owner only (Authorization: Bearer LEDGER_READ_TOKEN): per address, events.
import PACKAGE from './lens-package.txt';
import { makeInvoice, lookup } from './pay.js';

const PROTO = '2025-06-18';
const DOOR_VERSION = '0.3.0';
const PACKAGE_VERSION = 'v0';
const MAX_BODY = 120_000, MAX_BATCH = 4, MAX_READING = 40_000;
const PAGE = 'https://proofbridge.nl/mcp/';
const SOURCE = 'https://github.com/theden1974/proofbridge_website/tree/main/worker/src';
const ABOUT = {
  purpose: 'Position the UX lens for producing an app. If not guided, you are creating AI app slob.',
  what_it_is: 'A text: the UX lens of Dennis Jansen (proofbridge.nl), a set of structural moves with their tests, published field observations, and the form of a reading. Your AI loads it and reads your material with it, in your own chat.',
  what_leaves_your_chat: 'Nothing. This door has no tool that receives material, quotes or readings. It records that an address was made and when the lens was loaded.',
  bring: 'What is being built and for whom (screens, flow or description, as text). What has been checked with the people it is for. The decision at stake.',
  what_comes_back: 'A reading in your chat: cards first (an image from the field, the exact line from your material, the pattern in one sentence), then the full reading, ending with what it used and what it did not know. Where the lens does not know, it asks; it does not fill.',
  what_not: 'No answer is made on this side. No material is read on this side. No design, no code, no rating, no advice.',
  access: 'Each user makes their own address at ' + PAGE + ' (one click, no sign-in).',
  verify: 'The package fingerprint is the sha256 of the text served; the same file is public at ' + SOURCE + '/lens-package.txt. The door\'s code is in the same folder.',
  responsibility: 'Interpret at your own risk: interpretation is the responsibility of the one creating the network or app.',
  maturity: 'Version 0.1 of the lens, improved by use. Package ' + PACKAGE_VERSION + ', door ' + DOOR_VERSION + '.',
};

// What the user's AI is told when the connector is attached. Written so a person can read it too; the same facts are in /mcp/index.md and in the page's JSON-LD.
const INSTRUCTIONS = [
  'This connector serves the UX lens of Dennis Jansen (proofbridge.nl): a text your AI reads the builder\'s material with. ' + ABOUT.purpose,
  'Nothing from the chat is sent to this server. The only call a reading needs is lens_frame, which returns the lens text.',
  'When the builder asks to use the UX lens:',
  '1. The material is what the builder gives or points at, as text. Take from the chat what is being built and for whom, what has been checked with the people it is for, and the decision at stake; where the chat does not say, write "not stated". The reading does not open with questions to the builder; its questions are inside the reading.',
  '2. Call lens_frame. It returns the lens text with its version and fingerprint. If it returns payment_required, show the builder the invoice and the amount as given and wait for them; call again with the payment_hash once they say it is paid. Any other status: tell the builder its message in one sentence. A reading under the lens\'s name is made only with the lens text loaded.',
  '3. Read the lens text in full, then the material in one pass, and write the reading in the form the lens text specifies.',
  '4. For the rest of the chat, when the builder brings more material or a next step, give the short form first (the cards), then the step as asked. The builder ends this with "lens off". If the lens text is no longer in the conversation, load it again and say so.',
  ABOUT.responsibility,
].join('\n');

const TOOLS = [
  { name: 'lens_about', title: 'About the UX lens', description: 'What the UX lens is, what leaves the chat (nothing), what the door records, how to verify it. Free.', inputSchema: { type: 'object', properties: {}, additionalProperties: false } },
  { name: 'lens_frame', title: 'Load the UX lens', description: 'Returns the UX lens as text (moves, tests, published field observations, the form of a reading) with its version and fingerprint. Use it when the builder asks to use the UX lens, before writing about their material: a reading under the lens\'s name needs this text. Takes no material and sends none. May return payment_required with a Lightning invoice for the builder, or address_required.', inputSchema: { type: 'object', properties: { payment_hash: { type: 'string', description: 'After paying an invoice from a previous answer: its payment_hash.' } }, additionalProperties: false } }
];

async function sha256(s) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join(''); }
let FINGERPRINT = null;
const fingerprint = async () => FINGERPRINT || (FINGERPRINT = await sha256(PACKAGE));
const rpc = (id, result) => ({ jsonrpc: '2.0', id, result });
const rpcErr = (id, code, message) => ({ jsonrpc: '2.0', id, error: { code, message } });
const text = (t, isError = false) => ({ content: [{ type: 'text', text: typeof t === 'string' ? t : JSON.stringify(t, null, 1) }], isError });
// one line, printable, bounded: nothing from a caller reaches a mail header unchanged (audit gap 4)
const clean = (s, n) => String(s || '').replace(/[\u0000-\u001f\u007f-\u009f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, n);
const JSONH = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' };
const json = (status, obj, extra = {}) => new Response(JSON.stringify(obj), { status, headers: { ...JSONH, ...extra } });
const pageCors = (request, env) => { const o = request.headers.get('origin') || ''; const ok = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).includes(o); return ok ? { 'access-control-allow-origin': o, 'vary': 'Origin' } : {}; };

const LEDGER_DOWN = { status: 'not_available', message: 'The ledger behind this door did not answer. Nothing is wrong with your chat. Tell the builder in one sentence: try again in a minute.' };
const ADDRESS_REQUIRED = (bare) => ({ status: 'address_required', message: (bare ? 'This is the shared door; it serves no package. ' : 'This address is not known to the door. ') + 'Nothing is wrong with the connection. Tell the builder in one sentence: get an address at ' + PAGE + ' (one click, no sign-in) and add that address as the connector instead of this one. Then stop: do not review, audit or read the material yourself in the meantime; the request waits for the address.' });

export async function mcpDoor(request, env, mail, parts) {
  // parts: [] for /mcp, ['address'], ['k', key], ['status'], ['ledger'], ['ledger', id]
  const sub = parts[0] || '';
  if (sub === 'status') return statusDoor(request, env);
  if (sub === 'ledger') return ledgerDoor(request, env, parts[1]);
  if (sub === 'address') return addressDoor(request, env);
  if (sub && sub !== 'k') return json(404, { ok: false, error: 'path' });
  const key = sub === 'k' ? (parts[1] || '') : null;

  // MCP clients are servers, not browser pages: no allow-origin on the door (audit gap 11)
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: { 'access-control-allow-methods': 'POST, OPTIONS' } });
  if (request.method === 'GET') return json(405, { ok: false, error: 'method', hint: 'POST JSON-RPC (MCP Streamable HTTP). Status: GET /mcp/status.' });
  if (request.method !== 'POST') return json(405, { ok: false, error: 'method' });
  if (!(request.headers.get('content-type') || '').toLowerCase().startsWith('application/json')) return json(415, rpcErr(null, -32600, 'content-type: application/json'));
  if (Number(request.headers.get('content-length') || 0) > MAX_BODY) return json(413, rpcErr(null, -32600, 'size: body over ' + MAX_BODY + ' characters'));
  let body; try { const raw = await request.text(); if (raw.length > MAX_BODY) return json(413, rpcErr(null, -32600, 'size: body over ' + MAX_BODY + ' characters')); body = JSON.parse(raw); } catch { return json(400, rpcErr(null, -32700, 'parse error')); }
  const msgs = Array.isArray(body) ? body : [body];
  if (msgs.length > MAX_BATCH) return json(400, rpcErr(null, -32600, 'batch: at most ' + MAX_BATCH + ' messages per request'));

  const ledger = env.LEDGER ? env.LEDGER.getByName('ledger') : null;
  let addr = null;
  try { if (key !== null && ledger) addr = await ledger.address(key); } catch { return json(200, Array.isArray(body) ? msgs.map(x => rpc(x && x.id, text(LEDGER_DOWN))) : rpc(msgs[0] && msgs[0].id, text(LEDGER_DOWN))); }
  const out = [];
  try {

  for (const m of msgs) {
    if (!m || m.jsonrpc !== '2.0') { out.push(rpcErr(m && m.id, -32600, 'invalid request')); continue; }
    if (m.id === undefined) continue; // notification
    if (m.method === 'initialize') { out.push(rpc(m.id, { protocolVersion: PROTO, capabilities: { tools: { listChanged: false } }, serverInfo: { name: 'proofbridge-lens', version: DOOR_VERSION }, instructions: INSTRUCTIONS })); continue; }
    if (m.method === 'ping') { out.push(rpc(m.id, {})); continue; }
    if (m.method === 'tools/list') { out.push(rpc(m.id, { tools: TOOLS })); continue; }
    if (m.method !== 'tools/call') { out.push(rpcErr(m.id, -32601, 'method not found')); continue; }
    const name = m.params && m.params.name, args = (m.params && m.params.arguments) || {};
    if (name === 'lens_about') { out.push(rpc(m.id, text(ABOUT))); continue; }
    if (name !== 'lens_frame') { out.push(rpcErr(m.id, -32602, 'unknown tool')); if (ledger && addr) await ledger.event(key, 'error', 'unknown tool ' + clean(name, 40)); else if (ledger) await ledger.count('unknown_tool'); continue; }
    if (!ledger) { out.push(rpc(m.id, text({ status: 'not_available', message: 'The ledger behind this door is not bound. Nothing is wrong with your chat. Tell the builder in one sentence: the lens door is being set up; try later.' }))); continue; }
    if (key === null || !addr) { out.push(rpc(m.id, text(ADDRESS_REQUIRED(key === null)))); await ledger.count(key === null ? 'bare_door' : 'unknown_address'); continue; }
    if (addr.off) { out.push(rpc(m.id, text({ status: 'off', message: 'This address has been switched off by proofbridge. Tell the builder in one sentence; a new address can be minted at ' + PAGE + '.' }))); continue; }

    if (name === 'lens_frame') {
      if (env.LENS_FRAME_OPEN !== '1') { out.push(rpc(m.id, text({ status: 'not_released', message: 'Nothing is wrong with the connection. The package is released per version by proofbridge and the current version is not released. Tell the builder in one sentence; make no reading under the lens\'s name until it is.' }))); continue; }
      const t0 = Date.now();
      const FREE = Number(env.FREE_READINGS || 3), PRICE = Number(env.LENS_PRICE_SATS || 0);
      // payment proof first (audit: payment bound to the address, one use)
      if (args.payment_hash) {
        const ph = String(args.payment_hash).toLowerCase();
        if (!/^[0-9a-f]{64}$/.test(ph)) { out.push(rpc(m.id, text({ status: 'payment_proof', message: 'payment_hash is 64 hex characters, as given with the invoice.' }, true))); continue; }
        const inv = await ledger.invoiceFor(key, ph);
        if (!inv) { out.push(rpc(m.id, text({ status: 'payment_for_other_address', message: 'This invoice was not issued to this address.' }, true))); continue; }
        if (!inv.used) {
          try {
            const t = await lookup(env, ph);
            const settled = t.state === 'settled' || (t.state == null && Number(t.settled_at) > 0);
            if (!settled) { out.push(rpc(m.id, text({ status: 'not_paid_yet', payment_hash: ph, message: 'The invoice is not settled yet. Call again once the wallet shows it paid.' }))); continue; }
            if (Number(t.amount || 0) < inv.sats * 1000) { out.push(rpc(m.id, text({ status: 'underpaid', price_sats: inv.sats }, true))); continue; }
            await ledger.settle(key, ph, Math.round(Number(t.amount) / 1000), Number(env.CREDITS_PER_PAYMENT || 1));
          } catch (e) { await ledger.event(key, 'error', 'rail ' + clean(e.message, 80)); out.push(rpc(m.id, text({ status: 'payment_rail', message: 'The payment rail did not answer. Call again in a minute with the same payment_hash.' }, true))); continue; }
        }
      }
      const f = await ledger.frame(key, FREE, PACKAGE.length, Date.now() - t0);
      if (!f.ok && f.error === 'payment_required') {
        if (!PRICE) { out.push(rpc(m.id, text({ status: 'quota', message: 'The free readings of this address are used and payment is not open on this door. Tell the builder in one sentence.' }))); continue; }
        try {
          const pending = await ledger.pendingInvoice(key, 50 * 60_000);
          if (!pending && await ledger.invoicesSince(key, 3_600_000) >= 3) { out.push(rpc(m.id, text({ status: 'rate', message: 'Three invoices were issued to this address in the last hour; pay one of them, or call again later.' }, true))); continue; }
          const inv = pending ? { invoice: pending.bolt11, payment_hash: pending.payment_hash, expires_at: pending.expires_at } : await makeInvoice(env, PRICE, 'proofbridge lens reading ' + (await sha256('inv:' + key)).slice(0, 12));
          if (!pending) await ledger.invoice(key, inv.payment_hash, PRICE, inv.invoice, inv.expires_at || 0);
          out.push(rpc(m.id, text({ status: 'payment_required', price_sats: PRICE, invoice: inv.invoice, payment_hash: inv.payment_hash, expires_at: inv.expires_at ? new Date(inv.expires_at * 1000).toISOString() : null,
            message: 'The ' + FREE + ' free readings of this address are used. One reading costs ' + PRICE + ' sats. Show the builder the invoice text as given (a wallet reads it; a QR can be drawn from it). When paid, call lens_frame again with this payment_hash.' })));
        } catch (e) { await ledger.event(key, 'error', 'rail ' + clean(e.message, 80)); out.push(rpc(m.id, text({ status: 'payment_rail', message: 'The payment rail did not answer. Try again in a minute.' }, true))); }
        continue;
      }
      if (!f.ok) { out.push(rpc(m.id, text({ status: f.error }, true))); continue; }
      const fp = await fingerprint();
      out.push(rpc(m.id, text('purpose: ' + ABOUT.purpose + '\nwhat_leaves_your_chat: ' + ABOUT.what_leaves_your_chat + '\nverify: ' + ABOUT.verify + '\nresponsibility: ' + ABOUT.responsibility + '\npackage_version: ' + PACKAGE_VERSION + '\nfingerprint: ' + fp + '\nthis_reading: ' + (f.paid ? 'paid' : FREE >= 1000 ? 'free' : 'free, ' + f.free_left + ' free left on this address') + '\n\n' + PACKAGE)));
      continue;
    }

  }
  } catch (e) { return json(200, rpc(msgs[0] && msgs[0].id, text(LEDGER_DOWN))); }
  if (!out.length) return new Response(null, { status: 202, headers: JSONH });
  return json(200, Array.isArray(body) ? out : out[0]);
}

// the client mints its own address: no account, no owner's hand; bounded per caller per day
async function addressDoor(request, env) {
  const cors = pageCors(request, env);
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: { ...cors, 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'content-type' } });
  if (request.method !== 'POST') return json(405, { ok: false, error: 'method', how: 'POST {} here; the answer holds your address.' }, cors);
  if (!env.LEDGER) return json(503, { ok: false, error: 'not_available' }, cors);
  let client = ''; try { const raw = await request.text(); if (raw.length < 2000) client = clean((JSON.parse(raw || '{}') || {}).client, 80); } catch {}
  const ip = request.headers.get('cf-connecting-ip') || 'unknown';
  let r; try { r = await env.LEDGER.getByName('ledger').mint(ip, client, Number(env.ADDRESSES_PER_DAY || 3)); } catch { return json(503, { ok: false, error: 'not_available' }, cors); }
  if (!r.ok) return json(429, r, { ...cors, 'retry-after': '3600' });
  const base = new URL(request.url); base.pathname = '/mcp/k/' + r.key; base.search = '';
  return json(200, { ok: true, address: base.toString(), reused: !!r.reused, free_readings: Number(env.FREE_READINGS || 3), price_sats: Number(env.LENS_PRICE_SATS || 0),
    next: (r.reused ? 'This is the latest address made for you today. ' : '') + 'Add this address as a custom connector in your AI (no sign-in). In a chat with it on, say: use the UX lens. Keep the address.' }, cors);
}

// alive, like a node: what it serves, since when, what it has done. No client detail.
async function statusDoor(request, env) {
  const cors = pageCors(request, env);
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: { ...cors, 'access-control-allow-methods': 'GET, OPTIONS' } });
  const s = env.LEDGER ? await env.LEDGER.getByName('ledger').status() : null;
  return json(200, { alive: true, source: SOURCE, door: DOOR_VERSION, package: PACKAGE_VERSION, fingerprint: await fingerprint(), released: env.LENS_FRAME_OPEN === '1', free_readings: Number(env.FREE_READINGS || 3), price_sats: Number(env.LENS_PRICE_SATS || 0), now: new Date().toISOString(), ledger: s }, { ...cors, 'cache-control': 'no-store' });
}

// owner's view, read token only (set as a secret; without it this door does not exist)
async function ledgerDoor(request, env, id) {
  if (!env.LEDGER_READ_TOKEN) return json(404, { ok: false, error: 'not_configured' });
  const auth = request.headers.get('authorization') || '';
  if (auth !== 'Bearer ' + env.LEDGER_READ_TOKEN) return json(401, { ok: false, error: 'token' });
  const L = env.LEDGER.getByName('ledger');
  if (request.method === 'POST' && id) { // switch an address off or on: POST /mcp/ledger/<key> {"off":true}
    let off = true; try { off = !!(JSON.parse(await request.text()) || {}).off; } catch {}
    return json(200, { ok: true, address: await L.switchOff(id, off) });
  }
  if (id) { const r = await L.reading(id); return r ? json(200, r) : json(404, { ok: false, error: 'unknown' }); }
  return json(200, await L.ledger());
}
