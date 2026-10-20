# BRANDBOOK — proofbridge.nl
# Decision engine. Agent-readable. Same logic as interactiondesign.nl/BRANDBOOK.md and vocabulary.md.
# Dennis verifies through output, not inspection.
# Add decisions. Never rewrite. Git tracks evolution.
# Created: 2026-10-20 (REFLECT build session, MUP). Status of every decision: pending use — one line of Dennis reverts any.

---

site_purpose:
  decision: One page where people and AI agents read the same offer: need a human. Attention is paid in sats.
  source: Dennis 2026-10-20 — "I want my proof bridge and interactiondesign to bridge my world my expertise and offer this as a service to the agents, need a human" (C135 D-M2); "there needs to be a minimal payment to get my attention"; "The proposition needs a agentic context to being understood by agents how what they are hiring, Make for both websites a MUP".
  confusable_with:
    - interactiondesign.nl: the observation channel (singer-songwriter). proofbridge.nl is the offer (concert hall, purpose driven, agent ready — D035, 2026-04-21). Test — does the element state the offer or show an observation? Offer here, observation there.
  status: pending use

voice:
  decision: Every line about Dennis comes from his own words (written chats, his spoken talks, his captures). Terms (prices, steps, fields) may be composed and are marked as terms in the build record.
  locked_by: Dennis 2026-10-20 — "The proposal is now generated it needs to origin from my own hands on experience". The independent check of the first build found his old AI-written LinkedIn/Proofbridge text in the most visible places ("this is ai chosen"); removed.
  confusable_with:
    - old_proofbridge_copy: "AI is trained on publications…", "Companies buy solutions that sound right…", "The gap between what AI reads…". Test — is the line in his chats, talks or captures, not only in the LinkedIn/Proofbridge text he flagged? If only there, it does not go on the page.
  status: pending use

agent_layer:
  decision: The page, /offer.json, /llms.txt and /index.md carry the same words. The page shows the full offer.json in a visible details block. JSON-LD (schema.org WebPage → Person → Offer, price in BTC) carries only visible values.
  locked_by: C135 H3 and Nate N-M28–N-M30 — a message only agents can read is the attack hallmark; research 2026-10-20 (Google structured-data and spam policies; prompt-injection defences).
  rules:
    - Terms are written as descriptions ("A request starts with…"), never as instructions to an agent.
    - No A2A agent card and no MCP server card: both promise a live endpoint a static site does not have. Revisit when a hosted endpoint exists.
  status: pending use

attention_in_sats:
  decision: Tier 1 triage 5 000 sats, tier 2 human attention 50 000 sats, on-chain taproot address bc1p4zucan5kv5kl0x6hf5agemklvr86j9l3wnt9zqtnygpfc70494sqgxukty. Txid in the email subject; first claim wins; tier 1 counts when seen, tier 2 after 1 confirmation. Fee not refunded; tier 1 counts toward tier 2 when invited. Completion reward agreed in tier 2, paid to the same address, listed on /backlog.json.
  locked_by: research 2026-10-20 "Sats gated attention mechanisms" — a price filters senders and sharpens targeting but does not buy replies; on-chain sensible from ~5k sats at 1–2 sat/vB.
  open:
    - Dennis confirms he holds the key of the address.
    - Lightning Address or silent payment address as phase 2 (smaller amounts, no address reuse).
    - The tier 1 triage agent is not built (freeze). Until it is, Dennis sorts tier 1 himself; the page says so.
  status: pending use

design:
  decision: Direction D from June (Claude Design, "Squarefi two-tone · the seam as a two-panel grid"), interpreted: warm paper panel for people, near-black panel for agents, one gold seam between them. Bebas Neue headlines, DM Sans body — inherited from interactiondesign.nl.
  open: the Claude Design file itself was not reachable in the build session; Dennis compares by eye.
  status: pending use

deploy_mechanism:
  decision: Same as interactiondesign.nl — public trail in git, GitHub Pages from main, custom domain via CNAME, DNS at Namecheap. .nojekyll so .md, .txt and .json are served as-is.
  status: pending use
