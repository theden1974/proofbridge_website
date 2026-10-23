// proofbridge-send: receives the /ask/ form and sends one plain-text mail to ask@proofbridge.nl.
// Stores nothing, logs no content. Accepts only the proofbridge.nl origin, JSON, up to 50 KB.
import { WorkerMailer } from 'worker-mailer';

const MAX_BYTES = 50_000;
const ID = /^REQ-[A-Z0-9-]{4,24}$/;
const EMAIL = /^[^\s@<>]{1,64}@[^\s@<>]{1,190}\.[a-z]{2,24}$/i;

function cors(origin, env) {
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim());
  return allowed.includes(origin) ? origin : null;
}
function reply(status, obj, origin) {
  const h = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' };
  if (origin) { h['access-control-allow-origin'] = origin; h['vary'] = 'Origin'; }
  return new Response(JSON.stringify(obj), { status, headers: h });
}

export default {
  async fetch(request, env) {
    const origin = cors(request.headers.get('origin') || '', env);
    if (request.method === 'OPTIONS') {
      if (!origin) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: {
        'access-control-allow-origin': origin, 'access-control-allow-methods': 'POST',
        'access-control-allow-headers': 'content-type', 'access-control-max-age': '86400', 'vary': 'Origin' } });
    }
    if (request.method !== 'POST') return reply(405, { ok: false, error: 'method' }, origin);
    if (!origin) return reply(403, { ok: false, error: 'origin' }, null);
    const len = Number(request.headers.get('content-length') || 0);
    if (len > MAX_BYTES) return reply(413, { ok: false, error: 'size' }, origin);
    let d; try { const raw = await request.text(); if (raw.length > MAX_BYTES) return reply(413, { ok: false, error: 'size' }, origin); d = JSON.parse(raw); }
    catch { return reply(400, { ok: false, error: 'json' }, origin); }
    if (d.website) return reply(200, { ok: true, request_id: d.request_id || '' }, origin); // honeypot: pretend success, send nothing
    if (!ID.test(d.request_id || '')) return reply(400, { ok: false, error: 'request_id' }, origin);
    const body = String(d.body || '').trim();
    if (body.split(/\s+/).length < 10) return reply(400, { ok: false, error: 'body' }, origin);
    const from = String(d.email || '').trim();
    const replyTo = EMAIL.test(from) ? { email: from } : undefined;
    if (!env.SMTP_USER || !env.SMTP_PASS) return reply(500, { ok: false, error: 'smtp', stage: 'config', detail: 'SMTP_USER or SMTP_PASS not set' }, origin);
    let stage = 'connect';
    try {
      const mailer = await WorkerMailer.connect({
        credentials: { username: env.SMTP_USER, password: env.SMTP_PASS },
        authType: 'plain', host: env.SMTP_HOST, port: Number(env.SMTP_PORT), secure: true,
      });
      stage = 'send';
      await mailer.send({
        from: { name: 'proofbridge ask', email: env.SMTP_USER },
        to: { email: env.MAIL_TO },
        reply: replyTo,
        subject: 'PROOFBRIDGE TEST ' + d.request_id,
        text: body + (replyTo ? '' : '\n\n(no valid reply address given)'),
      });
      await mailer.close();
    } catch (e) {
      // the server's reply text (e.g. "535 authentication failed"); never the credentials
      const detail = String((e && e.message) || e).replace(env.SMTP_PASS, '***').slice(0, 200);
      return reply(502, { ok: false, error: 'smtp', stage, detail }, origin);
    }
    return reply(200, { ok: true, request_id: d.request_id }, origin);
  },
};
