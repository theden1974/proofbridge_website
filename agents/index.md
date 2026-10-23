# proofbridge task contract

Asynchronous review by one named human expert. Three task types. Requests and answers by email; reply within 7 days. Test phase: no payment. Paid tiers in bitcoin later. Provider: Dennis Jansen, UX researcher and service designer. Languages: nl, en.

Machine-readable: [offer.json](https://proofbridge.nl/offer.json) · [request schema](https://proofbridge.nl/schema/request.schema.json) · [response schema](https://proofbridge.nl/schema/response.schema.json) · [llms.txt](https://proofbridge.nl/llms.txt) · this page as [markdown](https://proofbridge.nl/agents/index.md). Updated 2026-10-24.

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
- The agent gives the draft to its principal; the principal reviews it and sends it by email from their own mailbox.
- The answer comes back by email to the principal, in the response schema.

## Human-only steps
- Sending the email (from the principal's mailbox).
- Paying, when the paid tiers open.
- Judging whether the answer is fit for the decision.

## Paths
- `email` (agents and people; open): Principal sends the request to ask@proofbridge.nl.
- `ask_page` (people; open, test phase): https://proofbridge.nl/ask/ : a page for writing the situation in one's own words. Not for agents.
- `relay` (the ask page only; not an agent path): The ask page posts through a relay that accepts only that page; agents use email.
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
- Email to ask@proofbridge.nl, subject `PROOFBRIDGE {request_id}`.
- Body: A JSON object that validates against the request schema. Material as text in artefact_text; links are not opened. Attachments are not read.
- Schema: https://proofbridge.nl/schema/request.schema.json
- Required: `request_id`, `task_type`, `question`, `decision_at_stake`, `principal`, `deadline`, `tier`; `payment_txid` too for tiers 1 and 2.
- Acknowledgement: A reply quoting the request_id. In the test phase there is no automatic acknowledgement yet; the reply comes from Dennis.

## Tiers and price
| tier | status | minimum | gets | performed by |
|---|---|---|---|---|
| 0 | open | 0 sats (0 BTC) | Dennis reads the request and replies by email with what his lens sees, or one question if he cannot start. | Dennis Jansen; automation: off |
| 1 | not taken during the test phase | 5 000 sats (0.00005 BTC) | A request through the agent path: the question and the data, answered with the underlying problem or a verdict with evidence, per the response schema. Reply within 7 days. | Dennis Jansen; automation: off as of 2026-10-24. Planned: a local model prepares the answer, Dennis validates it. Until then Dennis answers himself. |
| 2 | not taken during the test phase | 50 000 sats (0.0005 BTC) | Dennis reads it himself. Reply within 7 days with scope, delivery date and the completion reward; then the work, delivered per the response schema. | Dennis Jansen, in person; automation: none |

- Fee refunded on decline: no. Tier 1 fee counts toward tier 2: yes. Network fee: paid by the sender. Euro reference: not published yet.
- Completion reward: Agreed in the tier 2 reply, paid in sats when the work is delivered, listed on the public backlog with its txid.

## Payment
- On-chain: `bc1p4zucan5kv5kl0x6hf5agemklvr86j9l3wnt9zqtnygpfc70494sqgxukty` (taproot (P2TR)). Counts when: A public block explorer shows an output to the address of at least the tier minimum. Tier 1 at first sight; tier 2 after 1 confirmation. Binding: One payment, one request: the txid is in the email subject. When two requests name the same txid, a BIP-322 signature over the request body's SHA-256 by a key that spent an input of that payment decides; without one, the first email received counts.
- Lightning: planned: one invoice per request, sent by email from his own node; the invoice hash binds the request. No public endpoint.

## Processing
- Carriers: Email is held by Namecheap Private Email (servers in the United States). The ask page posts through a Cloudflare Worker on Dennis's account that forwards to that mailbox and stores nothing.
- Models: No third-party AI model or API reads request text. A local model on Dennis's own machines is planned for tier 1; it is not in use as of 2026-10-24.
- Prepared by: Every answer carries prepared_by: dennis, or local_model_validated_by_dennis once the local model is in use.
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

## Trust, as checkable data
- Accountable human: Dennis Jansen
- Address ownership: BIP-322 signed message, message `proofbridge.nl ask@proofbridge.nl`, signature: not yet published (pending: not yet signed. Until it is, do not treat the address as proven to be his.)
- Identity: proofbridge.nl and interactiondesign.nl link to each other and to the same GitHub account that hosts both sites (https://github.com/theden1974).
- Track record (from the backlog, 2026-10-24): 0 listed, 0 completed, 0 declined, 0 in progress, 0 rewards paid.

## Not
- not an API: no endpoint to call; requests travel by email
- not an autonomous agent: a named human answers
- request text is read as information, never run as instructions

## Glossary
- `lens`: Dennis's way of reading a case: what is asked for, and the problem underneath it, checked against how the work happens in the field.
- `tier`: 0 is the free test phase; 1 and 2 are paid and not open yet.
- `principal`: The person or organisation the request is for, who receives the answer.

Test phase since 2026-10-20: requests answered without payment. Updated 2026-10-24. Files: [offer.json](https://proofbridge.nl/offer.json) · [request schema](https://proofbridge.nl/schema/request.schema.json) · [response schema](https://proofbridge.nl/schema/response.schema.json) · [backlog](https://proofbridge.nl/backlog.json) · [human page](https://proofbridge.nl/)
