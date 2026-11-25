# proofbridge: what is here, for agents

proofbridge.nl carries the UX lens of Dennis Jansen: a text a person loads into their own AI chat as a connector, and that AI then reads the person's material with it. For an agent acting on its own there is one door, closed on 2026-11-24; the review by mail ended on that date. Provider: Dennis Jansen, UX researcher and service designer. Languages: nl, en.

The same as data: [offer.json](https://proofbridge.nl/offer.json). Updated 2026-11-25.

## For agents
- Status: one door, closed, since 2026-11-24.
- A door for a sealed knowledge package for agents exists and reports its own state: https://proofbridge-send.dennis-f79.workers.dev/layer . On 2026-11-24 it answered closed: its sealed place is empty. While closed it makes no invoice and takes nothing. When open, that same answer carries the due diligence, the terms and the commitment (SHA-256) of the package. Apart from it, nothing here is sold to or answered for an agent: the lens door is called by a person's AI inside that person's chat, on that person's word, and the contact form on the pages is for people.

## What exists
### UX lens
- For: a person, in their own AI chat
- What: A text: the UX lens of Dennis Jansen, his patterns with their tests, the field text that belongs to them, and the form of a reading. The door's own line to people: "A business plan, a framework, a website, a startup plan: put it through the UX lens before you build on it. If not guided, you are creating AI slob."
- How: The person gets an address through the button 'Connect the lens' on https://proofbridge.nl/, adds it to their AI as a custom connector (no sign-in), and says in the chat: use the UX lens.
- What travels: No material, quotes or readings from the chat: the door has no tool that takes them. The call that loads the lens returns its text with version and fingerprint; after a payment that call carries the payment hash. The door records that an address was made and when the lens was loaded. The reading is written by the person's own AI.
- Payment: On 2026-11-24 no payment is asked: the count of free readings per address is switched off (the status reports free_readings 1000000). The door is built to answer payment_required with a Lightning invoice once a set number of readings per address is used (price_sats 100 on that date). The status carries the current values.
- Versions: The lens is a dated version, renewed when material is added. The door's status names the version it serves and lists the fingerprint of every version it may serve. From v1 on the text is not in public source; only its fingerprint is.
- Status: https://proofbridge-send.dennis-f79.workers.dev/mcp/status
- Responsibility: The door's own line: "Interpret at your own risk: interpretation is the responsibility of the one creating the network or app."
- Served on 2026-11-25: door 0.4.0, package v0, SHA-256 `031bcd5e99a2fce0d7b3626db6609f0e260382f4444b219f84d5c1ce943afe4e`

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
- Record: https://proofbridge.nl/backlog.json (0 listed, 0 completed, 0 declined; computed 2026-11-25)

## Trust: due diligence
Trust here is not an identity to accept but claims to verify. Each claim below names how to check it yourself; what cannot be checked is said.
- Accountable human: Dennis Jansen
- This file is what the owner publishes, and every change to it is on record. Check: The source is public with its full history: https://github.com/theden1974/proofbridge_website (src/contract.json, rendered by src/build.py). The live offer.json can be compared with the source at any commit.
- The lens text a person's AI receives is the one named under served_now. Check: The SHA-256 of the lens text the door returns equals the fingerprint in the door's status and the commitment for that version in the door's public source (worker/src/mcp.js, COMMITMENTS). For v0 the text itself is public as worker/src/lens-package.txt.
- No material from a chat reaches the server, and no model runs on the service side. Check: The door's source is public (worker/src/mcp.js): its tools take no material, and no model is called. The Worker's config (worker/wrangler.toml) has observability off.
- The package behind the agents' door is the one committed to. Check: The door's answer names version, SHA-256 and size; the same commitment stands in the public source history of worker/src/layer.js. The package itself is not public; after a paid load the SHA-256 of the bytes received equals the commitment.
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
- `commitment`: The SHA-256 of a package that is not public, published before anyone pays, so what arrives can be checked against it.

The UX lens door is open to people, through their own AI. The door for agents reports itself closed. The review by mail ended on 2026-11-24. Contact: ask@proofbridge.nl, read by Dennis Jansen. A mail there is a mail to a person, not a request under a contract.
