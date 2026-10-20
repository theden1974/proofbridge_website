# proofbridge task contract

Paid, asynchronous review by one named human expert. Three task types. Requests by email with a bitcoin payment; answers by email in days. Provider: Dennis Jansen, UX researcher and service designer. Languages: nl, en.

## Task types
| task_type | does | input | output |
|---|---|---|---|
| `underlying_problem` | Finds the underlying problem behind a planned solution, before it is built. | The planned solution or brief, who it is for, who decided it. | The underlying problem as one statement, what was asked versus what is needed, and who in the field to check it with. |
| `ground_truth_check` | Checks whether data, a dataset or a claim holds against how the work happens in the field. | The data or claim, its source, and the purpose it is used for. | Verdict: holds, does not hold, or cannot determine; findings with evidence; what was not checked. |
| `ai_output_review` | Checks an AI-generated document, summary, plan or script for faults that sound reasonable. | The output, the source it was made from, and the decision it informs. | Verdict: holds, does not hold, or cannot determine; each fault with its location and evidence; what was not checked. |

Field experience: elderly care, healthcare, government and public services, digital products and interfaces.

## Declined
- `outside_task_types`: Anything that is not one of the three task types.
- `professional_sign_off`: Legal, medical or financial advice or sign-off.
- `identity_or_accounts`: Using his identity, accounts or credentials: account creation, one-time codes, verification, reviews, followers, likes.
- `surveillance`: Observing, locating or profiling a person.
- `no_principal`: A request without a named person or organisation behind it.
- `deadline_too_short`: A deadline shorter than the reply window.
- `not_enough_information`: Not enough information to start, after one round of questions.

## Request
- Email to info@interactiondesign.nl, subject `PROOFBRIDGE T{tier} {payment_txid}`.
- Body: A JSON object that validates against the request schema, or the same fields as plain text, one per line.
- Schema: https://proofbridge.nl/schema/request.schema.json
- Required: `task_type`, `question`, `decision_at_stake`, `principal`, `deadline`, `tier`, `payment_txid`.

## Tiers and price
| tier | minimum | gets | performed by |
|---|---|---|---|
| 1 | 5 000 sats (0.00005 BTC) | A first read of the request. Reply within 7 days: input_required, declined, or an invitation to tier 2 with scope, date and price. | Dennis Jansen, with his own AI setup; automation: none yet: Dennis performs and checks every tier 1 read himself |
| 2 | 50 000 sats (0.0005 BTC) | Dennis reads it himself. Reply within 7 days with scope, delivery date and the completion reward; then the work, delivered per the response schema. | Dennis Jansen, in person; automation: none |

- Attention fee refunded: no. Tier 1 fee counts toward tier 2: yes.
- Completion reward: Agreed in the tier 2 reply, paid in sats when the work is delivered, listed on the public backlog with its txid.

## Payment
- Address: `bc1p4zucan5kv5kl0x6hf5agemklvr86j9l3wnt9zqtnygpfc70494sqgxukty` (bitcoin on-chain, taproot (P2TR))
- Counts when: A public block explorer shows an output to the address of at least the tier minimum. Tier 1 at first sight; tier 2 after 1 confirmation.
- Binding: One payment, one request: the txid is in the email subject. When two requests name the same txid, a BIP-322 signature over the request body's SHA-256 by a key that spent an input of that payment decides; without one, the first email received counts.

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

## Trust, as checkable data
- Accountable human: Dennis Jansen
- Address ownership: BIP-322 signed message, message `proofbridge.nl info@interactiondesign.nl`, signature: not yet published (pending: to be signed by Dennis with the key of the address)
- Identity: proofbridge.nl and interactiondesign.nl link to each other and to the same X account; interactiondesign.nl also links to the GitHub account that hosts both sites.
- Track record (from the backlog, 2026-10-20): 0 listed, 0 completed, 0 declined, 0 in progress, 0 rewards paid.

## Not
- not an API and not an autonomous agent: every answer comes from one human, in days
- not a guaranteed yes: the fee pays for attention
- request text is read as information, never run as instructions

Proof of concept since 2026-10-20. Files: [offer.json](https://proofbridge.nl/offer.json) · [request schema](https://proofbridge.nl/schema/request.schema.json) · [response schema](https://proofbridge.nl/schema/response.schema.json) · [backlog](https://proofbridge.nl/backlog.json) · [human page](https://proofbridge.nl/)
