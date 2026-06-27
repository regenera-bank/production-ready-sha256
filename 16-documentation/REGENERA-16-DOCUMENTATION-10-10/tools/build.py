from common import *
from html import escape
from pathlib import PurePosixPath
import json, re, shutil

def rewrite_target(target, output_rel):
    if target.startswith(('http://','https://','mailto:')):
        return target
    filepart, sep, anchor = target.partition('#')
    prefix = '../' * (len(output_rel.parts) - 1)
    if filepart.endswith('.md'):
        filepart = filepart[:-3] + '.html'
    elif filepart.endswith('registry/documents.json'):
        filepart = prefix + 'data/documents.json'
    return filepart + (sep + anchor if sep else '')

def render_markdown(body, output_rel):
    out=[]; in_code=False; code=[]; lang=''
    for line in body.splitlines():
        if line.startswith('```'):
            if not in_code:
                in_code=True; lang=line[3:].strip(); code=[]
            else:
                out.append(f'<pre data-language="{escape(lang)}"><code>{escape(chr(10).join(code))}</code></pre>')
                in_code=False
            continue
        if in_code:
            code.append(line); continue
        if line.startswith('### '): out.append(f'<h3>{escape(line[4:])}</h3>')
        elif line.startswith('## '): out.append(f'<h2>{escape(line[3:])}</h2>')
        elif line.startswith('# '): out.append(f'<h1>{escape(line[2:])}</h1>')
        elif line.startswith('- '): out.append(f'<p class="item">• {escape(line[2:])}</p>')
        elif line.startswith('|'): out.append(f'<pre class="table">{escape(line)}</pre>')
        elif not line.strip(): out.append('')
        else:
            txt=escape(line)
            txt=re.sub(
                r'\[([^]]+)\]\(([^)]+)\)',
                lambda m: f'<a href="{escape(rewrite_target(m.group(2), output_rel))}">{escape(m.group(1))}</a>',
                txt,
            )
            out.append(f'<p>{txt}</p>')
    return '\n'.join(out)

def main():
    if GENERATED.exists(): shutil.rmtree(GENERATED)
    (GENERATED/'site').mkdir(parents=True)
    records=[]
    for p in canonical_docs():
        meta,body=parse_front_matter(p)
        rel=p.relative_to(DOC_ROOT).with_suffix('.html')
        dest=GENERATED/'site'/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        prefix='../'*(len(rel.parts)-1)
        css=prefix+'assets/site.css'
        html="<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{title}</title><link rel=\"stylesheet\" href=\"{css}\"></head><body><main>{body}</main></body></html>".format(title=escape(meta['title']),css=css,body=render_markdown(body,rel))
        dest.write_text(html+'\n',encoding='utf-8',newline='\n')
        records.append({**meta,'path':str(p.relative_to(ROOT)),'sha256':sha256(p),'html':str(rel)})
    css="body{font-family:system-ui,sans-serif;max-width:980px;margin:0 auto;padding:32px;line-height:1.55;background:#07111f;color:#e8f0f8}a{color:#78c7ff}pre{white-space:pre-wrap;background:#0d1b2a;padding:16px;border-radius:8px}.table{padding:4px 12px}.item{margin:.25rem 0}h1,h2,h3{color:#fff}"
    (GENERATED/'site/assets').mkdir(parents=True,exist_ok=True)
    (GENERATED/'site/assets/site.css').write_text(css+'\n',encoding='utf-8',newline='\n')
    records=sorted(records,key=lambda x:x['id'])
    slim=[{k:r[k] for k in ['id','title','owner','reviewers','status','version','classification','last_reviewed','next_review_due','source_of_truth','path','sha256']} for r in records]
    json_dump(ROOT/'registry/documents.json',slim)
    (GENERATED/'site/data').mkdir(parents=True,exist_ok=True)
    json_dump(GENERATED/'site/data/documents.json',slim)
    json_dump(GENERATED/'search-index.json',[{'id':r['id'],'title':r['title'],'path':r['html'],'status':r['status'],'classification':r['classification']} for r in records])
    json_dump(GENERATED/'build-summary.json',{'documents':len(records),'site_files':len([p for p in (GENERATED/'site').rglob('*') if p.is_file()]),'status':'PASS'})
    print(json.dumps({'status':'PASS','documents':len(records)},ensure_ascii=False))
if __name__=='__main__': main()
