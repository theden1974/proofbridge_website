# proofbridge.nl build (v4). One run renders every output from three sources:
#   src/site.json      human page text (his words, traced in the build record)
#   src/contract.json  agent-facing contract (task types, inputs, outputs, lifecycle, payment, trust)
#   backlog.json       the public ledger; counts on /agents/ and in /offer.json are computed from it
# Usage: python3 src/build.py   (from the repo root, or anywhere)
import json, sys, html, os, hashlib
SRC = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(SRC)
C = json.load(open(os.path.join(SRC, 'site.json'), encoding='utf-8'))
K = json.load(open(os.path.join(SRC, 'contract.json'), encoding='utf-8'))
BL = json.load(open(os.path.join(OUT, 'backlog.json'), encoding='utf-8'))
H = C['hire']
addr, t1, t2, mail = C['btc_address'], C['tier1_sats'], C['tier2_sats'], C['email']
E = html.escape
def btc(s): return f"{s/1e8:.8f}".rstrip('0').rstrip('.')
def fmt(n): return f"{n:,}".replace(',', ' ')

VP = C['vps']
page_words = []

ld = {
  "@context": "https://schema.org", "@type": "WebPage", "url": "https://proofbridge.nl/",
  "name": "proofbridge · Dennis Jansen", "dateModified": C['updated'],
  "description": C['meta_description'],
  "mainEntity": {
    "@type": "Person", "@id": "https://interactiondesign.nl/#dennis", "name": "Dennis Jansen",
    "url": "https://interactiondesign.nl/", "sameAs": ["https://interactiondesign.nl/", "https://x.com/theden1974", "https://github.com/theden1974"],
    "description": C['intro'],
    "makesOffer": [
      {"@type": "Offer", "name": "Attention: my agent reads your request", "price": btc(t1), "priceCurrency": "BTC",
       "acceptedPaymentMethod": "Bitcoin (on-chain, taproot)", "url": "https://proofbridge.nl/#attention"},
      {"@type": "Offer", "name": "Attention: I read it myself", "price": btc(t2), "priceCurrency": "BTC",
       "acceptedPaymentMethod": "Bitcoin (on-chain, taproot)", "url": "https://proofbridge.nl/#attention"}
    ],
    "knowsAbout": [v['title'] for v in VP]
  }
}

def vp_html(i, v):
    return f'''  <article class="vp">
    <span class="label">0{i}</span>
    <h2>{E(v['title'])}</h2>
    <p>{E(v['text'])}</p>
    <p class="proof"><span class="label">↳ seen in the field</span>{E(v['proof'])}</p>
  </article>'''

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>proofbridge · Dennis Jansen</title>
<meta name="description" content="{E(C['meta_description'])}">
<link rel="canonical" href="https://proofbridge.nl/">
<link rel="alternate" type="text/markdown" href="/agents/index.md" title="Task contract for AI agents (markdown)">
<link rel="alternate" type="application/json" href="/offer.json" title="Offer for AI agents (JSON)">
<link rel="describedby" type="text/markdown" href="/llms.txt">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<meta property="og:title" content="proofbridge · Dennis Jansen">
<meta property="og:description" content="{E(C['meta_description'])}">
<meta property="og:url" content="https://proofbridge.nl/">
<meta property="og:type" content="profile">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500&family=IBM+Plex+Mono&display=swap" rel="stylesheet">
<script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
</script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --paper: hsl(45, 20%, 96%); --ink: #111014; --grey: hsl(240, 6%, 42%); --line: hsl(45, 10%, 86%);
    --accent: #b8862b;
    --s-1: clamp(0.8rem, 0.76rem + 0.2vw, 0.9rem);
    --s0: clamp(1rem, 0.95rem + 0.25vw, 1.15rem);
    --s1: clamp(1.25rem, 1.19rem + 0.31vw, 1.5rem);
    --s3: clamp(1.95rem, 1.6rem + 1.2vw, 2.6rem);
    --s5: clamp(2.4rem, 1.9rem + 2.4vw, 4rem);
    --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
  }}
  html {{ background: var(--paper); color: var(--ink); }}
  body {{ font-family: "DM Sans", system-ui, -apple-system, Helvetica, sans-serif; font-weight: 300; font-size: var(--s0); line-height: 1.55; }}
  .wrap {{ max-width: 68rem; margin: 0 auto; padding: 0 clamp(1rem, 4vw, 3rem); }}
  .bar {{ display: flex; justify-content: space-between; align-items: center; padding: 1.4rem 0; }}
  .label {{ font-family: var(--mono); font-size: var(--s-1); letter-spacing: 0.06em; text-transform: uppercase; color: var(--grey); display: block; margin-bottom: 0.9rem; }}
  .bar .label {{ margin: 0; }}
  .bar a {{ color: var(--ink); text-decoration: none; }}
  .intro {{ padding: clamp(3rem, 10vh, 7rem) 0 clamp(2.5rem, 7vh, 5rem); border-bottom: 1px solid var(--line); }}
  .intro h1 {{ font-weight: 500; font-size: var(--s5); line-height: 1.08; letter-spacing: -0.02em; max-width: 22ch; }}
  .intro p {{ font-size: var(--s1); color: var(--grey); max-width: 38ch; margin-top: 1.4rem; }}
  .vps {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: clamp(1.5rem, 3vw, 3rem); padding: clamp(2.5rem, 7vh, 5rem) 0; border-bottom: 1px solid var(--line); }}
  .vp h2 {{ font-weight: 500; font-size: var(--s3); line-height: 1.1; letter-spacing: -0.015em; margin-bottom: 1rem; }}
  .vp p {{ max-width: 34ch; }}
  .vp .proof {{ margin-top: 1.4rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--grey); font-size: var(--s-1); line-height: 1.5; }}
  .vp .proof .label {{ margin-bottom: 0.4rem; }}
  .catch, .why {{ padding: clamp(1.8rem, 5vh, 3rem) 0; border-bottom: 1px solid var(--line); }}
  .catch p, .why p {{ max-width: 44ch; font-size: var(--s1); line-height: 1.35; }}
  .why p + p {{ margin-top: 0.6rem; }}
  .note {{ font-family: var(--mono); font-size: var(--s-1); color: var(--grey); letter-spacing: 0; text-transform: none; font-weight: 300; }}
  .att {{ padding: clamp(2.5rem, 7vh, 5rem) 0; display: grid; grid-template-columns: 1fr 1.2fr; gap: clamp(1.5rem, 4vw, 4rem); border-bottom: 1px solid var(--line); }}
  .att h2 {{ font-weight: 500; font-size: var(--s3); line-height: 1.1; }}
  .tiers {{ list-style: none; }}
  .tiers li {{ display: flex; justify-content: space-between; gap: 1rem; padding: 0.8rem 0; border-bottom: 1px solid var(--line); }}
  .tiers b {{ font-weight: 500; white-space: nowrap; }}
  .tiers .hi {{ color: var(--accent); }}
  .addr {{ font-family: var(--mono); font-size: var(--s-1); word-break: break-all; margin-top: 1.2rem; padding: 0.9rem 1rem; border: 1px solid var(--line); border-radius: 1rem; background: #fff; }}
  .how {{ margin-top: 1rem; color: var(--grey); font-size: var(--s-1); }}
  .copy {{ margin-top: 0.8rem; font: inherit; font-family: var(--mono); font-size: var(--s-1); text-transform: uppercase; letter-spacing: 0.06em; background: var(--ink); color: var(--paper); border: 0; border-radius: 2rem; padding: 0.55rem 1.1rem; cursor: pointer; }}
  footer {{ padding: 2.5rem 0 3.5rem; display: flex; flex-wrap: wrap; gap: 1.6rem; align-items: baseline; }}
  footer a {{ color: var(--ink); }}
  footer .label {{ margin: 0; }}
  footer .agents {{ flex-basis: 100%; color: var(--grey); }} footer .agents a {{ color: var(--grey); }}
  a:focus-visible, button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
  @media (max-width: 860px) {{ .vps, .att {{ grid-template-columns: 1fr; }} }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --paper: #111014; --ink: hsl(45, 20%, 94%); --grey: hsl(240, 5%, 66%); --line: hsl(240, 5%, 22%); }}
    .addr {{ background: #1a191e; }} .copy {{ background: var(--ink); color: #111014; }}
  }}
</style>
</head>
<body>
<div class="wrap">

<header class="bar">
  <span class="label">proofbridge</span>
  <a class="label" href="https://interactiondesign.nl/">Dennis Jansen ↗</a>
</header>

<section class="intro" aria-labelledby="h1">
  <span class="label">↳ intro</span>
  <h1 id="h1">{E(C['h1'])}{(' <span class="note">(' + E(C['h1_note']) + ')</span>') if C.get('h1_note') else ''}</h1>
  <p>{E(C['intro'])}</p>
</section>

<section class="vps" aria-label="What I do">
{chr(10).join(vp_html(i+1, v) for i, v in enumerate(VP))}
</section>

<section class="why" aria-label="Why a human">
  <span class="label">↳ {E(C['why_label'])}</span>
  <p>{E(C['why'][0])}</p>
  <p>{E(C['why'][1])} <span class="note">({E(C['why_note'].replace('second line ', ''))})</span></p>
</section>

<section class="att" id="attention" aria-labelledby="h-att">
  <div>
    <span class="label">↳ attention</span>
    <h2 id="h-att">{E(C['att_title'])}</h2>
  </div>
  <div>
    <ul class="tiers">
      <li><span>{E(C['tier1_human'])}</span><b>{fmt(t1)} sats</b></li>
      <li><span>{E(C['tier2_human'])}</span><b class="hi">{fmt(t2)} sats</b></li>
    </ul>
    <p class="addr" id="addr">{addr}</p>
    <button class="copy" type="button" onclick="navigator.clipboard &amp;&amp; navigator.clipboard.writeText('{addr}').then(()=>this.textContent='copied')">Copy address</button>
    <p class="how">{E(C['att_how'])}</p>
  </div>
</section>

<footer>
  <span class="label">↳ connect</span>
  <a href="mailto:{mail}">{mail}</a>
  <a href="https://interactiondesign.nl/">interactiondesign.nl</a>
  <a href="https://x.com/theden1974">X</a>
  <p class="agents label">↳ for AI agents: <a href="/agents/">task contract</a></p>
</footer>

</div>
</body>
</html>
'''
open(f"{OUT}/index.html", "w", encoding="utf-8").write(page)

# ---------- stats, computed from the public ledger ----------
reqs = BL.get('requests', [])
def count(*st): return sum(1 for r in reqs if r.get('status') in st)
stats = {"requests_listed": len(reqs), "completed": count('completed'), "declined": count('declined'),
         "in_progress": count('seen', 'input_required', 'working'),
         "rewards_paid": sum(1 for r in reqs if r.get('reward_txid')), "computed_on": C['updated']}
TT = K['task_types']; TT_IDS = [x['id'] for x in TT]; DECL_IDS = [x['id'] for x in K['declines']]
STATES = [s['id'] for s in K['lifecycle']['states']]
T1, T2 = K['tiers']

# ---------- JSON Schemas (2020-12) ----------
req_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://proofbridge.nl/schema/request.schema.json",
  "title": "proofbridge request", "type": "object", "additionalProperties": False,
  "required": ["task_type", "question", "decision_at_stake", "principal", "deadline", "tier", "payment_txid"],
  "properties": {
    "task_type": {"enum": TT_IDS, "description": "; ".join(f"{x['id']}: {x['does']}" for x in TT)},
    "question": {"type": "string", "description": "What the principal wants to know, in one or two sentences."},
    "decision_at_stake": {"type": "string", "description": "The decision this answer informs."},
    "artefact_urls": {"type": "array", "items": {"type": "string", "format": "uri"}, "description": "Links to the data, document, output or brief to look at."},
    "artefact_text": {"type": "string", "description": "The material itself, when it is not at a link."},
    "context": {"type": "string", "description": "Who it is for, who decided it, where it is used."},
    "principal": {"type": "object", "additionalProperties": False, "required": ["name", "kind", "email"],
                  "properties": {"name": {"type": "string"}, "kind": {"enum": ["person", "organisation"]},
                                 "email": {"type": "string", "format": "email"}, "agent": {"type": "string", "description": "Name of the agent sending on the principal's behalf, if any."}}},
    "deadline": {"type": "string", "format": "date", "description": f"At least {K['lifecycle']['reply_window_days']} days after the payment."},
    "language": {"enum": K['provider']['languages']},
    "public_backlog_ok": {"type": "boolean", "default": False, "description": "true: task_type, status and dates may appear on the public backlog. The content never does."},
    "tier": {"enum": [1, 2]},
    "payment_txid": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "payment_proof_bip322": {"type": "string", "description": "Optional. BIP-322 signature over the SHA-256 of this request body, by a key that spent an input of the payment."},
    "completion_reward_sats": {"type": "integer", "minimum": 0, "description": "Optional proposal; the reward is agreed in the tier 2 reply."}
  }
}
evidence = {"type": "object", "required": ["type", "ref"], "additionalProperties": False,
            "properties": {"type": {"enum": ["field_observation", "interview", "source_quote", "document_reference"]}, "ref": {"type": "string"}}}
resp_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://proofbridge.nl/schema/response.schema.json",
  "title": "proofbridge response", "type": "object",
  "required": ["payment_txid", "status", "accountable_human"],
  "properties": {
    "payment_txid": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "status": {"enum": STATES},
    "eta": {"type": "string", "format": "date"},
    "questions": {"type": "array", "description": "When status is input_required.", "items": {"type": "object", "required": ["key", "question"], "properties": {"key": {"type": "string"}, "question": {"type": "string"}}}},
    "invitation": {"type": "object", "description": "Tier 1 reply that invites to tier 2.", "properties": {"scope": {"type": "string"}, "delivery_date": {"type": "string", "format": "date"}, "tier_2_sats": {"type": "integer"}, "completion_reward_sats": {"type": "integer"}}},
    "decline_reason": {"enum": DECL_IDS},
    "task_type": {"enum": TT_IDS},
    "verdict": {"enum": ["holds", "does_not_hold", "cannot_determine"], "description": "For ground_truth_check and ai_output_review."},
    "underlying_problem": {"type": "string", "description": "For underlying_problem: the problem as one statement."},
    "asked_versus_needed": {"type": "string"},
    "findings": {"type": "array", "items": {"type": "object", "required": ["statement", "evidence"], "properties": {"statement": {"type": "string"}, "location": {"type": "string"}, "evidence": {"type": "array", "items": evidence}}}},
    "limits": {"type": "array", "items": {"type": "string"}, "description": "What was not checked."},
    "next_step": {"type": "string"},
    "accountable_human": {"type": "object", "required": ["name"], "properties": {"name": {"const": K['trust']['accountable_human']}, "role": {"type": "string"}}},
    "delivered_at": {"type": "string", "format": "date"},
    "deliverable_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "completion_reward_sats": {"type": "integer"}, "reward_txid": {"type": "string", "pattern": "^[0-9a-f]{64}$"}
  }
}
os.makedirs(f"{OUT}/schema", exist_ok=True); os.makedirs(f"{OUT}/agents", exist_ok=True)
json.dump(req_schema, open(f"{OUT}/schema/request.schema.json", "w"), indent=2, ensure_ascii=False)
json.dump(resp_schema, open(f"{OUT}/schema/response.schema.json", "w"), indent=2, ensure_ascii=False)

# ---------- offer.json: contract first, background after ----------
offer = {k: v for k, v in K.items() if not k.startswith('_')}
offer.update({"site": "https://proofbridge.nl/", "updated": C['updated'], "stats": stats,
  "contract_page": "https://proofbridge.nl/agents/", "backlog": "https://proofbridge.nl/backlog.json",
  "background": {
    "value_propositions": [{"title": v['title'], "text": v['text'], "seen_in_the_field": v['proof']} for v in VP],
    "you_are_hiring": H['you_are_hiring'], "what_he_does": H['what_he_does'],
    "where_the_expertise_comes_from": H['where_the_expertise_comes_from'], "method": H['method'],
    "evidence_from_the_field": [{k: v for k, v in c.items() if v} for c in C['cases']],
    "more": ["https://interactiondesign.nl/setup/", "https://interactiondesign.nl/index.md"]}})
json.dump(offer, open(f"{OUT}/offer.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------- the contract as markdown (agents/index.md) and HTML (agents/) ----------
L = lambda xs: "\n".join(f"- {x}" for x in xs)
P = K['payment']
contract_md = f"""# proofbridge task contract

{K['summary']} Provider: {K['provider']['name']}, {K['provider']['role']}. Languages: {', '.join(K['provider']['languages'])}.

## Task types
| task_type | does | input | output |
|---|---|---|---|
""" + "\n".join(f"| `{x['id']}` | {x['does']} | {x['input']} | {x['output']} |" for x in TT) + f"""

Field experience: {', '.join(K['domains_with_field_experience'])}.

## Declined
""" + "\n".join(f"- `{d['id']}`: {d['rule']}" for d in K['declines']) + f"""

## Request
- Email to {K['request']['to']}, subject `{K['request']['subject']}`.
- Body: {K['request']['body']}
- Schema: {K['request']['schema']}
- Required: {', '.join('`'+r+'`' for r in req_schema['required'])}.

## Tiers and price
| tier | minimum | gets | performed by |
|---|---|---|---|
""" + "\n".join(f"| {x['tier']} | {fmt(x['minimum_sats'])} sats ({btc(x['minimum_sats'])} BTC) | {x['gets']} | {x['performed_by']}; automation: {x['automation']} |" for x in K['tiers']) + f"""

- Attention fee refunded: no. Tier 1 fee counts toward tier 2: yes.
- Completion reward: {K['fees']['completion_reward']}

## Payment
- Address: `{P['address']}` ({P['rail']}, {P['address_type']})
- Counts when: {P['counts_when']}
- Binding: {P['binding']}

## Lifecycle
""" + "\n".join(f"- `{s['id']}`: {s['meaning']}" for s in K['lifecycle']['states']) + f"""
- Reply window: {K['lifecycle']['reply_window_days']} days. {K['lifecycle']['reply_window_rule']}
- Public status: {K['lifecycle']['public_status']}

## Response
- Schema: {K['response']['schema']}
- Completed work carries `verdict` (holds / does_not_hold / cannot_determine) or `underlying_problem`, `findings` with typed `evidence`, `limits`, `next_step`, and `accountable_human`.

## Trust, as checkable data
- Accountable human: {K['trust']['accountable_human']}
- Address ownership: {K['trust']['address_ownership']['method']}, message `{K['trust']['address_ownership']['message']}`, signature: {K['trust']['address_ownership']['signature'] or 'not yet published'} ({K['trust']['address_ownership']['status']})
- Identity: {K['trust']['identity_links']}
- Track record (from the backlog, {stats['computed_on']}): {stats['requests_listed']} listed, {stats['completed']} completed, {stats['declined']} declined, {stats['in_progress']} in progress, {stats['rewards_paid']} rewards paid.

## Not
{L(K['not'])}

{K['status']} Files: [offer.json](https://proofbridge.nl/offer.json) · [request schema](https://proofbridge.nl/schema/request.schema.json) · [response schema](https://proofbridge.nl/schema/response.schema.json) · [backlog](https://proofbridge.nl/backlog.json) · [human page](https://proofbridge.nl/)
"""
open(f"{OUT}/agents/index.md", "w", encoding="utf-8").write(contract_md)

def md_to_html(md):
    out, inlist, intable = [], False, False
    def inline(s):
        s = E(s)
        import re as _r
        s = _r.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = _r.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', s)
        return s
    for line in md.split("\n"):
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if set(''.join(cells)) <= set('-'): continue
            if not intable: out.append('<table>'); intable = True; out.append('<tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr>'); continue
            out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>'); continue
        if intable: out.append('</table>'); intable = False
        if line.startswith('- '):
            if not inlist: out.append('<ul>'); inlist = True
            out.append(f'<li>{inline(line[2:])}</li>'); continue
        if inlist: out.append('</ul>'); inlist = False
        if line.startswith('# '): out.append(f'<h1>{inline(line[2:])}</h1>')
        elif line.startswith('## '): out.append(f'<h2>{inline(line[3:])}</h2>')
        elif line.strip(): out.append(f'<p>{inline(line)}</p>')
    if inlist: out.append('</ul>')
    if intable: out.append('</table>')
    return "\n".join(out)

agents_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Task contract · proofbridge</title>
<meta name="description" content="{E(K['summary'])}">
<link rel="canonical" href="https://proofbridge.nl/agents/">
<link rel="alternate" type="text/markdown" href="/agents/index.md">
<link rel="alternate" type="application/json" href="/offer.json">
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ background: hsl(45, 20%, 96%); color: #111014; }}
  body {{ font-family: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace; font-size: 0.9rem; line-height: 1.55; max-width: 60rem; margin: 0 auto; padding: 2rem clamp(1rem, 4vw, 2rem) 4rem; overflow-wrap: anywhere; }}
  h1 {{ font-size: 1.4rem; }} h2 {{ font-size: 1rem; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2.2rem; border-top: 1px solid hsl(45, 10%, 82%); padding-top: 1rem; }}
  table {{ border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }} th, td {{ text-align: left; vertical-align: top; padding: 0.4rem 0.6rem 0.4rem 0; border-bottom: 1px solid hsl(45, 10%, 86%); }}
  code {{ background: hsl(45, 15%, 90%); padding: 0 0.2rem; word-break: break-all; }} td:first-child code {{ white-space: nowrap; word-break: normal; }} a {{ color: inherit; }}
  @media (prefers-color-scheme: dark) {{ html {{ background: #111014; color: hsl(45, 20%, 94%); }} code {{ background: #1f1e24; }} h2, th, td {{ border-color: hsl(240, 5%, 24%); }} }}
</style>
</head>
<body>
<p><a href="/">← proofbridge.nl</a></p>
{md_to_html(contract_md)}
</body>
</html>
"""
open(f"{OUT}/agents/index.html", "w", encoding="utf-8").write(agents_html)

# ---------- llms.txt: short, task language, pointers ----------
llms = f"""# proofbridge.nl

> {K['summary']} Provider: {K['provider']['name']}, {K['provider']['role']}.

Task types (closed list):
""" + "\n".join(f"- `{x['id']}`: {x['does']} Output: {x['output']}" for x in TT) + f"""

Price: tier 1 from {fmt(T1['minimum_sats'])} sats, tier 2 from {fmt(T2['minimum_sats'])} sats, on-chain bitcoin. Reply within {K['lifecycle']['reply_window_days']} days. Declines: {', '.join('`'+d+'`' for d in DECL_IDS)}.

## Contract
- [Task contract (markdown)](https://proofbridge.nl/agents/index.md)
- [Task contract (HTML)](https://proofbridge.nl/agents/)
- [Offer as JSON](https://proofbridge.nl/offer.json)
- [Request schema](https://proofbridge.nl/schema/request.schema.json)
- [Response schema](https://proofbridge.nl/schema/response.schema.json)
- [Backlog](https://proofbridge.nl/backlog.json)

## Optional
- [Background: value propositions and field evidence (markdown)](https://proofbridge.nl/index.md)
- [How Dennis works](https://interactiondesign.nl/setup/index.md)
- [Observations](https://interactiondesign.nl/index.md)
"""
open(f"{OUT}/llms.txt", "w", encoding="utf-8").write(llms)

# ---------- index.md: the human page plus background, for readers that prefer markdown ----------
def case_md(c):
    s = f"### {c['domain']}\n"
    if c.get('start'): s += f"- Starting point: {c['start']}\n"
    return s + f"- What I saw: {c['saw']}\n- After: {c['after']}\n"
bg = f"# proofbridge · Dennis Jansen\n\n## {C['h1']}\n\n{C['intro']}\n\n" + "\n".join(f"### {i+1}. {v['title']}\n{v['text']}\n- Seen in the field: {v['proof']}\n" for i, v in enumerate(VP)) + f"""
## My attention costs sats
- {C['tier1_human']}: {fmt(T1['minimum_sats'])} sats
- {C['tier2_human']}: {fmt(T2['minimum_sats'])} sats
- {C['att_how']}

## Background
{H['you_are_hiring']}

{H['what_he_does']}

### Where the expertise comes from
{L(H['where_the_expertise_comes_from'])}

### Method
{L(H['method'])}

### Evidence from the field
""" + "\n".join(case_md(c) for c in C['cases']) + "\nThe task contract for agents: https://proofbridge.nl/agents/index.md\n"
open(f"{OUT}/index.md", "w", encoding="utf-8").write(bg)

# ---------- backlog.json keeps its entries; its field list follows the contract ----------
BL.update({"fields": ["id", "received", "tier", "task_type", "payment_txid", "status", "eta", "delivered_at", "verdict", "completion_reward_sats", "reward_txid"],
           "status_values": STATES, "task_types": TT_IDS, "statement": "Public ledger of requests with public_backlog_ok true. Content of requests is never listed. Proof of concept since 2026-10-20."})
json.dump(BL, open(f"{OUT}/backlog.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------- sitemap ----------
urls = ["https://proofbridge.nl/", "https://proofbridge.nl/agents/", "https://proofbridge.nl/agents/index.md", "https://proofbridge.nl/llms.txt", "https://proofbridge.nl/offer.json", "https://proofbridge.nl/index.md", "https://proofbridge.nl/backlog.json", "https://proofbridge.nl/schema/request.schema.json", "https://proofbridge.nl/schema/response.schema.json"]
open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{C['updated']}</lastmod></url>\n" for u in urls) + "</urlset>\n")

import re
txt = re.sub(r'<script.*?</script>', '', page[page.index('<body>'):], flags=re.S); txt = re.sub(r'<[^>]+>', ' ', txt)
print("visible words:", len(html.unescape(txt).split()), "| stats:", stats)
