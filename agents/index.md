# proofbridge: what is here, for agents

proofbridge.nl carries the UX lens of Dennis Jansen: a text a person loads into their own AI chat as a connector, and that AI then reads the person's material with it. Nothing here is sold to, or answered for, an agent acting on its own; the review by mail ended on 2026-11-24. Provider: Dennis Jansen, UX researcher and service designer. Languages: nl, en.

The same as data: [offer.json](https://proofbridge.nl/offer.json). Updated 2026-11-24.

## For agents
- Status: nothing for an agent acting on its own, since 2026-11-24.
- No door here takes a request from an agent and returns an answer, and nothing is sold to an agent. The lens door is called by a person's AI inside that person's chat, on that person's word, and returns a text. The contact form on the pages is for people.

## What exists
### UX lens
- For: a person, in their own AI chat
- What: A text: the UX lens of Dennis Jansen, a set of structural moves with their tests, published field observations, and the form of a reading. The door's own line to people: "A business plan, a framework, a website, a startup plan: put it through the UX lens before you build on it. If not guided, you are creating AI slob."
- How: The person gets an address through the button 'Connect the lens' on https://proofbridge.nl/, adds it to their AI as a custom connector (no sign-in), and says in the chat: use the UX lens.
- What travels: No material, quotes or readings from the chat: the door has no tool that takes them. The call that loads the lens returns its text with version and fingerprint; after a payment that call carries the payment hash. The door records that an address was made and when the lens was loaded. The reading is written by the person's own AI.
- Payment: On 2026-11-24 no payment is asked: the count of free readings per address is switched off (the status reports free_readings 1000000). The door is built to answer payment_required with a Lightning invoice once a set number of readings per address is used (price_sats 100 on that date). The status carries the current values.
- Status: https://proofbridge-send.dennis-f79.workers.dev/mcp/status
- Responsibility: The door's own line: "Interpret at your own risk: interpretation is the responsibility of the one creating the network or app."
- Served on 2026-11-24: door 0.3.0, package v0, SHA-256 `031bcd5e99a2fce0d7b3626db6609f0e260382f4444b219f84d5c1ce943afe4e`

### Observations
- For: people and agents, to read
- What: Nineteen cases where AI output, plans or data and the field part ways, each with its source.
- Where: https://interactiondesign.nl/index.md

### How I work
- For: people and agents, to read
- What: Why, the gap, how he works, the door to the UX lens.
- Where: https://interactiondesign.nl/setup/index.md

## What ended
### `review_by_mail` · 2026-10-20 to 2026-11-24
- Was: Asynchronous review by Dennis Jansen of a request sent by POST (100 sats over Lightning from 2026-10-29), by email or through the ask page, answered by email within 7 days.
- Now: The agent intake answers 410 and takes no request, no invoice and no payment. The ask page is closed. The request and response schemas, the examples and the OpenAPI file are withdrawn.
- Record: https://proofbridge.nl/backlog.json (0 listed, 0 completed, 0 declined; computed 2026-11-24)

## Trust: due diligence
Trust here is not an identity to accept but claims to verify. Each claim below names how to check it yourself; what cannot be checked is said.
- Accountable human: Dennis Jansen
- This file is what the owner publishes, and every change to it is on record. Check: The source is public with its full history: https://github.com/theden1974/proofbridge_website (src/contract.json, rendered by src/build.py). The live offer.json can be compared with the source at any commit.
- The lens text a person's AI receives is the one named under served_now. Check: The SHA-256 of the lens text the door returns equals the fingerprint in the door's status and the SHA-256 of worker/src/lens-package.txt in the public source.
- No material from a chat reaches the server, and no model runs on the service side. Check: The door's source is public (worker/src/mcp.js): its tools take no material, and no model is called. The Worker's config (worker/wrangler.toml) has observability off.
- The lens comes from field work, not from theory. Check: The published observations each carry their source: https://interactiondesign.nl/index.md. What a fingerprint cannot show: that a reading made with the lens is true. That stays with the one who builds on it.
- The review by mail left a record. Check: backlog.json, as it stood when the path closed. It shows what exists, including zero.

## Processing
- A Cloudflare Worker on Dennis's account carries the lens door and a contact form for people on the pages (their email and a note). Its source is public: https://github.com/theden1974/proofbridge_website/tree/main/worker
- A note from the contact form is mailed to Dennis and not stored by the Worker. Mail is carried by Namecheap Private Email (servers in the United States).
- The lens door keeps a ledger of addresses made, loads and invoices. It holds no material and no name.

Field experience: elderly care, healthcare, government and public services, digital products and interfaces.

## Not
- no answers are made on this site: a reading is written by the person's own AI, with the lens text loaded
- not an autonomous agent
- not a review service: no material is taken in and no review is sent back

## Glossary
- `lens`: Dennis's way of reading material: what is asked for, and the problem underneath it, checked against how the work happens in the field. Here: the text that carries it.
- `address`: The connector URL a person gets at the lens door. It names no person; the door counts loads per address.
- `load`: One call that returns the lens text to the person's AI.
- `fingerprint`: The SHA-256 of the lens text, so a reader can check which text was served.
- `due_diligence`: Checks a reader can run itself to verify the claims made here, listed under trust.
- `door`: The connector endpoint that serves the lens text (an MCP server on the Worker).
- `package`: The lens text in one dated version; v0 is the one served.
- `connector`: What AI chat apps call an added MCP server.
- `payment_required`: The door's answer when a reading has to be paid first: it carries a Lightning invoice in sats (1 sat = 0.00000001 bitcoin).

The UX lens door is open to people, through their own AI. Nothing is offered to an agent acting on its own. The review by mail ended on 2026-11-24. Contact: ask@proofbridge.nl, read by Dennis Jansen. A mail there is a mail to a person, not a request under a contract.
