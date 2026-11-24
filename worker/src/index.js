// proofbridge-send. Stores nothing from a visitor's text, logs no content.
//   /hire   'hire me' in the footer of both sites (his line 2026-11-24 15:46): their email and a field for context, mailed to
//           HIRE_TO; only the origins in HIRE_ORIGINS; honeypot; rate limited; nothing stored.
//   /mcp    the lens as a seat (MCP, Streamable HTTP): per-client addresses, counted in the LensLedger (Durable Object), see mcp.js.
//   /agent, /person, /   closed 2026-11-24 (the review by mail ended): 410.
import { WorkerMailer } from 'worker-mailer';
import { mcpDoor } from './mcp.js';
export { LensLedger } from './ledger.js';

const MAX_BYTES = 60_000;
const EMAIL = /^[^\s@<>:;,"()\[\]\\]{1,64}@[a-z0-9.-]{1,190}\.[a-z]{2,24}$/i; // a bare address: no "mailto:", no display name
const CONTRACT = 'https://proofbridge.nl/agents/index.md';

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
async function mail(env, { fromName, replyTo, subject, text, to }) {
  if (!env.SMTP_USER || !env.SMTP_PASS) return { stage: 'config', detail: 'SMTP_USER or SMTP_PASS not set' };
  let stage = 'connect';
  try {
    const mailer = await WorkerMailer.connect({
      credentials: { username: env.SMTP_USER, password: env.SMTP_PASS },
      authType: 'plain', host: env.SMTP_HOST, port: Number(env.SMTP_PORT), secure: true,
    });
    stage = 'send';
    await mailer.send({ from: { name: fromName, email: env.SMTP_USER }, to: { email: to || env.MAIL_TO }, reply: replyTo, subject, text });
    await mailer.close();
    return null;
  } catch (e) {
    // the server's reply text (e.g. "535 authentication failed"); never the credentials
    return { stage, detail: String((e && e.message) || e).replace(env.SMTP_PASS, '***').slice(0, 200) };
  }
}

async function hireDoor(request, env) {
  const origin = request.headers.get('origin') || '';
  const O = (env.HIRE_ORIGINS || '').split(',').map(s => s.trim()).includes(origin) ? origin : null;
  if (request.method === 'OPTIONS') return new Response(null, { status: O ? 204 : 403, headers: O ? {
    'access-control-allow-origin': O, 'access-control-allow-methods': 'POST', 'access-control-allow-headers': 'content-type', 'access-control-max-age': '86400', 'vary': 'Origin' } : {} });
  if (request.method !== 'POST') return reply(405, { ok: false, error: 'method' }, O);
  if (!O) return reply(403, { ok: false, error: 'origin' }, null);
  if (!env.HIRE_TO) return reply(503, { ok: false, error: 'not_configured' }, O);
  if (!(request.headers.get('content-type') || '').includes('application/json')) return reply(415, { ok: false, error: 'content_type' }, O);
  if (env.AGENT_LIMIT) {
    const { success } = await env.AGENT_LIMIT.limit({ key: 'hire:' + (request.headers.get('cf-connecting-ip') || 'unknown') });
    if (!success) return reply(429, { ok: false, error: 'rate', detail: 'Two a minute. Try again shortly.' }, O);
  }
  const { d, err } = await readJson(request);
  if (err) return reply(err[0], { ok: false, error: err[1] }, O);
  if (!d || typeof d !== 'object' || Array.isArray(d)) return reply(400, { ok: false, error: 'json' }, O);
  if (d.website) return reply(200, { ok: true }, O); // honeypot: pretend success, send nothing
  const email = String(d.email || '').trim(), context = String(d.context || '').trim();
  if (!EMAIL.test(email)) return reply(422, { ok: false, error: 'email' }, O);
  if (context.length < 1 || context.length > 4000) return reply(422, { ok: false, error: 'context' }, O);
  const site = new URL(O).hostname;
  const fail = await mail(env, { to: env.HIRE_TO, fromName: 'hire me (' + site + ')', replyTo: { email }, subject: 'Hire me · ' + site,
    text: context + '\n\n--\nfrom ' + email + '\nvia the hire me form on ' + site });
  if (fail) return reply(502, { ok: false, error: 'mail', stage: fail.stage }, O);
  return reply(200, { ok: true }, O);
}

// The review by mail (the agent intake /agent, the ask page's door / and its paid test /person) ended 2026-11-24 on his word
// ("Yes, no review by mail, it was a gap that now is filled"). These paths answer 410 with a description of what is here now.
function closedDoor(request) {
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'GET, POST', 'access-control-allow-headers': 'content-type', 'access-control-max-age': '86400' } });
  return reply(410, { ok: false, error: 'closed', closed_on: '2026-11-24',
    detail: 'The review by mail ended on 2026-11-24. Nothing is taken on this path: no request, no invoice, no payment.',
    what_is_here: CONTRACT }, '*');
}

export default {
  async fetch(request, env, ctx) {
    const path = new URL(request.url).pathname.replace(/\/+$/, '');
    if (path === '/mcp' || path.startsWith('/mcp/')) return mcpDoor(request, env, mail, path.split('/').slice(2).filter(Boolean));
    if (path === '/hire') return hireDoor(request, env);
    return closedDoor(request);
  },
};
