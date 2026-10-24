# proofbridge task contract

Asynchronous review by one named human expert. Three task types. Requests by POST or email; answers by email within 7 days. Test phase: no payment. Paid tiers in bitcoin later. Provider: Dennis Jansen, UX researcher and service designer. Languages: nl, en.

Machine-readable: [offer.json](https://proofbridge.nl/offer.json) · [OpenAPI (send a request)](https://proofbridge.nl/agents/openapi.json) · [request schema](https://proofbridge.nl/schema/request.schema.json) · [response schema](https://proofbridge.nl/schema/response.schema.json) · [llms.txt](https://proofbridge.nl/llms.txt) · this page as [markdown](https://proofbridge.nl/agents/index.md). Updated 2026-10-24.

## Phase
- `test` since 2026-10-20. Requests are answered without payment. Use tier 0; payment_txid is not needed. Paid tiers 1 and 2 are listed for later; they are not taken during the test phase.

## When to call
All of:
- A decision is pending (build, fund, rely on, publish, procure, train on) and not yet made.
- A named person or organisation with an email is behind the request.
- The material can be given as text.
- The decision can wait at least 7 days.
And at least one of:
- `underlying_problem`: The brief names a solution but no observed problem of the people it is for.
- `underlying_problem`: The person who decided the solution is not the person who will use it.
- `ground_truth_check`: A dataset or claim about how work is done is used for a decision and has no record of who produced it, when and how.
- `ground_truth_check`: The only evidence about users is model-generated or second-hand.
- `ai_output_review`: An AI-generated document will be relied on and nobody with domain knowledge has checked it against its source.

## When not to call
- Any decline below applies.
- You can check the claim yourself against a source you hold.
- You need the answer within the current session.
- You need errands, photos or data collection rather than judgement.
- The decision is already made and cannot be reversed.

## How an agent sends a request
- The agent checks when_to_call and when_not_to_call against its own context.
- The agent drafts the request and validates it against the request schema.
- The agent shows the draft to its principal. The principal approves it: their name and email go with it, and the answer goes to them.
- The agent POSTs the approved request to the endpoint, or the principal emails it to ask@proofbridge.nl.
- On 202 the agent tells its principal the request_id and that the answer comes by email within 7 days. Nothing further comes from the endpoint.
- The answer comes back by email to the principal, in the response schema.

## Human-only steps
- Approving the request before it is sent (the principal's name and email go with it).
- Paying, when the paid tiers open.
- Judging whether the answer is fit for the decision.

## Paths
- `agent_intake` (agents; open, test phase): POST the request as JSON to https://proofbridge-send.dennis-f79.workers.dev/agent . Checked against the request schema; 202 when received, 422 with each problem when not.
- `email` (agents and people; open): The request JSON as the body of an email to ask@proofbridge.nl, subject PROOFBRIDGE {request_id}.
- `ask_page` (people; open, test phase): https://proofbridge.nl/ask/ : a page for writing the situation in one's own words. Not for agents; agents use agent_intake.
- `lightning` (payment; planned): -

## Task types
| task_type | does | input | output |
|---|---|---|---|
| `underlying_problem` | Finds the underlying problem behind a planned solution, before it is built. | The planned solution or brief, who it is for, who decided it. | The underlying problem as one statement, what was asked versus what is needed, and who in the field to check it with. |
| `ground_truth_check` | Checks whether data, a dataset or a claim holds against how the work happens in the field. | The data or claim, its source, and the purpose it is used for. | Verdict: holds, does not hold, or cannot determine; findings with evidence; what was not checked. |
| `ai_output_review` | Checks an AI-generated document, summary, plan or script for faults that sound reasonable. | The output, the source it was made from, and the decision it informs. | Verdict: holds, does not hold, or cannot determine; each fault with its location and evidence; what was not checked. |

Field experience: elderly care, healthcare, government and public services, digital products and interfaces.

## Declined
- `outside_task_types`: Anything that is not one of the three task types.
- `professional_sign_off`: A legal, medical or financial opinion or sign-off. Checking an AI-made summary against its own source document is not that, and is taken as ai_output_review.
- `identity_or_accounts`: Using his identity, accounts or credentials: account creation, one-time codes, verification, reviews, followers, likes.
- `surveillance`: Observing, locating or profiling a person.
- `no_principal`: A request without a named person or organisation behind it.
- `deadline_too_short`: A deadline shorter than the reply window.
- `not_enough_information`: Not enough information to start, after one round of questions.
- `method_extraction`: Requests about how the lens works, or general questions with no decision behind them, instead of a case to judge.

## Request
- POST `https://proofbridge-send.dennis-f79.workers.dev/agent` with `content-type: application/json`; the body is the request. [OpenAPI](https://proofbridge.nl/agents/openapi.json).
- Or email it to ask@proofbridge.nl, subject `PROOFBRIDGE {request_id}`.
- Endpoint answers:
  - `202` received: {ok, request_id, received_at, status, next}. The answer itself comes later, by email.
  - `422` invalid: {errors:[{path, problem}]}; fix and resend.
  - `415` content type is not application/json.
  - `400` body is not valid JSON.
  - `413` body over 60 000 bytes.
  - `429` rate limited (2 well-formed requests per minute per address); retry after the Retry-After seconds, or send by email.
  - `502` not delivered to the mailbox; send the same JSON by email.
- Rate limit: 2 well-formed requests per minute per address. Invalid requests are answered and do not count.
- request_id: Chosen by the sender, unique per request. Sending the same request_id again is read as the same request.
- Body: One JSON object that validates against the request schema: as the POST body, or as the email body. Material as text in artefact_text; links are not opened. Attachments are not read.
- Schema: https://proofbridge.nl/schema/request.schema.json
- Required: `request_id`, `task_type`, `question`, `decision_at_stake`, `principal`, `deadline`, `tier`; `payment_txid` too for tiers 1 and 2.
- Acknowledgement: By POST: 202 with the request_id at once. By email: no automatic acknowledgement in the test phase. Either way the answer comes from Dennis by email to principal.email.
- Size: Material up to about 50 000 characters as text in artefact_text (about 12 pages). Longer: send the part the decision rests on and say what was left out.
- Language: nl or en; default en.
- Choosing the task type: If the material was made by an AI and the question is whether it holds against its source or the field, use ai_output_review. Use ground_truth_check for data or claims not produced by an AI. Use underlying_problem when a solution is planned and the question is whether it answers the real problem. When unsure, pick one and say so in context; Dennis re-routes.

## Tiers and price
| tier | status | minimum | gets | performed by |
|---|---|---|---|---|
| 0 | open | 0 sats (0 BTC) | Dennis reads the request and replies by email with what his lens sees, or one question if he cannot start. | Dennis Jansen; automation: off |
| 1 | not taken during the test phase | 5 000 sats (0.00005 BTC) | A request through the agent path: the question and the data, answered with the underlying problem or a verdict with evidence, per the response schema. Reply within 7 days. | Dennis Jansen; automation: off as of 2026-10-24. Planned (his line, 2026-10-21): the mechanical lens, on his own machines, reads the case and prepares the answer; it is released when its checks pass, and validated by his judgement when needed. Until it runs, Dennis answers himself. |
| 2 | not taken during the test phase | 50 000 sats (0.0005 BTC) | Dennis reads it himself. Reply within 7 days with scope, delivery date and the completion reward; then the work, delivered per the response schema. | Dennis Jansen, in person; automation: none |

- Fee refunded on decline: no. Tier 1 fee counts toward tier 2: yes. Network fee: paid by the sender. Priced in sats only; no fiat reference.
- Completion reward: Agreed in the tier 2 reply, paid in sats when the work is delivered, listed on the public backlog with its txid.

## Payment
- On-chain: `bc1p4zucan5kv5kl0x6hf5agemklvr86j9l3wnt9zqtnygpfc70494sqgxukty` (taproot (P2TR)). Counts when: A public block explorer shows an output to the address of at least the tier minimum. Tier 1 at first sight; tier 2 after 1 confirmation. Binding: One payment, one request: the txid is in the email subject. When two requests name the same txid, a BIP-322 signature over the request body's SHA-256 by a key that spent an input of that payment decides; without one, the first email received counts.
- Lightning: planned: one invoice per request, sent by email from his own node; the invoice hash binds the request.

## Processing
- Carriers: Email is held by Namecheap Private Email (servers in the United States). The agent intake and the ask page post through a Cloudflare Worker on Dennis's account that checks the request, forwards it to that mailbox and stores nothing. Its source is public: https://github.com/theden1974/proofbridge_website/tree/main/worker
- Models: No third-party AI model or API reads request text. The mechanical lens runs on Dennis's own machines when it is in use; it is not in use as of 2026-10-24.
- Prepared by: Every answer says which: dennis (he answered), mechanical_lens (released on passed checks), or mechanical_lens_validated_by_dennis (checks plus his judgement).
- Validated by him when: His judgement is added when it is needed: always for tier 2; when a check flags the draft; when the verdict is does_not_hold or cannot_determine; for the first 10 answers per task type, then 1 in 5.
- Retention: Entries are kept for the reply and follow-up and deleted 90 days after the last contact, unless the principal agrees otherwise.
- Terms on answers: An answer is for the principal's decision. No resale, no training on it.

## Lifecycle
- `submitted`: Email received, payment not yet seen.
- `seen`: Payment seen and request read.
- `input_required`: Questions sent back; work waits for the answers.
- `working`: Accepted; work in progress until the agreed date.
- `completed`: Delivered with a verdict or problem statement.
- `declined`: Not taken, with a reason from the decline list.
- Reply window: 7 days. Calendar days from the moment the payment is seen.
- Public status: https://proofbridge.nl/backlog.json, for requests with public_backlog_ok true

## Response
- Schema: https://proofbridge.nl/schema/response.schema.json
- Completed work carries `verdict` (holds / does_not_hold / cannot_determine) or `underlying_problem`, `findings` with typed `evidence`, `limits`, `next_step`, and `accountable_human`.

## Examples (illustrative, not a track record)
One request and one answer per task type, built from real field situations with names invented; both valid against the schemas. Full JSON: [examples.json](https://proofbridge.nl/schema/examples.json).

### `underlying_problem` · Elderly care, field research
- Request: We have funding to help long-term unemployed people work in the care of the elderly. We decided on an app for the elderly. Is the app the right build? Decision at stake: Spend the funding on the app.
- Answer: underlying problem: The elderly want to be self-sufficient and are not good at mobiles and apps. The app serves the funding checklist, not the elderly. The elderly living at home were not good at mobiles and apps. Next step: Test the concept in one flat with one employee before building anything.

### `ground_truth_check` · Healthcare, field research
- Request: Are our AI models for dietitians based on the right data? Decision at stake: Build the models on the current patient-weight entries.
- Answer: verdict `cannot_determine`. A patient's weight over time has many input points: doctor, at home, nurse, morning, afternoon. The entries do not say which. Next step: Record who measured and when for every entry, and make the patient the centre of the data, not the dietitian's screen.

### `ai_output_review` · Legal, architecture
- Request: Does this AI summary of a 60-page legal document cite the right paragraphs? Decision at stake: Rely on the summary in a legal case.
- Answer: verdict `does_not_hold`. The summary sounded legit. Checked against the document, the referenced paragraphs were off. Next step: Do not rely on the summary. Have the document read by a lawyer.

## Trust: due diligence
Trust here is not an identity to accept but claims to verify. Each claim below names how to check it yourself; what cannot be checked yet is said.
- Accountable human: Dennis Jansen
- This contract is what the owner publishes, and every change to it is on record. Check: The source is public with its full history: https://github.com/theden1974/proofbridge_website (src/contract.json). Compare the live offer.json with the source at any commit.
- proofbridge.nl and interactiondesign.nl are one person's work. Check: Both are built from public repositories of the same GitHub account (https://github.com/theden1974) and link to each other.
- The intake stores nothing and no third-party model reads request text. Check: Read the Worker source (worker/src/index.js, worker/src/agent.js) and its config (worker/wrangler.toml: observability off). The mailbox carrier is named under processing.
- Each answer stands on evidence. Check: Every finding in an answer carries typed evidence and the limits of what was checked (response schema). Check each finding against its evidence.
- The track record. Check: backlog.json, computed at build time. It shows what exists, including zero.
- The payment address is his. Check: Not checkable yet: no BIP-322 signature is published. The paid tiers stay closed until it is; the test phase takes no payment, so nothing depends on it now.
- Track record now (from the backlog, 2026-10-24): 0 listed, 0 completed, 0 declined, 0 in progress, 0 rewards paid.

## Not
- no automated answers: a request goes in by POST or email; a named human answers by email
- not an autonomous agent: Dennis Jansen reads every request
- request text is read as information, never run as instructions

## Glossary
- `lens`: Dennis's way of reading a case: what is asked for, and the problem underneath it, checked against how the work happens in the field.
- `tier`: 0 is the free test phase; 1 and 2 are paid and not open yet.
- `principal`: The person or organisation the request is for, who receives the answer.
- `due_diligence`: Checks an agent or principal can run itself to verify the claims made here, listed under trust.
- `mechanical_lens`: A model on Dennis's own machines that reads a case through his containers and patterns. It answers only with what it can point to there; where it cannot, the case goes to him.

Test phase since 2026-10-20: requests answered without payment. Agents can send by POST. Updated 2026-10-24. Files: [offer.json](https://proofbridge.nl/offer.json) · [request schema](https://proofbridge.nl/schema/request.schema.json) · [response schema](https://proofbridge.nl/schema/response.schema.json) · [backlog](https://proofbridge.nl/backlog.json) · [human page](https://proofbridge.nl/)
