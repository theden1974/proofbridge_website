# /ask/ : the human door (prototype). His intake in his order (src/ask.json); mechanical pre-scan in the page, same three slots as the pre-scan test's key.
# Called from build.py with the shared names (C, A-file path, page css, E, fmt, t1, t2, mail, OUT, SRC).
import json, os
def build_ask(C, page, E, fmt, t1, t2, mail, OUT, SRC):
    A = json.load(open(os.path.join(SRC, 'ask.json'), encoding='utf-8'))
    css = page[page.index('<style>'):page.index('</style>')+8]
    ld = {"@context": "https://schema.org", "@type": "WebPage", "url": "https://proofbridge.nl/ask/",
          "name": f"{A['title']} · proofbridge", "dateModified": C['updated'], "description": A['lead'],
          "isPartOf": {"@type": "WebSite", "url": "https://proofbridge.nl/"}}
    tpl = open(os.path.join(SRC, 'ask.template.html'), encoding='utf-8').read()
    li = lambda xs: "".join(f"<li>{E(x)}</li>" for x in xs)
    rep = {'__TITLE__': E(A['title']), '__LEAD__': E(A['lead']), '__LD__': json.dumps(ld, ensure_ascii=False), '__CSS__': css, '__STATUS__': E(A['status']),
           '__SCRIPT_VERSION__': E(A['script_version']), '__DOOR_TELL__': E(A['doors']['tell']), '__DOOR_CHAT__': E(A['doors']['chat']), '__CHAT_LEAD__': E(A['chat_lead']),
           '__CHAT_PLACEHOLDER__': E(A['chat_placeholder']), '__PROMPT1__': E(A['prompt1']), '__PROMPT2__': E(A['prompt2']), '__BOX_HINT__': E(A['box_hint']),
           '__GUIDE_LABEL__': E(A['guide_label']), '__GUIDE_NOTE__': E(A['guide_note']), '__GUIDE_JSON__': json.dumps(A['guide'], ensure_ascii=False), '__THEN_LABEL__': E(A['then_label']), '__THEN_LINES__': li(A['then_lines']),
           '__FLOOR_JSON__': json.dumps(A['floor'], ensure_ascii=False), '__EMAIL_LABEL__': E(A['email_label']), '__SEND__': E(A['send_label']), '__COPY__': E(A['copy_label']), '__SEND_NOTE__': E(A['send_note']), '__MAIL__': mail,
           '__CONTRACT_LINE__': E(A['contract_line']).replace('the task contract', '<a href="/agents/">the task contract</a>')}
    for k, v in rep.items(): tpl = tpl.replace(k, v)
    os.makedirs(f"{OUT}/ask", exist_ok=True)
    open(f"{OUT}/ask/index.html", "w", encoding="utf-8").write(tpl)
    return tpl
