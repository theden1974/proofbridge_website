// Payment rail for the agent door: one Lightning invoice per request, through the NWC connection
// on Dennis's Umbrel (make and look up invoices only; it cannot pay). Stores nothing: the invoice
// description carries the request_id and a hash of the request, so a payment is bound to that exact request.
import { NWCClient } from '@getalby/sdk/nwc';

const hex = buf => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
const stable = v => Array.isArray(v) ? '[' + v.map(stable).join(',') + ']'
  : (v && typeof v === 'object') ? '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + stable(v[k])).join(',') + '}'
  : JSON.stringify(v);
export async function requestHash(d) { return hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(stable(d)))).slice(0, 16); }
export const description = (d, h) => `proofbridge request ${d.request_id} ${h}`;
const timeout = (p, ms, what) => Promise.race([p, new Promise((_, r) => setTimeout(() => r(new Error(what + ': no answer within ' + ms / 1000 + ' s')), ms))]);

async function withClient(env, fn) {
  if (!env.NWC_INVOICE_URL) throw new Error('payment rail not configured');
  const c = new NWCClient({ nostrWalletConnectUrl: env.NWC_INVOICE_URL });
  try { return await fn(c); } finally { try { c.close(); } catch {} }
}
export async function makeInvoice(env, sats, desc) {
  return withClient(env, c => timeout(c.makeInvoice({ amount: sats * 1000, description: desc, expiry: 3600 }), 20000, 'make_invoice'));
}
export async function lookup(env, payment_hash) {
  return withClient(env, c => timeout(c.lookupInvoice({ payment_hash }), 20000, 'lookup_invoice'));
}
// proof from the agent: header X-Payment-Hash: <hash>, or Authorization: Lightning <hash>:<preimage>
export async function readProof(request) {
  const h = (request.headers.get('x-payment-hash') || '').trim().toLowerCase();
  const a = (request.headers.get('authorization') || '').match(/^Lightning\s+([0-9a-f]{64})(?::([0-9a-f]{64}))?$/i);
  const payment_hash = /^[0-9a-f]{64}$/.test(h) ? h : (a ? a[1].toLowerCase() : null);
  const preimage = a && a[2] ? a[2].toLowerCase() : null;
  if (payment_hash && preimage) {
    const calc = hex(await crypto.subtle.digest('SHA-256', Uint8Array.from(preimage.match(/../g).map(x => parseInt(x, 16)))));
    if (calc !== payment_hash) return { bad: 'preimage does not match payment hash' };
  }
  return { payment_hash, preimage };
}
