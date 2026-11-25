# proofbridge.nl build (v5, 2026-11-24). One run renders every output from three sources:
#   src/site.json      human page text (his words, traced in the build record)
#   src/contract.json  what the site says to agents: what exists, what ended, how to check it
#   backlog.json       the record of the review by mail (ended 2026-11-24); its count is computed, never typed
# Usage: python3 src/build.py   (from the repo root, or anywhere)
import json, html, os
SRC = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(SRC)
C = json.load(open(os.path.join(SRC, 'site.json'), encoding='utf-8'))
K = json.load(open(os.path.join(SRC, 'contract.json'), encoding='utf-8'))
_h = open(os.path.join(SRC, 'hire.html'), encoding='utf-8').read()
HIRE_CSS = _h.split('<!--css-->')[1].split('<!--button-->')[0].strip('\n'); HIRE_BTN = _h.split('<!--button-->')[1].split('<!--dialog-->')[0].strip('\n'); HIRE_DIALOG = _h.split('<!--dialog-->')[1].strip('\n')
BL = json.load(open(os.path.join(OUT, 'backlog.json'), encoding='utf-8'))
import datetime as _dt
C['updated'] = _dt.date.today().isoformat()  # dates generated at build time
H = C['hire']
mail = C['email']
E = html.escape
def btc(s): return f"{s/1e8:.8f}".rstrip('0').rstrip('.')
def fmt(n): return f"{n:,}".replace(',', ' ')

VP = C['vps']

ld = {
  "@context": "https://schema.org", "@type": "WebPage", "url": "https://proofbridge.nl/",
  "name": "proofbridge · Dennis Jansen", "dateModified": C['updated'],
  "description": C['meta_description'],
  "mainEntity": {
    "@type": "Person", "@id": "https://interactiondesign.nl/#dennis", "name": "Dennis Jansen",
    "url": "https://interactiondesign.nl/", "sameAs": ["https://interactiondesign.nl/", "https://x.com/theden1974"],
    "description": C['intro'],
    "knowsAbout": K['knows_about']
  }
}

def vp_html(i, v):
    return f'''  <article class="vp">
    <span class="label">0{i}</span>
    <h2>{E(v['title'])}</h2>
    <p>{E(v['text'])}</p>
    <p class="proof">{E(v["proof"])}</p>
  </article>'''

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>proofbridge · Dennis Jansen</title>
<meta name="description" content="{E(C['meta_description'])}">
<link rel="canonical" href="https://proofbridge.nl/">
<link rel="alternate" type="text/markdown" href="/index.md" title="This page as markdown">
<link rel="alternate" type="application/json" href="/offer.json" title="What is here, for AI agents (JSON)">
<link rel="describedby" type="text/markdown" href="/llms.txt">
<meta property="og:title" content="proofbridge · Dennis Jansen">
<meta property="og:description" content="{E(C['meta_description'])}">
<meta property="og:url" content="https://proofbridge.nl/">
<meta property="og:type" content="profile">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500&family=IBM+Plex+Mono&display=swap" rel="stylesheet">
<script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
</script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --paper: hsl(45, 20%, 96%); --ink: #111014; --grey: hsl(240, 6%, 42%); --line: hsl(45, 10%, 86%);
    --accent: #b8862b; color-scheme: dark;
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
  .vp .proof {{ margin-top: 1.4rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--grey); font-size: var(--s-1); line-height: 1.5; }}
  .vp .proof .label {{ margin-bottom: 0.4rem; }}
  .note {{ font-family: var(--mono); font-size: var(--s-1); color: var(--grey); letter-spacing: 0; text-transform: none; font-weight: 300; }}
  .att h2 {{ font-weight: 500; font-size: var(--s3); line-height: 1.1; }}
  .story {{ padding: clamp(2.5rem, 7vh, 5rem) 0; border-bottom: 1px solid var(--line); display: grid; gap: 1.6rem; max-width: 42ch; }}
  .story p {{ font-size: var(--s1); line-height: 1.45; }} .story p::first-line {{ font-weight: 500; }} .story .who {{ color: var(--grey); }}
  .ways {{ padding: clamp(2.5rem, 7vh, 5rem) 0; border-bottom: 1px solid var(--line); display: block; }}
  .way h2 {{ font-weight: 500; font-size: var(--s2); line-height: 1.15; margin-bottom: .8rem; }} .way p {{ max-width: 34ch; margin-bottom: 1rem; }}
  @media (max-width: 860px) {{ .ways {{ grid-template-columns: 1fr; }} }}
  .att .door {{ font-size: var(--s1); line-height: 1.45; max-width: 42ch; margin-bottom: 1.2rem; }} .att .door::first-line {{ font-weight: 500; }}
  .btn {{ display: inline-block; font-family: var(--mono); font-size: var(--s-1); text-transform: uppercase; letter-spacing: 0.08em; background: var(--ink); color: var(--paper); border-radius: 2rem; padding: 0.7rem 1.3rem; text-decoration: none; }}
  .how {{ margin-top: 1rem; color: var(--grey); font-size: var(--s-1); }}
  footer {{ padding: 2.5rem 0 3.5rem; display: flex; flex-wrap: wrap; gap: 1.6rem; align-items: baseline; }}
  footer a {{ color: var(--ink); }}
  footer .label {{ margin: 0; }}
  footer .agents {{ flex-basis: 100%; color: var(--grey); }} footer .agents a {{ color: var(--grey); }}
  a:focus-visible, button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
  @media (max-width: 860px) {{ .vps, .att {{ grid-template-columns: 1fr; }} }}
  @media all {{
    :root {{ --paper: #111014; --ink: hsl(45, 20%, 94%); --grey: hsl(240, 5%, 66%); --line: hsl(240, 5%, 22%); }}
  }}
{HIRE_CSS}
</style>
</head>
<body>
<div class="wrap">

<header class="bar">
  <span class="label">proofbridge</span>
  <a class="label" href="https://interactiondesign.nl/">Dennis Jansen ↗</a>
</header>

<section class="intro" aria-labelledby="h1">
  <h1 id="h1">{E(C['h1'])}</h1>
</section>

<section class="ways" aria-label="The lens">
  <div class="way"><p>{E(C['ways'][0]['text'])}</p><p><a class="btn" href="{C['ways'][0]['href']}">{E(C['ways'][0]['btn'])}</a></p></div>
</section>

<footer>
  <span class="label">↳ connect</span>
  <a href="mailto:{mail}">{mail}</a>
  <a href="https://interactiondesign.nl/">interactiondesign.nl</a>
{HIRE_BTN}
</footer>

</div>
{HIRE_DIALOG}
</body>
</html>
'''
open(f"{OUT}/index.html", "w", encoding="utf-8").write(page)

# ---------- the record of the ended path: computed, never typed ----------
reqs = BL.get('requests', [])
def count(*st): return sum(1 for r in reqs if r.get('status') in st)
record = {"requests_listed": len(reqs), "completed": count('completed'), "declined": count('declined'), "computed_on": C['updated']}
L = lambda xs: "\n".join(f"- {x}" for x in xs)
X = K['exists']; LENS = X[0]; END = K['ended']; T = K['trust']
os.makedirs(f"{OUT}/agents", exist_ok=True)

# ---------- offer.json: the contract as it is, plus pointers ----------
offer = {k: v for k, v in K.items() if not k.startswith('_')}
offer.update({"site": "https://proofbridge.nl/", "updated": C['updated'], "record_of_the_ended_path": record,
  "this_as_page": "https://proofbridge.nl/agents/", "this_as_markdown": "https://proofbridge.nl/agents/index.md",
  "background": "https://proofbridge.nl/index.md"})
json.dump(offer, open(f"{OUT}/offer.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------- the same as markdown (agents/index.md) and HTML (agents/) ----------
def exists_md(x):
    s = f"### {x['name']}\n- For: {x['for']}\n- What: {x['what']}\n"
    for k, lab in (('how', 'How'), ('what_travels', 'What travels'), ('payment', 'Payment'), ('versions', 'Versions'), ('status', 'Status'), ('url', 'Where'), ('responsibility', 'Responsibility')):
        if x.get(k): s += f"- {lab}: {x[k]}\n"
    if x.get('served_now'):
        v = x['served_now']; s += f"- Served on {v['read_on']}: door {v['door']}, package {v['package']}, SHA-256 `{v['sha256']}`\n"
    return s
contract_md = f"""# proofbridge: what is here, for agents

{K['summary']} Provider: {K['provider']['name']}, {K['provider']['role']}. Languages: {', '.join(K['provider']['languages'])}.

The same as data: [offer.json](https://proofbridge.nl/offer.json). Updated {C['updated']}.

## For agents
- Status: {K['for_agents']['status']}, since {K['for_agents']['since']}.
- {K['for_agents']['detail']}

## What exists
""" + "\n".join(exists_md(x) for x in X) + """
## What ended
""" + "\n".join(f"### `{e['id']}` · {e['from']} to {e['until']}\n- Was: {e['was']}\n- Now: {e['now']}\n- Record: {e['record']} ({record['requests_listed']} listed, {record['completed']} completed, {record['declined']} declined; computed {record['computed_on']})\n" for e in END) + f"""
## Trust: due diligence
{T['principle']}
- Accountable human: {T['accountable_human']}
""" + "\n".join(f"- {x['claim']} Check: {x['check']}" for x in T['due_diligence']) + f"""

## Processing
""" + "\n".join(f"- {v}" for v in K['processing'].values()) + f"""

Field experience: {', '.join(K['domains_with_field_experience'])}.

## Not
{L(K['not'])}

## Glossary
""" + "\n".join(f"- `{k}`: {v}" for k, v in K['glossary'].items()) + f"""

{K['status']} Contact: {K['contact']}
"""
open(f"{OUT}/agents/index.md", "w", encoding="utf-8").write(contract_md)

def md_to_html(md):
    out, inlist = [], False
    def inline(s):
        s = E(s)
        import re as _r
        s = _r.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = _r.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', s)
        s = _r.sub(r'(?<![">])(https?://[^\s<)]+[^\s<).,;:])', r'<a href="\1">\1</a>', s)
        return s
    for line in md.split("\n"):
        if line.startswith('- '):
            if not inlist: out.append('<ul>'); inlist = True
            out.append(f'<li>{inline(line[2:])}</li>'); continue
        if inlist: out.append('</ul>'); inlist = False
        if line.startswith('# '): out.append(f'<h1>{inline(line[2:])}</h1>')
        elif line.startswith('## '): out.append(f'<h2>{inline(line[3:])}</h2>')
        elif line.startswith('### '): out.append(f'<h3>{inline(line[4:])}</h3>')
        elif line.strip(): out.append(f'<p>{inline(line)}</p>')
    if inlist: out.append('</ul>')
    return "\n".join(out)

agents_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>What is here, for agents · proofbridge</title>
<meta name="description" content="{E(K['summary'])}">
<link rel="canonical" href="https://proofbridge.nl/agents/">
<link rel="alternate" type="text/markdown" href="/agents/index.md">
<link rel="alternate" type="application/json" href="/offer.json">
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ background: #111014; color: hsl(45, 20%, 94%); color-scheme: dark; }}
  body {{ font-family: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace; font-size: 0.9rem; line-height: 1.55; max-width: 60rem; margin: 0 auto; padding: 2rem clamp(1rem, 4vw, 2rem) 4rem; overflow-wrap: anywhere; }}
  h1 {{ font-size: 1.4rem; }} h2 {{ font-size: 1rem; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2.2rem; border-top: 1px solid hsl(240, 5%, 24%); padding-top: 1rem; }} h3 {{ font-size: 0.9rem; margin-top: 1.4rem; }}
  code {{ background: #1f1e24; padding: 0 0.2rem; word-break: break-all; }} a {{ color: inherit; }}
</style>
</head>
<body>
<p><a href="/">← proofbridge.nl</a></p>
{md_to_html(contract_md)}
</body>
</html>
"""
open(f"{OUT}/agents/index.html", "w", encoding="utf-8").write(agents_html)

# ---------- llms.txt: short, pointers ----------
llms = f"""# proofbridge.nl

> {K['summary']} Provider: {K['provider']['name']}, {K['provider']['role']}.

- For agents: {K['for_agents']['status']}, since {K['for_agents']['since']}. {K['for_agents']['detail']}
- UX lens ({LENS['for']}): {LENS['what']} {LENS['how']} {LENS['what_travels']}
- Ended: """ + " ".join(f"{e['was']} ({e['from']} to {e['until']}.) {e['now']}" for e in END) + f"""

## What is here
- [What is here, for agents (markdown)](https://proofbridge.nl/agents/index.md)
- [The same as JSON](https://proofbridge.nl/offer.json)
- [The same as a page](https://proofbridge.nl/agents/)

## Optional
- [Background: field evidence (markdown)](https://proofbridge.nl/index.md)
- [How Dennis works](https://interactiondesign.nl/setup/index.md)
- [Observations](https://interactiondesign.nl/index.md)
"""
open(f"{OUT}/llms.txt", "w", encoding="utf-8").write(llms)

# ---------- index.md: the human page plus background, for readers that prefer markdown ----------
def case_md(c):
    s = f"### {c['domain']}\n"
    if c.get('start'): s += f"- Starting point: {c['start']}\n"
    return s + f"- What I saw: {c['saw']}\n- After: {c['after']}\n"
W = C['ways'][0]
bg = f"# proofbridge · Dennis Jansen\n\n## {C['h1']}\n\n{W['text']} [{W['btn']}](https://proofbridge.nl{W['href']})\n\n" + "\n".join(f"### {i+1}. {v['title']}\n{v['text']}\n- Seen in the field: {v['proof']}\n" for i, v in enumerate(VP)) + f"""
## Background
{H['you_are_hiring']}

{H['what_he_does']}

### Where the expertise comes from
{L(H['where_the_expertise_comes_from'])}

### Method
{L(H['method'])}

### Evidence from the field
""" + "\n".join(case_md(c) for c in C['cases']) + "\nWhat is here, for agents: https://proofbridge.nl/agents/index.md\n"
open(f"{OUT}/index.md", "w", encoding="utf-8").write(bg)

# ---------- backlog.json: the record of the ended path, closed as it stood ----------
BL = {"site": "https://proofbridge.nl/", "closed": END[0]['until'],
      "statement": f"Record of the review by mail, {END[0]['from']} to {END[0]['until']}. Closed. Content of requests was never listed. {END[0]['now']}",
      "requests": reqs}
json.dump(BL, open(f"{OUT}/backlog.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------- sitemap ----------
urls = ["https://proofbridge.nl/", "https://proofbridge.nl/agents/", "https://proofbridge.nl/agents/index.md", "https://proofbridge.nl/llms.txt", "https://proofbridge.nl/offer.json", "https://proofbridge.nl/index.md"]
open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{C['updated']}</lastmod></url>\n" for u in urls) + "</urlset>\n")

import re
txt = re.sub(r'<script.*?</script>', '', page[page.index('<body>'):], flags=re.S); txt = re.sub(r'<[^>]+>', ' ', txt)
print("visible words:", len(html.unescape(txt).split()), "| record:", record)
