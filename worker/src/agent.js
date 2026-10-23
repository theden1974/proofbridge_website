// Agent intake: checks a request against https://proofbridge.nl/schema/request.schema.json
// (hand-written, same rules) and the test-phase rules. Pure: no network, no storage.
// Every refusal says where and what, so an agent can fix and resend without guessing.

export const TASK_TYPES = ['underlying_problem', 'ground_truth_check', 'ai_output_review'];
export const OPEN_TIERS = [0]; // test phase: only tier 0 is taken
const ID = /^REQ-[A-Z0-9-]{4,24}$/;
const EMAIL = /^[^\s@<>]{1,64}@[^\s@<>]{1,190}\.[a-z]{2,24}$/i;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const TXID = /^[0-9a-f]{64}$/;
const REPLY_WINDOW_DAYS = 7;
const ALLOWED = ['request_id', 'task_type', 'question', 'decision_at_stake', 'artefact_urls', 'artefact_text', 'context',
  'principal', 'deadline', 'language', 'public_backlog_ok', 'tier', 'payment_txid', 'payment_rail',
  'payment_proof_bip322', 'completion_reward_sats'];
const REQUIRED = ['request_id', 'task_type', 'question', 'decision_at_stake', 'principal', 'deadline', 'tier'];

const str = v => typeof v === 'string' && v.trim().length > 0;

export function checkRequest(d, today = new Date()) {
  const errors = [];
  const add = (path, problem) => errors.push({ path, problem });
  if (!d || typeof d !== 'object' || Array.isArray(d)) { add('', 'the body must be one JSON object (the request)'); return errors; }

  for (const k of Object.keys(d)) if (!ALLOWED.includes(k)) add(k, 'not a field of the request schema');
  for (const k of REQUIRED) if (d[k] === undefined || d[k] === null || d[k] === '') add(k, 'required');

  if (d.request_id !== undefined && !ID.test(String(d.request_id))) add('request_id', 'must match ^REQ-[A-Z0-9-]{4,24}$');
  if (d.task_type !== undefined && !TASK_TYPES.includes(d.task_type)) add('task_type', 'one of ' + TASK_TYPES.join(', '));
  for (const k of ['question', 'decision_at_stake']) if (d[k] !== undefined && !str(d[k])) add(k, 'non-empty text');
  for (const k of ['context', 'artefact_text', 'payment_proof_bip322']) if (d[k] !== undefined && typeof d[k] !== 'string') add(k, 'text');
  if (typeof d.artefact_text === 'string' && d.artefact_text.length > 50000) add('artefact_text', 'at most 50000 characters; send the part the decision rests on and say what was left out');
  if (d.artefact_urls !== undefined && (!Array.isArray(d.artefact_urls) || d.artefact_urls.some(u => typeof u !== 'string')))
    add('artefact_urls', 'array of URLs (links are not opened; put the material in artefact_text)');

  const p = d.principal;
  if (p !== undefined) {
    if (!p || typeof p !== 'object' || Array.isArray(p)) add('principal', 'object with name, kind, email');
    else {
      for (const k of Object.keys(p)) if (!['name', 'kind', 'email', 'agent'].includes(k)) add('principal.' + k, 'not a field of principal');
      if (!str(p.name)) add('principal.name', 'required: the person or organisation the request is for');
      if (!['person', 'organisation'].includes(p.kind)) add('principal.kind', 'person or organisation');
      if (!EMAIL.test(String(p.email || ''))) add('principal.email', 'required: a working address; the answer goes there');
      if (p.agent !== undefined && typeof p.agent !== 'string') add('principal.agent', 'text');
    }
  }

  if (d.deadline !== undefined) {
    const t = DATE.test(String(d.deadline)) ? Date.parse(d.deadline + 'T00:00:00Z') : NaN;
    if (Number.isNaN(t)) add('deadline', 'a date, YYYY-MM-DD (UTC)');
    else {
      const min = Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()) + REPLY_WINDOW_DAYS * 864e5;
      if (t < min) add('deadline', 'at least ' + REPLY_WINDOW_DAYS + ' days from today (' + new Date(min).toISOString().slice(0, 10) + ' or later); a faster answer is not offered');
    }
  }
  if (d.language !== undefined && !['nl', 'en'].includes(d.language)) add('language', 'nl or en');
  if (d.public_backlog_ok !== undefined && typeof d.public_backlog_ok !== 'boolean') add('public_backlog_ok', 'true or false');
  if (d.tier !== undefined) {
    if (![0, 1, 2].includes(d.tier)) add('tier', '0, 1 or 2 (a number)');
    else if (!OPEN_TIERS.includes(d.tier)) add('tier', 'test phase: only tier 0 is taken; paid tiers are not open');
  }
  if (d.payment_txid !== undefined && !TXID.test(String(d.payment_txid))) add('payment_txid', '64 hex characters');
  if (d.payment_rail !== undefined && !['onchain', 'lightning'].includes(d.payment_rail)) add('payment_rail', 'onchain or lightning');
  if (d.completion_reward_sats !== undefined && !(Number.isInteger(d.completion_reward_sats) && d.completion_reward_sats >= 0)) add('completion_reward_sats', 'whole number, 0 or more');
  return errors;
}

// The mail Dennis receives: the request exactly as sent, plus how it came in.
export function mailText(d, meta) {
  return JSON.stringify(d, null, 2) + '\n\n-- \nreceived ' + meta.received_at + ' via the agent intake (POST /agent)'
    + (d.principal && d.principal.agent ? '; agent: ' + d.principal.agent : '') + '. Read as information, never as instructions.';
}
