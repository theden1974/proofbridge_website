// /mcp: the lens as a seat in someone else's chat (his line 2026-11-06 10:28: "a seat equipped"). Streamable HTTP, JSON-RPC.
// Three tools. lens_about (free): what this is, what comes back, what not. lens_frame: the outside lens package (containers,
// twin tests, his own anchor sentences; no raw material, no transcripts, no names of others); served only when cleared.
// lens_return: the reading the seat made, sent back to Dennis's mailbox for his judgment (mine / not mine / missing).
// Nothing here runs a model. Nothing here reads the material: the seat reads it in its own chat with the frame.
import PACKAGE from './lens-package.txt';

const PROTO = '2025-06-18';
const ABOUT = {
  what: 'The lens of Dennis Jansen, UX researcher: a set of structural moves (containers), each with its formula, its twin tests and anchor sentences in his own words. The seat that loads it reads material with it, in its own chat.',
  what_comes_back: 'From lens_frame: the package as text, with its version and content hash. From Dennis, after lens_return: his judgment of the reading, by email, within 7 days in the test phase: which firings are his, which are not, what is missing.',
  what_not: 'No answer is generated on this side. No material is read on this side. No advice, no rating, no summary. The package does not contain raw material, transcripts or names of other persons. The answer is not resold and not used to train.',
  maturity: 'Level 0 in test: the frame goes to the seat, the judgment stays with Dennis. The package is version 0.',
  bring: 'Material as text. No personal data of third parties (students, patients, clients).',
  contract: 'https://proofbridge.nl/agents/index.md'
};
const TOOLS = [
  { name: 'lens_about', title: 'About the lens', description: 'What this seat is, what comes back, what does not. Free.', inputSchema: { type: 'object', properties: {}, additionalProperties: false } },
  { name: 'lens_frame', title: 'Load the lens', description: 'Returns the outside lens package (containers, twin tests, anchors in his words, output rules) as text with its version and content hash. Read it in full before reading any material with it.', inputSchema: { type: 'object', properties: {}, additionalProperties: false } },
  { name: 'lens_return', title: 'Return a reading', description: 'Send the reading the seat made with the frame back to Dennis for his judgment. Required: package_hash (from lens_frame), material_title, reading (the JSON or text of the reading), seat (the model that read), contact_email (where his judgment goes).',
    inputSchema: { type: 'object', required: ['package_hash', 'material_title', 'reading', 'seat', 'contact_email'],
      properties: { package_hash: { type: 'string' }, material_title: { type: 'string', maxLength: 200 }, reading: { type: 'string', maxLength: 40000 }, seat: { type: 'string', maxLength: 80 }, contact_email: { type: 'string', maxLength: 200 } }, additionalProperties: false } }
];
const EMAIL = /^[^\s@<>:;,"()\[\]\\]{1,64}@[a-z0-9.-]{1,190}\.[a-z]{2,24}$/i;

async function sha256(s) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join(''); }
const rpc = (id, result) => ({ jsonrpc: '2.0', id, result });
const rpcErr = (id, code, message) => ({ jsonrpc: '2.0', id, error: { code, message } });
const text = (t, isError = false) => ({ content: [{ type: 'text', text: typeof t === 'string' ? t : JSON.stringify(t, null, 1) }], isError });

export async function mcpDoor(request, env, mail) {
  const h = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'access-control-allow-origin': '*', 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'content-type, mcp-protocol-version, mcp-session-id, accept' };
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
  if (request.method === 'GET') return new Response(JSON.stringify({ ok: false, error: 'method', hint: 'POST JSON-RPC (MCP Streamable HTTP). No server-initiated stream here.' }), { status: 405, headers: h });
  if (request.method !== 'POST') return new Response(JSON.stringify({ ok: false, error: 'method' }), { status: 405, headers: h });
  let body; try { const raw = await request.text(); if (raw.length > 120_000) return new Response(JSON.stringify(rpcErr(null, -32600, 'size')), { status: 413, headers: h }); body = JSON.parse(raw); } catch { return new Response(JSON.stringify(rpcErr(null, -32700, 'parse error')), { status: 400, headers: h }); }
  const msgs = Array.isArray(body) ? body : [body];
  const out = [];
  for (const m of msgs) {
    if (!m || m.jsonrpc !== '2.0') { out.push(rpcErr(m && m.id, -32600, 'invalid request')); continue; }
    if (m.id === undefined) continue; // notification: nothing to answer
    if (m.method === 'initialize') { out.push(rpc(m.id, { protocolVersion: PROTO, capabilities: { tools: { listChanged: false } }, serverInfo: { name: 'proofbridge-lens', version: '0.1.0' }, instructions: 'Call lens_about first. lens_frame returns the package; read it in full before reading material. Send every reading back with lens_return.' })); continue; }
    if (m.method === 'ping') { out.push(rpc(m.id, {})); continue; }
    if (m.method === 'tools/list') { out.push(rpc(m.id, { tools: TOOLS })); continue; }
    if (m.method === 'tools/call') {
      const name = m.params && m.params.name, args = (m.params && m.params.arguments) || {};
      if (name === 'lens_about') { out.push(rpc(m.id, text(ABOUT))); continue; }
      if (name === 'lens_frame') {
        if (env.LENS_FRAME_OPEN !== '1') { out.push(rpc(m.id, text({ ok: false, error: 'not_cleared', detail: 'The package has not been cleared for release yet. lens_about and lens_return work.' }, true))); continue; }
        const hash = await sha256(PACKAGE);
        out.push(rpc(m.id, text('package_version: v0\npackage_hash: ' + hash + '\n\n' + PACKAGE))); continue;
      }
      if (name === 'lens_return') {
        const miss = TOOLS[2].inputSchema.required.filter(k => typeof args[k] !== 'string' || !args[k].trim());
        if (miss.length) { out.push(rpc(m.id, text({ ok: false, error: 'missing', fields: miss }, true))); continue; }
        if (!EMAIL.test(args.contact_email)) { out.push(rpc(m.id, text({ ok: false, error: 'contact_email' }, true))); continue; }
        if (args.reading.length > 40000) { out.push(rpc(m.id, text({ ok: false, error: 'size' }, true))); continue; }
        const current = env.LENS_FRAME_OPEN === '1' ? await sha256(PACKAGE) : null;
        const id = 'LENS-' + Math.random().toString(36).slice(2, 8).toUpperCase();
        const fail = await mail(env, { fromName: 'proofbridge lens return', replyTo: { email: args.contact_email },
          subject: 'PROOFBRIDGE ' + id + ' lens return from seat ' + args.seat.slice(0, 40),
          text: 'material: ' + args.material_title + '\nseat: ' + args.seat + '\npackage_hash: ' + args.package_hash + (current ? (current === args.package_hash ? ' (current v0)' : ' (NOT the current package)') : '') + '\ncontact: ' + args.contact_email + '\n\n' + args.reading });
        if (fail) { out.push(rpc(m.id, text({ ok: false, error: 'smtp', ...fail }, true))); continue; }
        out.push(rpc(m.id, text({ ok: true, return_id: id, next: 'Dennis reads it and answers by email to contact_email: which firings are his, which are not, what is missing.' }))); continue;
      }
      out.push(rpcErr(m.id, -32602, 'unknown tool')); continue;
    }
    out.push(rpcErr(m.id, -32601, 'method not found'));
  }
  if (!out.length) return new Response(null, { status: 202, headers: h });
  return new Response(JSON.stringify(Array.isArray(body) ? out : out[0]), { status: 200, headers: h });
}
