# proofbridge.nl/ledger/ (draft, noindex). v2 per his 21:16 and 21:22: public captures only, each with context, quotes, reasoning, why in the record; counts as footnote; the hand-over as the one call to action at the end.
import json, html, os, datetime
SRC = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(SRC)
L = json.load(open(os.path.join(SRC, 'ledger.json'), encoding='utf-8'))
N = json.load(open(os.path.join(SRC, 'ledger-entries.json'), encoding='utf-8')); E = html.escape
DOT = ' · '
def entry(e):
    cs = ''
    for c in e['shown_in']:
        qs = ''.join('<li><span class="who">' + E(q['who']) + ((DOT + E(q['at'])) if q.get('at') else '') + '</span><q>' + E(q['text']) + '</q></li>' for q in c['quotes'])
        cs += ('<div class="cap">\n  <p class="src">' + E(c['source']) + DOT + 'captured ' + E(c['captured']) + '</p>\n  <p>' + E(c['context']) + '</p>\n  <ul class="qs">' + qs + '</ul>\n  <p>' + E(c['what_it_shows']) + '</p>\n  <p class="why"><span class="label">why it is in the record</span>' + E(c['why_in_the_record']) + '</p>\n</div>\n')
    return '<article class="entry">\n  <h2>' + E(e['name']) + '</h2>\n  <p class="stands">' + E(e['stands_for']) + '</p>\n' + cs + '  <p class="foot">' + E(e['comes_back']) + '</p>\n</article>\n'
entries = ''.join(entry(e) for e in N['entries']); C = N['cta']; sp = L['captures_span']
today = datetime.date.today().isoformat()
lede = ('Dennis Jansen records how people see what is going on under what is said: in talks, interviews and recorded conversations, kept as they were spoken. A way of seeing counts when it comes back, said by different people in different fields who never heard of each other. Below, '
        + str(len(N['entries'])) + ' of them, each shown in two public talks, with the words, where they sit, and the reasoning from the words to the pattern, so you can check each step. The record runs from ' + E(sp['first_date']) + ' to ' + E(sp['last_date']) + ' and grows with every recording that goes in; private conversations are in it but not on this page.')
css = '''
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root { --paper: hsl(45, 20%, 96%); --ink: #111014; --grey: hsl(240, 6%, 42%); --line: hsl(45, 10%, 86%); --accent: #b8862b;
    --s-1: clamp(0.8rem, 0.76rem + 0.2vw, 0.9rem); --s0: clamp(1rem, 0.95rem + 0.25vw, 1.15rem); --s1: clamp(1.25rem, 1.19rem + 0.31vw, 1.5rem); --s3: clamp(1.7rem, 1.4rem + 1.2vw, 2.4rem);
    --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace; }
  body { background: var(--paper); color: var(--ink); font-family: "DM Sans", system-ui, sans-serif; font-weight: 300; font-size: var(--s0); line-height: 1.6; }
  .wrap { max-width: 44rem; margin: 0 auto; padding: 3rem max(16px, env(safe-area-inset-left)) 5rem max(16px, env(safe-area-inset-right)); display: grid; gap: 3rem; }
  .label { font-family: var(--mono); font-size: var(--s-1); text-transform: uppercase; letter-spacing: 0.06em; color: var(--grey); display: block; margin-bottom: .3rem; }
  h1 { font-size: var(--s3); font-weight: 500; line-height: 1.15; text-wrap: balance; margin-bottom: 1rem; }
  h2 { font-size: var(--s1); font-weight: 500; }
  .lede p { max-width: 62ch; }
  .entry { display: grid; gap: 1.2rem; padding-top: 2rem; border-top: 1px solid var(--line); }
  .stands { font-weight: 500; }
  .cap { display: grid; gap: .8rem; padding-left: 1rem; border-left: 2px solid var(--accent); }
  .src { font-family: var(--mono); font-size: var(--s-1); color: var(--grey); }
  .qs { list-style: none; display: grid; gap: .5rem; } .qs li { display: grid; gap: .1rem; }
  .qs .who { font-family: var(--mono); font-size: var(--s-1); color: var(--grey); } .qs q { font-weight: 500; }
  .why { font-size: var(--s-1); color: var(--grey); }
  .foot { font-family: var(--mono); font-size: var(--s-1); color: var(--grey); }
  .cta { border-top: 2px solid var(--ink); padding-top: 2rem; display: grid; gap: 1rem; }
  .btn { font: inherit; font-family: var(--mono); font-size: var(--s-1); text-transform: uppercase; letter-spacing: 0.06em; background: var(--ink); color: var(--paper); border-radius: 2rem; padding: 0.8rem 1.3rem; text-decoration: none; display: inline-block; justify-self: start; }
  .muted { color: var(--grey); font-size: var(--s-1); }
  a { color: var(--ink); }
'''
page = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>The record · proofbridge</title>\n<meta name="robots" content="noindex, nofollow">\n<meta name="description" content="Patterns that came back over time, shown in public talks, with the reasoning. Draft.">\n'
  '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500&family=IBM+Plex+Mono&display=swap" rel="stylesheet">\n<style>' + css + '</style>\n</head>\n<body>\n<div class="wrap">\n'
  '<header class="lede">\n  <span class="label">proofbridge' + DOT + 'the record' + DOT + 'draft, ' + today + '</span>\n  <h1>Patterns that came back</h1>\n  <p>' + lede + '</p>\n</header>\n\n' + entries +
  '<section class="cta">\n  <h2>' + E(C['heading']) + '</h2>\n  <p>' + E(C['text']) + '</p>\n  <a class="btn" href="' + E(C['link']) + '">Hand it over</a>\n</section>\n\n'
  '<footer><p class="muted">Draft, not linked, not indexed. Every quote is from the published talk named beside it; the counts are read from the record, not written by hand.</p></footer>\n</div>\n</body>\n</html>\n')
os.makedirs(os.path.join(OUT, 'ledger'), exist_ok=True)
open(os.path.join(OUT, 'ledger', 'index.html'), 'w', encoding='utf-8').write(page)
print('ledger/index.html', len(page))
