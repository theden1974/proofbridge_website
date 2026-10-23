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
           '__SCRIPT_VERSION__': E(A['script_version']), '__DOOR_TELL__': E(A['doors']['tell']), '__DOOR_CHAT__': E(A['doors']['chat']), '__DOOR_BACK__': E(A['doors']['back']), '__CHAT_LEAD__': E(A['chat_lead']),
           '__CHAT_PLACEHOLDER__': E(A['chat_placeholder']), '__PROMPT1__': E(A['prompt1']), '__BOX_HINT__': E(A['box_hint']), 
           '__SK_INTRO__': E(A['sidekick']['intro']), '__SK_PRESENTED__': E(A['sidekick']['presented']), '__SK_UNDERNEATH__': E(A['sidekick']['underneath']), '__SK_YES__': E(A['sidekick']['yes']), '__SK_NO__': E(A['sidekick']['no']), '__SK_THANKS_YES__': E(A['sidekick']['thanks_yes']), '__SK_THANKS_NO__': E(A['sidekick']['thanks_no']), '__SK_QUESTION__': E(A['sidekick']['question']), '__SK_ASK_INTRO__': E(A['sidekick']['ask_intro']), '__SK_ASK_PLAN__': E(A['sidekick']['ask_plan']), '__SK_ASK_PEOPLE__': E(A['sidekick']['ask_people']), '__SK_ASK_EFFECT__': E(A['sidekick']['ask_effect']), '__SK_ASK_THANKS__': E(A['sidekick']['ask_thanks']), '__SK_CORRECT__': E(A['sidekick']['correct_prompt']), 
           '__FLOOR_JSON__': json.dumps(A['floor'], ensure_ascii=False), '__EMAIL_LABEL__': E(A['email_label']), '__SEND__': E(A['send_label']), '__COPY__': E(A['copy_label']), '__SEND_NOTE__': E(A['send_note']), '__MAIL__': mail,
           '__CONTRACT_LINE__': E(A['contract_line']).replace('the task contract', '<a href="/agents/">the task contract</a>')}
    for k, v in rep.items(): tpl = tpl.replace(k, v)
    os.makedirs(f"{OUT}/ask", exist_ok=True)
    open(f"{OUT}/ask/index.html", "w", encoding="utf-8").write(tpl)
    return tpl
