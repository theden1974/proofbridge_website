// proofbridge-send: two doors to one mailbox (ask@proofbridge.nl). Stores nothing, logs no content.
//   /       the /ask/ page for people: only the proofbridge.nl origin, plain text, honeypot.
//   /agent  agents: any origin, one JSON request per the request schema, checked before it is mailed.
// The answer to either is never automatic: Dennis replies by email.
import { WorkerMailer } from 'worker-mailer';
import { checkRequest, mailText } from './agent.js';
import { requestHash, description, makeInvoice, lookup, readProof } from './pay.js';

const MAX_BYTES = 60_000;
const ID = /^REQ-[A-Z0-9-]{4,24}$/;
const EMAIL = /^[^\s@<>:;,"()\[\]\\]{1,64}@[a-z0-9.-]{1,190}\.[a-z]{2,24}$/i; // a bare address: no "mailto:", no display name
const CONTRACT = 'https://proofbridge.nl/agents/index.md';
const SCHEMA = 'https://proofbridge.nl/schema/request.schema.json';

function cors(origin, env) {
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim());
  return allowed.includes(origin) ? origin : null;
}
function reply(status, obj, origin, extra = {}) {
  const h = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra };
  if (origin) { h['access-control-allow-origin'] = origin; if (origin !== '*') h['vary'] = 'Origin'; }
  return new Response(JSON.stringify(obj), { status, headers: h });
}
async function readJson(request) {
  const len = Number(request.headers.get('content-length') || 0);
  if (len > MAX_BYTES) return { err: [413, 'size'] };
  const raw = await request.text();
  if (raw.length > MAX_BYTES) return { err: [413, 'size'] };
  try { return { d: JSON.parse(raw) }; } catch { return { err: [400, 'json'] }; }
}
async function mail(env, { fromName, replyTo, subject, text }) {
  if (!env.SMTP_USER || !env.SMTP_PASS) return { stage: 'config', detail: 'SMTP_USER or SMTP_PASS not set' };
  let stage = 'connect';
  try {
    const mailer = await WorkerMailer.connect({
      credentials: { username: env.SMTP_USER, password: env.SMTP_PASS },
      authType: 'plain', host: env.SMTP_HOST, port: Number(env.SMTP_PORT), secure: true,
    });
    stage = 'send';
    await mailer.send({ from: { name: fromName, email: env.SMTP_USER }, to: { email: env.MAIL_TO }, reply: replyTo, subject, text });
    await mailer.close();
    return null;
  } catch (e) {
    // the server's reply text (e.g. "535 authentication failed"); never the credentials
    return { stage, detail: String((e && e.message) || e).replace(env.SMTP_PASS, '***').slice(0, 200) };
  }
}

async function agentDoor(request, env) {
  const O = '*';
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: {
    'access-control-allow-origin': O, 'access-control-allow-methods': 'GET, POST', 'access-control-allow-headers': 'content-type, x-payment-hash, authorization', 'access-control-expose-headers': 'x-payment-hash', 'access-control-max-age': '86400' } });
  const PRICE = Number(env.AGENT_PRICE_SATS || 0);
  if (request.method === 'GET') return reply(200, {
    what: 'proofbridge agent intake: POST one request (JSON) here. A named human answers by email to principal.email within 7 days; nothing is answered automatically.',
    method: 'POST', content_type: 'application/json', schema: SCHEMA, contract: CONTRACT,
    price_sats: PRICE, payment: PRICE ? 'Lightning. POST the request: the answer is 402 with an invoice. Pay it, then POST the same request again with header X-Payment-Hash: <payment_hash> (or Authorization: Lightning <payment_hash>:<preimage>). Paid and identical: 202.' : 'none',
  }, O);
  if (request.method !== 'POST') return reply(405, { ok: false, error: 'method', allowed: ['GET', 'POST'] }, O, { allow: 'GET, POST, OPTIONS' });
  if (!(request.headers.get('content-type') || '').toLowerCase().startsWith('application/json'))
    return reply(415, { ok: false, error: 'content_type', expected: 'application/json' }, O);
  const { d, err } = await readJson(request);
  if (err) return reply(err[0], { ok: false, error: err[1], detail: err[1] === 'size' ? 'body over 60 000 bytes; artefact_text is at most 50 000 characters' : 'body is not valid JSON' }, O);
  const errors = checkRequest(d);
  if (errors.length) return reply(422, { ok: false, error: 'invalid', errors, schema: SCHEMA }, O);
  // only well-formed requests count toward the limit, so an agent can fix and resend
  if (env.AGENT_LIMIT) {
    const key = request.headers.get('cf-connecting-ip') || 'unknown';
    const { success } = await env.AGENT_LIMIT.limit({ key });
    if (!success) return reply(429, { ok: false, error: 'rate', detail: 'Too many requests from this address. Wait a minute, or send by email to ask@proofbridge.nl.' }, O, { 'retry-after': '60' });
  }
  let paid = null;
  if (PRICE > 0) {
    const h = await requestHash(d), desc = description(d, h);
    const proof = await readProof(request);
    if (proof.bad) return reply(400, { ok: false, error: 'payment_proof', detail: proof.bad }, O);
    try {
      if (!proof.payment_hash) {
        const inv = await makeInvoice(env, PRICE, desc);
        return reply(402, { ok: false, error: 'payment_required', price_sats: PRICE, invoice: inv.invoice, payment_hash: inv.payment_hash,
          expires_at: inv.expires_at ? new Date(inv.expires_at * 1000).toISOString() : null, bound_to: desc,
          next: 'Pay the invoice, then POST this same request again (unchanged) with header X-Payment-Hash: ' + inv.payment_hash + '. A changed request needs a new invoice.' }, O, { 'x-payment-hash': inv.payment_hash });
      }
      const t = await lookup(env, proof.payment_hash);
      if ((t.description || '') !== desc) return reply(409, { ok: false, error: 'payment_for_other_request', detail: 'This payment is bound to another request or to a changed version of it. POST without a payment hash to get a new invoice.' }, O);
      const settled = t.state === 'settled' || (t.state == null && Number(t.settled_at) > 0);  // never the preimage: the receiver knows it before payment
      if (!settled) return reply(402, { ok: false, error: 'not_paid_yet', payment_hash: proof.payment_hash, state: t.state || 'pending', invoice: t.invoice }, O);
      if (Number(t.amount || 0) < PRICE * 1000) return reply(402, { ok: false, error: 'underpaid', price_sats: PRICE }, O);
      paid = { sats: Math.round(Number(t.amount) / 1000), payment_hash: proof.payment_hash, settled_at: t.settled_at ? new Date(t.settled_at * 1000).toISOString() : null };
    } catch (e) {
      return reply(503, { ok: false, error: 'payment_rail', detail: String(e.message || e).slice(0, 120), detail_for_agent: 'The payment rail did not answer. Try again in a minute, or send the JSON by email to ask@proofbridge.nl.' }, O);
    }
  }
  const received_at = new Date().toISOString();
  const fail = await mail(env, {
    fromName: 'proofbridge agent intake', replyTo: { email: d.principal.email, name: d.principal.name },
    subject: 'PROOFBRIDGE ' + d.request_id + (paid ? ' (paid ' + paid.sats + ' sats)' : ''), text: mailText(d, { received_at, paid }),
  });
  if (fail) return reply(502, { ok: false, error: 'smtp', ...fail, detail_for_agent: 'Not delivered. Send the same JSON by email to ask@proofbridge.nl, subject PROOFBRIDGE ' + d.request_id + '.' }, O);
  return reply(202, {
    ok: true, request_id: d.request_id, received_at, status: 'received', paid,
    next: 'Dennis reads it and replies by email to ' + d.principal.email + ' within 7 days: an answer per the response schema, or one question if he cannot start. Nothing further comes from this endpoint.',
  }, O);
}

async function askDoor(request, env) {
  const origin = cors(request.headers.get('origin') || '', env);
  if (request.method === 'OPTIONS') {
    if (!origin) return new Response(null, { status: 403 });
    return new Response(null, { status: 204, headers: {
      'access-control-allow-origin': origin, 'access-control-allow-methods': 'POST',
      'access-control-allow-headers': 'content-type', 'access-control-max-age': '86400', 'vary': 'Origin' } });
  }
  if (request.method !== 'POST') return reply(405, { ok: false, error: 'method', agents: 'POST /agent' }, origin);
  if (!origin) return reply(403, { ok: false, error: 'origin', agents: 'this door is for the ask page; agents POST to /agent' }, null);
  const { d, err } = await readJson(request);
  if (err) return reply(err[0], { ok: false, error: err[1] }, origin);
  if (d.website) return reply(200, { ok: true, request_id: d.request_id || '' }, origin); // honeypot: pretend success, send nothing
  if (!ID.test(d.request_id || '')) return reply(400, { ok: false, error: 'request_id' }, origin);
  const body = String(d.body || '').trim();
  if (body.split(/\s+/).length < 10) return reply(400, { ok: false, error: 'body' }, origin);
  const from = String(d.email || '').trim();
  const replyTo = EMAIL.test(from) ? { email: from } : undefined;
  const fail = await mail(env, { fromName: 'proofbridge ask', replyTo, subject: 'PROOFBRIDGE ' + d.request_id,
    text: body + (replyTo ? '' : '\n\n(no valid reply address given)') });
  if (fail) return reply(fail.stage === 'config' ? 500 : 502, { ok: false, error: 'smtp', ...fail }, origin);
  return reply(200, { ok: true, request_id: d.request_id }, origin);
}

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname.replace(/\/+$/, '');
    return path === '/agent' ? agentDoor(request, env) : askDoor(request, env);
  },
};
