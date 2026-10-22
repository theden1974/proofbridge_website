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
    rep = {'__TITLE__': E(A['title']), '__LEAD__': E(A['lead']), '__LD__': json.dumps(ld, ensure_ascii=False), '__CSS__': css, '__STATUS__': E(A['status']),
           '__SCRIPT_VERSION__': E(A['script_version']), '__DOOR_TELL__': E(A['doors']['tell']), '__DOOR_CHAT__': E(A['doors']['chat']), '__CHAT_LEAD__': E(A['chat_lead']),
           '__CHAT_PLACEHOLDER__': E(A['chat_placeholder']), '__CHAT_READ__': E(A['chat_read']), '__FIRST_PROMPT__': E(A['first_prompt']), '__INPUT_PLACEHOLDER__': E(A['input_placeholder']),
           '__SEND_TURN__': E(A['send_turn']), '__HEARD_LABEL__': E(A['heard_label']), '__HEARD_NOTE__': E(A['heard_note']), '__CONFIRM__': E(A['confirm']), '__FIX__': E(A['fix']),
           '__COLLECTED__': E(A['collected_label']), '__OPEN__': E(A['open_label']), '__CHUNKS_JSON__': json.dumps(A['chunks'], ensure_ascii=False), '__OBJECTS_JSON__': json.dumps(A['objects'], ensure_ascii=False),
           '__TURNS_JSON__': json.dumps(A['turns'], ensure_ascii=False), '__STEP2_LABEL__': E(A['step2_label']), '__EMAIL_LABEL__': E(A['email_label']), '__TIERS_LABEL__': E(A['tiers_label']),
           '__T1__': E(C['tier1_human']), '__T1S__': fmt(t1), '__T1G__': E(C['tier1_gets']), '__T2__': E(C['tier2_human']), '__T2S__': fmt(t2), '__T2G__': E(C['tier2_gets']),
           '__DL__': E(A['deadline_label']), '__DLH__': E(A['deadline_hint']), '__SEND__': E(A['send_label']), '__COPY__': E(A['copy_label']), '__SEND_NOTE__': E(A['send_note']), '__MAIL__': mail, '__AFTER__': E(A['after']),
           '__CONTRACT_LINE__': E(A['contract_line']).replace('the task contract', '<a href="/agents/">the task contract</a>')}
    for k, v in rep.items(): tpl = tpl.replace(k, v)
    os.makedirs(f"{OUT}/ask", exist_ok=True)
    open(f"{OUT}/ask/index.html", "w", encoding="utf-8").write(tpl)
    return tpl
