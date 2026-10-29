# proofbridge.nl/ledger/ (draft, noindex), v3: the interactiondesign observation shape, more extensive. His go 2026-10-29 21:43.
import json, html, os
SRC = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(SRC)
N = json.load(open(os.path.join(SRC, 'ledger-observations.json'), encoding='utf-8')); E = html.escape
def obs(o):
    s, c = o['sample'], o['comes_back']
    return ('<article class="obs">\n  <span class="label">↳ ' + E(o['move']) + '</span>\n  <h2>' + E(o['headline']) + '</h2>\n'
      '  <div class="sample"><p class="lead">' + E(s['lead_in']) + '</p><blockquote>' + E(s['line']) + '<cite>' + E(s['who']) + ', ' + E(s['talk']) + '</cite></blockquote></div>\n'
      '  <p class="reading">' + E(o['reading']) + '</p>\n'
      '  <div class="sample back"><span class="label">↳ it comes back</span><p class="lead">' + E(c['lead_in']) + '</p><blockquote>' + E(c['line']) + '<cite>' + E(c['who']) + ', ' + E(c['talk']) + '</cite></blockquote><p>' + E(c['same_move']) + '</p></div>\n'
      '  <p class="src label">Source: ' + E(o['source']) + '</p>\n</article>\n')
C = N['cta']
css = '''
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root { --paper: hsl(45, 20%, 96%); --ink: #111014; --grey: hsl(240, 6%, 42%); --line: hsl(45, 10%, 86%); --accent: #b8862b;
    --s-1: clamp(0.8rem, 0.76rem + 0.2vw, 0.9rem); --s0: clamp(1rem, 0.95rem + 0.25vw, 1.15rem); --s1: clamp(1.25rem, 1.19rem + 0.31vw, 1.5rem); --s3: clamp(1.6rem, 1.3rem + 1.3vw, 2.4rem);
    --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace; }
  body { background: var(--paper); color: var(--ink); font-family: "DM Sans", system-ui, sans-serif; font-weight: 300; font-size: var(--s0); line-height: 1.6; }
  .wrap { max-width: 44rem; margin: 0 auto; padding: 3rem max(16px, env(safe-area-inset-left)) 5rem max(16px, env(safe-area-inset-right)); display: grid; gap: 3.5rem; }
  .label { font-family: var(--mono); font-size: var(--s-1); text-transform: uppercase; letter-spacing: 0.06em; color: var(--grey); display: block; }
  h1 { font-size: var(--s3); font-weight: 500; line-height: 1.15; text-wrap: balance; }
  h2 { font-size: var(--s3); font-weight: 500; line-height: 1.15; text-wrap: balance; margin: .4rem 0 1.2rem; }
  .obs { display: grid; gap: 1.1rem; padding-top: 2.2rem; border-top: 1px solid var(--line); }
  .sample { display: grid; gap: .6rem; }
  .lead { color: var(--grey); }
  blockquote { border-left: 2px solid var(--accent); padding-left: 1rem; font-size: var(--s1); font-weight: 500; line-height: 1.35; }
  blockquote cite { display: block; font-style: normal; font-family: var(--mono); font-size: var(--s-1); color: var(--grey); font-weight: 400; margin-top: .4rem; }
  .reading { font-size: var(--s0); max-width: 62ch; }
  .back { padding-top: .6rem; }
  .src { margin-top: .4rem; }
  .cta { border-top: 2px solid var(--ink); padding-top: 2rem; display: grid; gap: 1rem; }
  .cta p { max-width: 62ch; }
  .btn { font: inherit; font-family: var(--mono); font-size: var(--s-1); text-transform: uppercase; letter-spacing: 0.06em; background: var(--ink); color: var(--paper); border-radius: 2rem; padding: 0.8rem 1.3rem; text-decoration: none; display: inline-block; justify-self: start; }
  a { color: var(--ink); }
'''
page = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>The record · proofbridge</title>\n<meta name="robots" content="noindex, nofollow">\n<meta name="description" content="What people say, and what sits under it, heard by someone with the experience to hear it.">\n'
  '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500&family=IBM+Plex+Mono&display=swap" rel="stylesheet">\n<style>' + css + '</style>\n</head>\n<body>\n<div class="wrap">\n'
  '<header>\n  <span class="label">proofbridge · Dennis Jansen</span>\n  <h1>People say one thing. Something else is going on underneath. Someone with the experience hears it.</h1>\n</header>\n\n'
  + ''.join(obs(o) for o in N['observations']) +
  '<section class="cta">\n  <h2>' + E(C['heading']) + '</h2>\n  <p>' + E(C['text']) + '</p>\n  <a class="btn" href="' + E(C['link']) + '">Hand it over</a>\n</section>\n</div>\n</body>\n</html>\n')
os.makedirs(os.path.join(OUT, 'ledger'), exist_ok=True)
open(os.path.join(OUT, 'ledger', 'index.html'), 'w', encoding='utf-8').write(page); print('ledger/index.html', len(page))
