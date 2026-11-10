# proofbridge UX lens, the door (MCP)

For agents, AI platforms and anyone doing due diligence. The page a person sees carries one line and one button; this file carries the rest.

## What it is
A text: the UX lens of Dennis Jansen (proofbridge.nl). An AI loads it and reads the user's material with it, in the user's own chat.

## What leaves the user's chat
Nothing. The door has no tool that receives material, quotes or readings. Tools: lens_about (what this is), lens_frame (returns the lens text).

## What the door records
That an address was made and when the lens text was loaded on it, and payments when payment is on. The caller's network address is kept only as a salted hash, to bound how many addresses one caller can make per day. No model runs on the door. No material is read on the door.

## Don't trust, verify
- Source of the door and the lens text: https://github.com/theden1974/proofbridge_website/tree/main/worker/src
- The door states the sha256 of the lens text it serves: GET https://proofbridge-send.dennis-f79.workers.dev/mcp/status
- The same text is the file lens-package.txt in the repository; hash it and compare.
- Not provable from outside: that the server runs exactly the repository's code. It is built from the repository by the host; no third party attests it.

## Access and payment
An address is made by the user (POST /mcp/address, no account). Payment, when on, is a Lightning invoice made by the owner's own node through an invoice-only connection: the door can ask for money, it cannot spend any.

## Who
Dennis Jansen, ask@proofbridge.nl. Interpret at your own risk: interpretation is the responsibility of the one creating the network or app.
