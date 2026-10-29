# proofbridge.nl/ledger/ (draft, noindex). His line 2026-10-29 20:53 and 20:57: the record of patterns, the ledger, raw into the studio, samples that come back.
import json, html, os, datetime
SRC = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(SRC)
L = json.load(open(os.path.join(SRC, 'ledger.json'), encoding='utf-8')); E = html.escape
HIS = "It is the record of patterns that are recognised over time validated by an ever growing source of material that is added through event transcriptions, interviews and reviews of video content. All raw all ready for remastering once the underlying intelligence and reasoning matures."
HIS2 = "Its the ledger, all input is raw but goes into the studio. It's like the recognisable samples of old music that come back in new music releases, you recognise the sample from the original but in a new composition."
def short(s, n=15):
    w = s.split(); return s if len(w) <= n else ' '.join(w[:n]) + ' [...]'
rows = ''
for p in L['patterns']:
    ids = ', '.join(p['capture_ids']) if p['capture_ids'] else 'none yet'
    note = f'<p class="note">{E(p["note"])}</p>' if p.get('note') else ''
    rows += f'''<li class="row">
  <div class="head"><h3>{E(p['name'])}</h3><span class="tier">{E(p['tier_plain'])}</span></div>
  <p>{E(p['stands_for'])}</p>
  <dl><dt>comes back in</dt><dd>{p['captures']} captures{', ' + str(p['domains']) + ' fields' if p['domains'] else ''}</dd>
  <dt>since</dt><dd>{E(p['first_date'] or 'no dated capture')}</dd><dt>last counted</dt><dd>{E(p['recomputed'])}</dd></dl>
  <details><summary>the captures</summary><p class="ids">{E(ids)}</p></details>{note}
</li>
'''
S = L['sample']; sp = L['captures_span']
page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The ledger · proofbridge</title>
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="The record of patterns recognised over time, with their counts and sources. Draft.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500&family=IBM+Plex+Mono&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{ --paper: hsl(45, 20%, 96%); --ink: #111014; --grey: hsl(240, 6%, 42%); --line: hsl(45, 10%, 86%); --accent: #b8862b;
    --s-1: clamp(0.8rem, 0.76rem + 0.2vw, 0.9rem); --s0: clamp(1rem, 0.95rem + 0.25vw, 1.15rem); --s1: clamp(1.25rem, 1.19rem + 0.31vw, 1.5rem); --s3: clamp(1.7rem, 1.4rem + 1.2vw, 2.4rem);
    --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace; }}
  body {{ background: var(--paper); color: var(--ink); font-family: "DM Sans", system-ui, sans-serif; font-weight: 300; font-size: var(--s0); line-height: 1.55; }}
  .wrap {{ max-width: 46rem; margin: 0 auto; padding: 3rem max(16px, env(safe-area-inset-left)) 5rem max(16px, env(safe-area-inset-right)); display: grid; gap: 2.4rem; }}
  .label {{ font-family: var(--mono); font-size: var(--s-1); text-transform: uppercase; letter-spacing: 0.06em; color: var(--grey); }}
  h1 {{ font-size: var(--s3); font-weight: 500; line-height: 1.15; text-wrap: balance; }}
  h2 {{ font-size: var(--s1); font-weight: 500; margin-bottom: .6rem; }}
  h3 {{ font-size: var(--s0); font-weight: 500; }}
  blockquote {{ border-left: 2px solid var(--accent); padding-left: 1rem; font-size: var(--s1); font-weight: 300; }}
  blockquote cite {{ display: block; font-style: normal; font-family: var(--mono); font-size: var(--s-1); color: var(--grey); margin-top: .5rem; }}
  ul {{ list-style: none; }}
  .row {{ padding: 1rem 0; border-top: 1px solid var(--line); display: grid; gap: .5rem; }}
  .head {{ display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; flex-wrap: wrap; }}
  .tier {{ font-family: var(--mono); font-size: var(--s-1); color: var(--accent); }}
  dl {{ display: grid; grid-template-columns: max-content 1fr; gap: .15rem 1rem; font-size: var(--s-1); }} dt {{ color: var(--grey); font-family: var(--mono); }}
  details summary {{ cursor: pointer; font-family: var(--mono); font-size: var(--s-1); color: var(--grey); }}
  .ids {{ font-family: var(--mono); font-size: var(--s-1); color: var(--grey); margin-top: .3rem; overflow-wrap: anywhere; }}
  .note {{ font-size: var(--s-1); color: var(--grey); }}
  .sample {{ border: 1px solid var(--line); padding: 1.2rem; display: grid; gap: .9rem; }}
  .sample .q {{ font-size: var(--s0); }} .sample .src {{ font-family: var(--mono); font-size: var(--s-1); color: var(--grey); }}
  p.muted {{ color: var(--grey); font-size: var(--s-1); }}
  a {{ color: var(--ink); }}
  @media (max-width: 520px) {{ dl {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <span class="label">proofbridge · the ledger · draft, {datetime.date.today().isoformat()}</span>
  <h1>The record of patterns recognised over time</h1>
</header>
<blockquote>{E(HIS)}<cite>Dennis Jansen, 2026-10-29</cite></blockquote>

<section>
  <h2>What is in the record</h2>
  <p>{len(L['patterns'])} patterns, counted over {E(sp['first_id'])} to {E(sp['last_id'])}: captures from {E(sp['first_date'])} to {E(sp['last_date'])}, made from {E(', '.join(L['sources']['kinds']))}. {E(L['sources']['private_kept_out'].capitalize())}. Last counted {E(L['ledger_recomputed'])}.</p>
  <p class="muted">Each pattern is a way of seeing that came back often enough, in enough places, to count. The tiers are borrowed from music: a jazz riff is heard once; a songwriter draft is written down; a band arrangement is played by more than one; a hit comes back on its own.</p>
</section>

<section>
  <h2>The ledger</h2>
  <ul>
{rows}  </ul>
</section>

<section>
  <h2>A sample that came back</h2>
  <blockquote>{E(HIS2)}<cite>Dennis Jansen, 2026-10-29</cite></blockquote>
  <div class="sample">
    <span class="label">{E(L['patterns'][[p['internal'] for p in L['patterns']].index(S['pattern'])]['name'])}</span>
    <p class="q">“{E(short(S['original']['line']))}”</p><p class="src">{E(S['original']['source'])} · capture {E(S['original']['capture'])} · {E(S['original']['date'])}</p>
    <p class="q">“{E(short(S['later']['line']))}”</p><p class="src">{E(S['later']['source'])} · capture {E(S['later']['capture'])} · {E(S['later']['date'])}{(' · at ' + E(S['later']['at'])) if S['later'].get('at') else ''}</p>
    <p>{E(S['what_comes_back'])}</p>
  </div>
</section>

<section>
  <h2>The studio</h2>
  <p>All input is raw and stays raw: the transcript, the interview, the video review as it was. It goes into the studio, where it is read against the ledger. What comes out is a reading, marked as a reading, and counted only once it is used. The raw is kept for remastering when the intelligence and reasoning underneath mature.</p>
</section>

<section>
  <h2>Bring material</h2>
  <p>A transcript, an interview, a recorded talk. It enters raw. What comes back is where it meets the ledger: the moments, as they were said, and what sits under them. <a href="/ask/">Hand it over</a>.</p>
</section>

<footer><p class="muted">Draft page, not linked, not indexed. Every number above is read from the ledger in the record (bundle {E(L['bundle_head'])}); nothing is written by hand.</p></footer>
</div>
</body>
</html>
'''
os.makedirs(os.path.join(OUT, 'ledger'), exist_ok=True)
open(os.path.join(OUT, 'ledger', 'index.html'), 'w', encoding='utf-8').write(page)
print('ledger/index.html', len(page))
