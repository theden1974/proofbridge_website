// Temporary self-test of the invoice route (B38). Asks the NWC connection what it may do,
// makes one 1-sat invoice and looks it up. Never pays, never shows the secret. Remove after the test.
import { NWCClient } from '@getalby/sdk/nwc';

const J = (status, obj) => new Response(JSON.stringify(obj, null, 1), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'access-control-allow-origin': '*' } });
const withTimeout = (p, ms, label) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error(label + ': no answer within ' + ms / 1000 + ' s')), ms))]);

export async function nwcSelftest(request, env) {
  if (request.method !== 'GET') return J(405, { ok: false, error: 'method' });
  if (env.AGENT_LIMIT) { const { success } = await env.AGENT_LIMIT.limit({ key: 'selftest' }); if (!success) return J(429, { ok: false, error: 'rate', detail: 'wait a minute' }); }
  const out = { step1_secret_in_cloudflare: !!env.NWC_INVOICE_URL };
  if (!env.NWC_INVOICE_URL) return J(200, { ...out, verdict: 'NWC_INVOICE_URL is not set in the relay (Cloudflare, Variables and Secrets, type Secret).' });
  out.step1_looks_like_nwc = /^nostr\+walletconnect:\/\//.test(env.NWC_INVOICE_URL);
  let client;
  try {
    client = new NWCClient({ nostrWalletConnectUrl: env.NWC_INVOICE_URL });
    try {
      const info = await withTimeout(client.getInfo(), 20000, 'get_info');
      out.step2_methods_allowed = info.methods || [];
      out.step2_can_pay = (info.methods || []).some(m => /^pay_|multi_pay|pay_keysend/.test(m));
      out.step2_network = info.network || null;
    } catch (e) { out.step2_get_info_error = String(e.message || e).slice(0, 160); }
    const inv = await withTimeout(client.makeInvoice({ amount: 1000, description: 'proofbridge selftest, do not pay' }), 20000, 'make_invoice');
    out.step3_invoice_made = !!(inv && inv.invoice);
    out.step3_invoice_start = inv && inv.invoice ? inv.invoice.slice(0, 14) + '...' : null;
    const look = await withTimeout(client.lookupInvoice({ payment_hash: inv.payment_hash }), 20000, 'lookup_invoice');
    out.step4_lookup_ok = !!look;
    out.step4_state = look ? (look.state || (look.settled_at ? 'settled' : 'unsettled')) : null;
  } catch (e) {
    out.error = String(e.message || e).replace(env.NWC_INVOICE_URL, '***').slice(0, 200);
  } finally { try { client && client.close(); } catch {} }
  out.verdict = out.step3_invoice_made && out.step4_lookup_ok && out.step2_can_pay === false
    ? 'pass: invoices can be made and checked; the connection cannot pay'
    : out.step2_can_pay ? 'FAIL: the connection is allowed to pay. Remove pay permissions in Alby Hub.' : 'not passed yet: see the fields above';
  return J(200, out);
}
