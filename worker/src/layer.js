// The agent layer (/layer): a sealed knowledge package for agents. Pay first, then load. No free load, no refund.
// His lines, 2026-11-24: the agentic layer is paid and differs from the human lens in purpose and design; the step before
// paying must make clear to the agent that the service is what it is (don't trust, verify).
// The package and its due diligence are NOT in this repository. They sit in the KV namespace bound as AGENT_LAYER, in one value
// under the key 'sealed': {"due_diligence": {...}, "package": "<the package as one string>"}. The owner puts it there.
// This file holds only the commitments (version, sha256, bytes, date), so the public history shows what was committed to and when.
// Empty or mismatching sealed place = closed: no invoice is made and nothing is taken.
// Stateless: a settled payment hash opens the package for 24 hours (a retry after a broken connection costs nothing more).
import { makeInvoice, lookup, readProof } from './pay.js';

const COMMITMENTS = [
  { version: 'agent-v0.2', sha256: '9e3dc5a0fa31c827d9a8edb2018621b836593b3e94385802bb61591a1521126c', bytes: 43843, committed: '2026-11-24', form: 'one JSON document on one line, ASCII' },
];
const CURRENT = COMMITMENTS[COMMITMENTS.length - 1];
const DESC = 'proofbridge agent layer ' + CURRENT.version + ' ' + CURRENT.sha256.slice(0, 16);
const WINDOW_S = 24 * 3600;
const hex = buf => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
const sha256 = async s => hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)));
const CORS = { 'access-control-allow-origin': '*', 'access-control-expose-headers': 'x-payment-hash, x-package-sha256, x-package-version, x-receipt' };
const json = (status, obj, extra = {}) => new Response(JSON.stringify(obj, null, 1), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...CORS, ...extra } });

async function sealed(env) {
  const price = Number(env.LAYER_PRICE_SATS || 0);
  if (!(price > 0)) return { open: false, why: 'no fee is set; there is no free load' };
  if (!env.AGENT_LAYER) return { open: false, why: 'no sealed place is bound to this door' };
  let raw; try { raw = await env.AGENT_LAYER.get('sealed'); } catch { return { open: false, why: 'the sealed place did not answer' }; }
  if (!raw) return { open: false, why: 'the sealed place is empty' };
  let v; try { v = JSON.parse(raw); } catch { return { open: false, why: 'what is in the sealed place cannot be read' }; }
  if (typeof v.package !== 'string' || !v.due_diligence) return { open: false, why: 'the sealed place holds no package or no due diligence' };
  if (await sha256(v.package) !== CURRENT.sha256) return { open: false, why: 'what is in the sealed place does not match the commitment' };
  return { open: true, price, body: v.package, dd: v.due_diligence };
}

export async function layerDoor(request, env, parts) {
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: { ...CORS, 'access-control-allow-methods': 'GET', 'access-control-allow-headers': 'x-payment-hash, authorization', 'access-control-max-age': '86400' } });
  if (request.method !== 'GET') return json(405, { ok: false, error: 'method', allowed: ['GET'] }, { allow: 'GET, OPTIONS' });
  const s = await sealed(env);
  const price = s.price || Number(env.LAYER_PRICE_SATS || 0) || null;
  if (!parts.length) return json(200, {
    kind: 'proofbridge.agent_layer', open: s.open, ...(s.open ? {} : { closed_because: s.why }),
    what: 'A sealed knowledge package for agents: patterns with their sequences and tests, field cases, and the form of a reading, as data. Human field knowledge, not theory; a reflection of the real world through one person\'s lens.',
    commitment: CURRENT, earlier_commitments: COMMITMENTS.slice(0, -1),
    terms: { price_sats: price, unit: 'one settled payment opens the package for 24 hours', rail: 'Lightning; the invoice comes from the owner\'s own node through a connection that can only make and look up invoices', refund: 'none', free_load: 'none', free: 'this answer, with the due diligence when the door is open' },
    how_it_goes: [
      'GET /layer : this answer. Free.',
      'GET /layer/package without proof: 402 with a Lightning invoice and its payment_hash. Nothing is made when the door is closed.',
      'GET /layer/package with header X-Payment-Hash: <payment_hash> after the invoice is settled: the package as sent bytes, with headers x-package-sha256, x-package-version and x-receipt.',
      'The SHA-256 of the bytes received equals commitment.sha256; the commitment is in the public source history of this file.' ],
    source: 'https://github.com/theden1974/proofbridge_website/tree/main/worker/src/layer.js',
    ...(s.open ? { due_diligence: s.dd } : {}),
  });
  if (parts[0] !== 'package' || parts.length > 1) return json(404, { ok: false, error: 'not_found' });
  if (!s.open) return json(503, { ok: false, error: 'closed', detail: s.why + '. No invoice is made and nothing is taken.' });
  const proof = await readProof(request);
  if (proof.bad) return json(400, { ok: false, error: 'payment_proof', detail: proof.bad });
  try {
    if (!proof.payment_hash) {
      if (env.AGENT_LIMIT) {
        const { success } = await env.AGENT_LIMIT.limit({ key: 'layer:' + (request.headers.get('cf-connecting-ip') || 'unknown') });
        if (!success) return json(429, { ok: false, error: 'rate', detail: 'At most 2 invoices per minute per address.' }, { 'retry-after': '60' });
      }
      const inv = await makeInvoice(env, s.price, DESC);
      return json(402, { ok: false, error: 'payment_required', price_sats: s.price, invoice: inv.invoice, payment_hash: inv.payment_hash,
        expires_at: inv.expires_at ? new Date(inv.expires_at * 1000).toISOString() : null, bound_to: DESC,
        then: 'Once the invoice is settled, the same GET with header X-Payment-Hash: ' + inv.payment_hash + ' returns the package. No refund.' }, { 'x-payment-hash': inv.payment_hash });
    }
    const t = await lookup(env, proof.payment_hash);
    if ((t.description || '') !== DESC) return json(409, { ok: false, error: 'payment_for_something_else', detail: 'This payment is not bound to ' + DESC + '.' });
    const settled = t.state === 'settled' || (t.state == null && Number(t.settled_at) > 0);
    if (!settled) return json(402, { ok: false, error: 'not_paid_yet', payment_hash: proof.payment_hash, state: t.state || 'pending', invoice: t.invoice });
    if (Number(t.amount || 0) < s.price * 1000) return json(402, { ok: false, error: 'underpaid', price_sats: s.price });
    const at = Number(t.settled_at) || 0, now = Math.floor(Date.now() / 1000);
    if (at && now - at > WINDOW_S) return json(410, { ok: false, error: 'receipt_expired', detail: 'A settled payment opens the package for 24 hours; this one was settled ' + new Date(at * 1000).toISOString() + '.' });
    const receipt = { payment_hash: proof.payment_hash, sats: Math.round(Number(t.amount) / 1000), settled_at: at ? new Date(at * 1000).toISOString() : null,
      valid_until: at ? new Date((at + WINDOW_S) * 1000).toISOString() : null, version: CURRENT.version, sha256: CURRENT.sha256 };
    return new Response(s.body, { status: 200, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...CORS,
      'x-package-sha256': CURRENT.sha256, 'x-package-version': CURRENT.version, 'x-receipt': JSON.stringify(receipt) } });
  } catch (e) {
    return json(503, { ok: false, error: 'payment_rail', detail: String(e.message || e).slice(0, 120) });
  }
}
