# proofbridge-send
The relay behind the Send button on proofbridge.nl/ask/. One request in, one mail out to ask@proofbridge.nl, nothing stored, no content logged.
Deployed by Cloudflare from this folder (Workers & Pages → import repository → root directory `worker`). Secrets SMTP_USER and SMTP_PASS live in the Cloudflare dashboard only.
Who sees the text: Cloudflare as the carrier, then Private Email (the mailbox). No model, no third party.
