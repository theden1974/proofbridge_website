# /ask/ : the human door (prototype). His intake in his order (src/ask.json); mechanical pre-scan in the page, same three slots as the pre-scan test's key.
# Called from build.py with the shared names (C, A-file path, page css, E, fmt, t1, t2, mail, OUT, SRC).
import json, os
def build_ask(C, page, E, fmt, t1, t2, mail, OUT, SRC):
    A = json.load(open(os.path.join(SRC, 'ask.json'), encoding='utf-8'))
    css = page[page.index('<style>'):page.index('</style>')+8]
    def field_html(f):
        if f['rows'] == 1:
            ctl = f'<input type="text" id="{f["id"]}" name="{f["id"]}" data-slot="{f["slot"]}">'
        else:
            ctl = f'<textarea rows="{f["rows"]}" id="{f["id"]}" name="{f["id"]}" data-slot="{f["slot"]}"></textarea>'
        return f'<label for="{f["id"]}"><b>{E(f["label"])}</b><small>{E(f["hint"])}</small>\n{ctl}</label>'
    ld = {"@context": "https://schema.org", "@type": "WebPage", "url": "https://proofbridge.nl/ask/",
          "name": f"{A['title']} · proofbridge", "dateModified": C['updated'], "description": A['lead'],
          "isPartOf": {"@type": "WebSite", "url": "https://proofbridge.nl/"}}
    tpl = open(os.path.join(SRC, 'ask.template.html'), encoding='utf-8').read()
    rep = {'__TITLE__': E(A['title']), '__LEAD__': E(A['lead']), '__LD__': json.dumps(ld, ensure_ascii=False), '__CSS__': css,
           '__STATUS__': E(A['status']), '__FIELDS__': "\n".join(field_html(f) for f in A['fields']), '__TIERS_LABEL__': E(A['tiers_label']),
           '__T1__': E(C['tier1_human']), '__T1S__': fmt(t1), '__T1G__': E(C['tier1_gets']), '__T2__': E(C['tier2_human']), '__T2S__': fmt(t2), '__T2G__': E(C['tier2_gets']),
           '__DL__': E(A['deadline_label']), '__DLH__': E(A['deadline_hint']), '__CHECK_LABEL__': E(A['check_label']), '__CHECK_NOTE__': E(A['check_note']),
           '__SEND__': E(A['send_label']), '__COPY__': E(A['copy_label']), '__SEND_NOTE__': E(A['send_note']), '__MAIL__': mail, '__AFTER__': E(A['after']),
           '__CONTRACT_LINE__': E(A['contract_line']).replace('the task contract', '<a href="/agents/">the task contract</a>'),
           '__SLOTS_JSON__': json.dumps(A['slots'], ensure_ascii=False), '__ROUTES_JSON__': json.dumps(A['routes'], ensure_ascii=False)}
    for k, v in rep.items(): tpl = tpl.replace(k, v)
    os.makedirs(f"{OUT}/ask", exist_ok=True)
    open(f"{OUT}/ask/index.html", "w", encoding="utf-8").write(tpl)
    return tpl
