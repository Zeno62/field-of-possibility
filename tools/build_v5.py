#!/usr/bin/env python3
"""Build v5.0 publication assets from two exact, author-approved Git blobs.

No philosophical text is rewritten. Only candidate front matter is replaced.
All generated formats derive from the same body, with auditable checksums.
"""
from __future__ import annotations
import argparse, base64, hashlib, html, json, os, re, shutil, subprocess, sys, unicodedata, urllib.request, zipfile
from pathlib import Path
from urllib.parse import urlparse, unquote
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup
from weasyprint import HTML
import fitz
from PIL import Image, ImageDraw

REPO = 'Zeno62/field-of-possibility'
BASE = '/field-of-possibility/'
SITE = 'https://zeno62.github.io' + BASE
VERSION = '5.0.0'
DATE = '2026-09-08'
SOURCES = {'zh-Hans':'2c0ec2ef2215d3c09dcb584d647ce0cf9dbf1c61','en':'0e39379ffc6ea7188401451d7b0b32496ffa1f77'}
MARKERS = {'zh-Hans':'## 创作说明','en':'## Note on the Writing Process'}
TITLES = {'zh-Hans':'可能性网络白皮书 v5.0 正式版','en':'Field of Possibility White Paper v5.0 — Official English Edition'}
MD = MarkdownIt('commonmark', {'html':False}).enable('table')
ROOT = Path.cwd()
WORK = ROOT / '.build-v5'
QA = WORK / 'qa'
CSS = '''
:root{color-scheme:light;--ink:#1c2e36;--muted:#66757b;--line:#d9e1e3;--accent:#245c68;--paper:#fafbf9}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:5rem}body{margin:0;color:var(--ink);background:var(--paper);font:17px/1.85 system-ui,-apple-system,BlinkMacSystemFont,'Noto Sans CJK SC',sans-serif}a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:3px}a:hover{color:#122e35}nav.top{display:flex;gap:1.4rem;align-items:center;flex-wrap:wrap;padding:1.1rem max(5vw,1rem);border-bottom:1px solid var(--line);background:white}.brand{font-weight:650;margin-right:auto}main{max-width:1060px;margin:auto;padding:2.5rem 1.3rem 5rem}.hero{padding:2rem 0 3rem}.kicker{font-size:.78rem;letter-spacing:.13em;text-transform:uppercase;color:var(--accent)}h1,h2,h3{line-height:1.4;letter-spacing:-.015em}h1{font-size:clamp(1.8rem,3.5vw,3rem)}h2{margin-top:2.3rem;font-size:1.5rem}h3{font-size:1.15rem}p{margin:.7rem 0 1rem}.sub{color:var(--muted);max-width:55rem}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(265px,1fr));gap:1.4rem}.card{padding:1.7rem;background:white;border:1px solid var(--line);border-radius:9px}.card h2{margin-top:0}.button{display:inline-block;margin:.25rem .55rem .35rem 0;border:1px solid var(--accent);padding:.45rem .85rem;border-radius:4px;text-decoration:none}.primary{background:var(--accent);color:white}.primary:hover{color:white;background:#173e47}.reader{max-width:820px}.reader article{font-family:Georgia,'Noto Serif CJK SC',serif;font-size:18px;line-height:1.95}.reader article h1{font-family:system-ui,'Noto Sans CJK SC',sans-serif;font-size:1.85rem;margin:4rem 0 1.6rem;padding-top:1.7rem;border-top:1px solid var(--line)}.reader article h2,.reader article h3{font-family:system-ui,'Noto Sans CJK SC',sans-serif}blockquote{border-left:3px solid var(--accent);padding:.4rem 1.25rem;margin:1.7rem 0;background:#f1f5f4}blockquote p{margin:.35rem 0}pre{padding:1.1rem;background:#edf2f3;border:1px solid var(--line);border-radius:4px;white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.8 'Noto Sans Mono','Noto Sans CJK SC',monospace}code{overflow-wrap:anywhere}hr{border:0;border-top:1px solid var(--line);margin:2.3rem 0}.toc{background:white;border:1px solid var(--line);padding:1rem 1.3rem;margin:1.5rem 0}.toc summary{cursor:pointer;font-weight:600}.toc ol{margin:.8rem 0}.toc li{margin:.3rem 0}table{width:100%;border-collapse:collapse}td,th{padding:.6rem;text-align:left;border-bottom:1px solid var(--line)}footer{font-size:.85rem;color:var(--muted);padding:2rem max(5vw,1rem);border-top:1px solid var(--line)}.fine{font-size:.85rem;color:var(--muted)}.reader a{overflow-wrap:anywhere}.retired{max-width:720px;margin:4rem auto}.pdf-cover,.pdf-toc{display:none}@media(max-width:600px){body{font-size:16px}nav.top{gap:.7rem}.brand{width:100%}.reader article{font-size:17px}main{padding-top:1.4rem}}
'''
PRINT = '''
@page{size:A4;margin:22mm 22mm 21mm;@top-left{content:'FIELD OF POSSIBILITY';font-family:'Noto Sans';font-size:8pt;color:#62747c;letter-spacing:.5pt}@top-right{content:'v5.0';font-family:'Noto Sans';font-size:8pt;color:#62747c}@bottom-left{content:'CC BY-NC-SA 4.0';font-family:'Noto Sans';font-size:7.5pt;color:#6b777c}@bottom-right{content:counter(page);font-family:'Noto Sans';font-size:8pt;color:#6b777c}}
@page:first{@top-left{content:none}@top-right{content:none}@bottom-left{content:none}@bottom-right{content:none}}
html{color:#182f38}body{font-family:'Noto Serif','Noto Serif CJK SC',serif;font-size:10.5pt;line-height:1.64;font-variant-ligatures:none}body.zh{font-family:'Noto Serif CJK SC','Noto Serif',serif;font-size:10.4pt;line-height:1.8}h1,h2,h3{font-family:'Noto Sans','Noto Sans CJK SC',sans-serif;font-weight:700;line-height:1.45;break-after:avoid}h1{font-size:21pt;margin:0 0 10mm;break-before:page;bookmark-level:1}h2{font-size:14pt;margin:7mm 0 3mm;bookmark-level:2}h3{font-size:11.8pt;margin:5mm 0 2mm;bookmark-level:3}p{margin:0 0 3mm;orphans:3;widows:3}strong{font-weight:700}blockquote{border-left:2pt solid #316570;margin:4mm 0;padding:2mm 0 1mm 5mm;color:#173e47;break-inside:avoid}blockquote p{margin:0 0 2mm}pre{font-family:'Noto Sans Mono','Noto Sans CJK SC',monospace;font-size:8.3pt;line-height:1.7;white-space:pre-wrap;overflow-wrap:anywhere;padding:3.5mm;background:#eff4f3;border:.4pt solid #d5e0df;margin:3mm 0 4mm;break-inside:avoid}a{color:#245c68;text-decoration:none;overflow-wrap:anywhere}hr{height:0;border:0;margin:4mm 0}ol,ul{padding-left:6mm}li{margin-bottom:2mm;orphans:3;widows:3}.pdf-cover{display:block;height:246mm;break-after:page;padding-top:40mm}.pdf-cover .eyebrow{font:10pt 'Noto Sans',sans-serif;letter-spacing:2pt;color:#316570}.pdf-cover h1{break-before:auto;font-size:34pt;line-height:1.4;bookmark-level:none;margin:12mm 0 9mm}.pdf-cover .edition{font:13pt/1.7 'Noto Sans','Noto Sans CJK SC',sans-serif;color:#4c626b}.pdf-cover .rule{height:1pt;background:#316570;width:35mm;margin:20mm 0 8mm}.pdf-cover .details{font:9pt/1.9 'Noto Sans','Noto Sans CJK SC',sans-serif;color:#62747c}.pdf-toc{display:block;break-after:page}.pdf-toc h1{break-before:auto;bookmark-level:none;font-size:22pt}.pdf-toc ol{list-style:none;padding:0}.pdf-toc li{margin:0 0 3mm;font:9.5pt/1.6 'Noto Sans','Noto Sans CJK SC',sans-serif}.pdf-toc a:after{content:leader('.') target-counter(attr(href),page)}article>h2:first-child{margin-top:0}article>h1:first-of-type{break-before:page}.refs{font-size:8.7pt;line-height:1.55}table{border-collapse:collapse;width:100%}td,th{border-bottom:.5pt solid #ddd;padding:2mm}
'''
TERMS = [
('纯粹可能性','Pure Possibility','能具化全量的本体性能；不是概率分布。'),('觉','Awareness','第一层术语，不与 consciousness 混用。'),('明性','Luminosity','不是一种视觉亮光或特殊体验。'),('唯一能知','the sole Knowing','不可分异，且别无第二本体；不是单个观察者。'),('全知','Total Knowing','不表示局部意识拥有所有知识。'),('所知','the known / what is known','所有可显现内容所属的一侧。'),('相','appearance / manifested appearance','不默认译为 illusion。'),('显化','manifestation','本体关系，不是时间中的制造。'),('可能性母网','Mother Field of Possibility','第二层全部关系与显化之相。'),('全量','Totality','不等于局部意识的全部见闻。'),('本体','ontological ground','不另设一个位于万物背后的对象。'),('意识','consciousness','第二层真实关系组织，仍属所知。'),('真实高约束意识子网','genuine high-constraint consciousness subnet','特定关系共同成立；不是计算所得概率。'),('意识像','consciousness-image','显化的意识组织。'),('模拟意识像','simulated consciousness-image','本书中普通 AI 的关系位置。'),('生命本质','essence of life','本书中指明性。'),('生命态','life-state','真实意识子网成立时的生命显化状态。'),('智能','intelligence','能力维度，不替代生命定义。'),('自我模型','self-model','组织经验的模型，不是最终能知。'),('假我','false self','所知模型被认作最终主体。'),('主体认同','subject-identification','将所知内容认作最终主体。'),('权重','Weight','既有关系使某些反应更易再次成立的倾向。'),('集体权重','Collective Weight','群体与制度等尺度的关系强化。'),('单帧中断','Single-Frame Interruption','当下辨认的方法；帧不是离散物理时间。'),('游戏三昧','Playful Samadhi','意识仍运行、执着显著松动的状态。'),('回归','Return','意识不断突破自我，并最终彻底解构。')]

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def gitsha(data:bytes)->str:return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def write(path:Path|str,text:str|bytes)->None:
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(text if isinstance(text,bytes) else text.encode('utf-8'))
def api_blob(blob:str)->bytes:
 token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
 headers={'Accept':'application/vnd.github+json','User-Agent':'field-of-possibility-v5-publisher'}
 if token:headers['Authorization']='Bearer '+token
 req=urllib.request.Request(f'https://api.github.com/repos/{REPO}/git/blobs/{blob}',headers=headers)
 with urllib.request.urlopen(req,timeout=60) as r:payload=json.load(r)
 data=base64.b64decode(payload['content']);assert gitsha(data)==blob,'Approved source hash mismatch'
 return data

def source(lang:str)->tuple[str,bytes]:
 p=WORK/f'approved-{lang}.md'
 if not p.exists():write(p,api_blob(SOURCES[lang]))
 raw=p.read_bytes();assert gitsha(raw)==SOURCES[lang]
 text=raw.decode('utf-8');start=text.index(MARKERS[lang]+'\n')
 body=text[start:];assert body.endswith('\n')
 assert re.findall(r'^# (\d+)｜',body,re.M)==[str(i) for i in range(14)]
 assert len(re.findall(r'^## Q\d+｜',body,re.M))==10
 assert re.findall(r'^## A\.(\d+)｜',body,re.M)==[str(i) for i in range(1,12)]
 return body,raw

def rendered(body:str)->tuple[str,list[tuple[str,str]]]:
 soup=BeautifulSoup(MD.render(body),'html.parser');toc=[];seq=0
 for h in soup.find_all(['h1','h2','h3']):
  label=h.get_text();match=re.match(r'(\d+)｜',label)
  if h.name=='h1' and match:key='chapter-'+match.group(1)
  elif h.name=='h1':key='appendix-a'
  else:seq+=1;key='section-'+str(seq)
  h['id']=key
  if h.name=='h1':toc.append((key,label))
 for node in list(soup.find_all(string=True)):
  if node.parent.name in ['a','code','pre']:continue
  value=str(node)
  if 'https://' not in value:continue
  parts=re.split(r'(https://[^\s<>]+)',value)
  for part in parts:
   if part.startswith('https://'):
    a=soup.new_tag('a',href=part);a.string=part;node.insert_before(a)
   elif part:node.insert_before(part)
  node.extract()
 ref=soup.find(lambda t:t.name=='h2' and ('References' in t.get_text() or '参考来源' in t.get_text()))
 if ref:
  following=ref.find_next_sibling('ol')
  if following:following['class']='refs'
 return str(soup),toc

def nav()->str:
 return f'<nav class="top"><a class="brand" href="{BASE}">Field of Possibility · 可能性网络</a><a href="{BASE}zh-Hans/official-v5.html">中文</a><a href="{BASE}en/official-v5.html">English</a><a href="{BASE}downloads.html">下载 / Downloads</a><a href="https://github.com/{REPO}">GitHub</a></nav>'
def page(title:str,content:str,lang='zh-Hans',reader=False,canonical='')->str:
 return f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="{BASE}assets/css/v5.css">'+(f'<link rel="canonical" href="{SITE}{canonical}">' if canonical else '')+f'</head><body>{nav()}<main'+(' class="reader"' if reader else '')+f'>{content}</main><footer>Field of Possibility / 可能性网络 · v5.0 · {DATE}<br>中文为源版本 · Chinese source edition with official English translation.<br><a href="https://github.com/{REPO}/blob/main/LICENSE.md">CC BY-NC-SA 4.0</a></footer></body></html>\n'
def toc_html(toc:list[tuple[str,str]],prefix='')->str:
 return '<ol>'+''.join(f'<li><a href="{prefix}#{k}">{html.escape(t)}</a></li>' for k,t in toc)+'</ol>'
def retired(dest:str)->str:
 return '<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url='+BASE+dest+'"><link rel="canonical" href="'+SITE+dest+'"><title>Read v5.0 · 阅读当前正式版</title></head><body><p>此阅读入口已迁移至 v5.0。This reading entry now points to v5.0.</p><p><a href="'+BASE+dest+'">阅读 v5.0 / Read v5.0</a></p></body></html>\n'
def zip_files(dest:Path,items:dict[str,bytes])->None:
 dest.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(items.items()):
   info=zipfile.ZipInfo(name,(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
   z.writestr(info,data)
 with zipfile.ZipFile(dest) as z:assert z.testzip() is None

def pdf_html(lang:str,body_html:str,toc:list[tuple[str,str]])->str:
 zh=lang=='zh-Hans';cover_title='可能性网络<br>白皮书' if zh else 'Field of<br>Possibility<br>White Paper'
 edition='v5.0 正式版 · 中文源版本' if zh else 'v5.0 · Official English Edition'
 return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{html.escape(TITLES[lang])}</title><meta name="author" content="Field of Possibility / Zeno62"><style>{PRINT}</style></head><body class="'+('zh' if zh else 'en')+'"><section class="pdf-cover"><div class="eyebrow">FIELD OF POSSIBILITY</div><h1>'+cover_title+'</h1><div class="edition">'+edition+'</div><div class="rule"></div><div class="details">'+DATE+'<br>Field of Possibility / 可能性网络<br>CC BY-NC-SA 4.0<br>'+SITE+'</div></section><section class="pdf-toc"><h1>'+('目录' if zh else 'Contents')+'</h1>'+toc_html(toc)+'</section><article>'+body_html+'</article></body></html>'

def normalize(t:str)->str:
 return ''.join(c for c in unicodedata.normalize('NFKC',t) if not c.isspace() and c not in '\u200b\u00ad\ufeff')
def inspect_pdf(lang:str,pdf:Path,body_html:str)->dict:
 doc=fitz.open(pdf);texts=[];bad=[];previews=[]
 for i,p in enumerate(doc):
  texts.append(p.get_text('text',clip=fitz.Rect(0,49,p.rect.width,p.rect.height-39)))
  for b in p.get_text('dict')['blocks']:
   for line in b.get('lines',[]):
    for s in line['spans']:
     x0,y0,x1,y1=s['bbox']
     if x0 < -0.5 or y0 < -0.5 or x1 > p.rect.width+.5 or y1 > p.rect.height+.5:bad.append([i+1,s['text'],s['bbox']])
  img=p.get_pixmap(matrix=fitz.Matrix(.38,.38),alpha=False)
  previews.append(Image.frombytes('RGB',[img.width,img.height],img.samples))
 full=normalize('\n'.join(texts));soup=BeautifulSoup(body_html,'html.parser');miss=[]
 for n in soup.find_all(['p','h1','h2','h3','li','pre']):
  if n.name=='li' and n.find('p'):continue
  text=normalize(n.get_text())
  if len(text)>8 and text not in full:miss.append(text[:160])
 if '\ufffd' in full:bad.append(['replacement-character'])
 QA.mkdir(parents=True,exist_ok=True)
 for start in range(0,len(previews),16):
  sheet=Image.new('RGB',(4*240,4*358),'#dde4e5');d=ImageDraw.Draw(sheet)
  for j,img in enumerate(previews[start:start+16]):
   x=(j%4)*240+6;y=(j//4)*358+22;sheet.paste(img,(x,y));d.text((x,y-16),f'{lang} / {start+j+1}',fill='black')
  sheet.save(QA/f'{lang}-contact-{start//16+1:02d}.png')
 selected={0,1,len(doc)-1}
 for i,text in enumerate(texts):
  if any(s in text for s in ['最短实操','The Shortest Practice','#unlikely#','最后，再看一眼','Finally, Look Once More','Q10｜','Q3｜']):selected.add(i)
  if i>1 and ('7｜权重' in text or '7｜Weight' in text or '2｜纯粹' in text or '2｜Pure' in text):selected.add(i)
 for i in sorted(selected):doc[i].get_pixmap(matrix=fitz.Matrix(1.45,1.45),alpha=False).save(QA/f'{lang}-page-{i+1:03d}.png')
 result={'pages':len(doc),'out_of_bounds_spans':bad,'paragraphs_not_found':miss,'sampled_full_pages':[i+1 for i in sorted(selected)],'toc_entries':len(doc.get_toc())}
 write(QA/f'{lang}-pdf-check.json',json.dumps(result,ensure_ascii=False,indent=2))
 if bad:raise RuntimeError(f'PDF content outside page or invalid characters: {lang}: {bad[:3]}')
 if miss:raise RuntimeError(f'PDF textual coverage failed: {lang}: {miss[:5]}')
 return result

def main()->None:
 parser=argparse.ArgumentParser();parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
 WORK.mkdir(exist_ok=True);QA.mkdir(exist_ok=True)
 inventory=subprocess.check_output(['git','ls-files'],text=True).splitlines()
 write(QA/'before-paths.json',json.dumps(inventory,indent=2))
 sources={};bodies={};renderings={};tocs={};manifest={'version':VERSION,'released':DATE,'default_edition':'5.0','historical_editions_in_navigation':False,'restore_historical_display_requires_author_authorization':True,'sources':{},'assets':{}}
 for lang in SOURCES:
  bodies[lang],sources[lang]=source(lang);renderings[lang],tocs[lang]=rendered(bodies[lang]);assert len(tocs[lang])==15
  manifest['sources'][lang]={'approved_source_git_blob':SOURCES[lang],'approved_body_sha256':sha(bodies[lang].encode())}
 if args.verify_only:
  known=json.loads(Path('releases/v5.0.0-manifest.json').read_text())
  for lang in SOURCES:assert known['sources'][lang]['approved_body_sha256']==manifest['sources'][lang]['approved_body_sha256']
  for path,d in known['assets'].items():assert sha(Path(path).read_bytes())==d['sha256'],path
  print(json.dumps({'verified_assets':len(known['assets']),'version':VERSION},indent=2));return
 removed=[]
 for p in Path('whitepaper').rglob('*'):
  if p.is_file() and ('v4.0' in p.name or 'chapters' in p.parts):removed.append(str(p));p.unlink()
 aliases=[]
 for lang in SOURCES:
  parent=Path('docs')/lang
  if parent.exists():
   for p in list(parent.rglob('*')):
    if p.is_file() and p.suffix in ['.md','.html']:
     dest=f'{lang}/official-v5.html';target=p.with_suffix('.html');aliases.append(str(target))
     if p!=target:p.unlink()
     write(target,retired(dest))
 for p in list(Path('docs').rglob('*')):
  if p.is_file() and ('v4.0' in p.name) and p.suffix in ['.pdf','.zip']:removed.append(str(p));p.unlink()
 docs=Path('docs');write(docs/'.nojekyll','');write(docs/'assets/css/v5.css',CSS)
 release_assets=[]
 for lang in SOURCES:
  body=bodies[lang];title=TITLES[lang];stem=f'field-of-possibility-whitepaper-v5.0-{lang}';root=Path('whitepaper')/lang
  fm=f'---\ntitle: {title}\nversion: "5.0.0"\nstatus: official\nlanguage: {lang}\nreleased: "{DATE}"\nlicense: CC-BY-NC-SA-4.0\nreviewed_body_sha256: {sha(body.encode())}\n---\n\n'
  note='中文为本书源版本；英文为同版官方对应译本。' if lang=='zh-Hans' else 'The Chinese edition is the source; this is its official English translation.'
  official=fm+'# '+title+'\n\n> '+note+'\n> CC BY-NC-SA 4.0 · '+SITE+'\n\n---\n\n'+body
  full=root/'full'/f'{stem}.md';write(full,official);release_assets.append(full)
  assert full.read_text().split(MARKERS[lang]+'\n',1)[1]==body.split(MARKERS[lang]+'\n',1)[1]
  heads=re.findall(r'^# (.+)$',body,re.M)
  obs_toc='## '+('目录' if lang=='zh-Hans' else 'Contents')+'\n\n'+'\n'.join('- [[#'+h+'|'+h+']]' for h in heads)+'\n\n---\n\n'
  obs=root/'obsidian'/f'{stem}-obsidian.md';write(obs,official.replace(body,obs_toc+body,1));release_assets.append(obs)
  chunks=re.split(r'(?m)(?=^# (?:\d+｜|附录 A｜|Appendix A｜))',body);assert len(chunks)==16;assert ''.join(chunks)==body
  zip_items={};index=['# '+title+' — '+('分章阅读' if lang=='zh-Hans' else 'Chapters'),'']
  for i,ch in enumerate(chunks):
   name='00-front-matter.md' if i==0 else (f'chapter-{i-1:02d}.md' if i<15 else 'appendix-a.md')
   write(root/'chapters'/name,ch);zip_items[name]=ch.encode();label=MARKERS[lang][3:] if i==0 else heads[i-1]
   index.append(f'- [{label}]({name})')
  write(root/'chapters/README.md','\n'.join(index)+'\n');zip_items['README.md']=('\n'.join(index)+'\n').encode();zip_items['LICENSE.md']=Path('LICENSE.md').read_bytes()
  package=root/'packages'/f'{stem}-chapters.zip';zip_files(package,zip_items);release_assets.append(package)
  pdf=root/'pdf'/f'{stem}.pdf';pdf.parent.mkdir(parents=True,exist_ok=True)
  print('Rendering PDF:',lang,flush=True);HTML(string=pdf_html(lang,renderings[lang],tocs[lang]),base_url=str(ROOT)).write_pdf(pdf)
  manifest['sources'][lang]['pdf_validation']=inspect_pdf(lang,pdf,renderings[lang]);release_assets.append(pdf)
  article='<div class="kicker">v5.0 · '+('中文源版本' if lang=='zh-Hans' else 'Official English Edition')+'</div><h1>'+html.escape(title)+'</h1><p class="fine">'+note+'</p><p><a class="button" href="'+BASE+'downloads.html">下载 / Downloads</a></p><details class="toc" open><summary>'+('目录' if lang=='zh-Hans' else 'Contents')+'</summary>'+toc_html(tocs[lang])+'</details><article>'+renderings[lang]+'</article>'
  out=docs/lang/'official-v5.html';write(out,page(title,article,lang,True,f'{lang}/official-v5.html'))
  readback=BeautifulSoup(out.read_text(),'html.parser').article
  assert normalize(readback.get_text())==normalize(BeautifulSoup(renderings[lang],'html.parser').get_text())
  write(docs/lang/'index.html',retired(f'{lang}/official-v5.html'));write(docs/lang/'read-v5.html',retired(f'{lang}/official-v5.html'))
  links=[]
  for i,ch in enumerate(chunks):
   name='front-matter' if i==0 else (f'chapter-{i-1:02d}' if i<15 else 'appendix-a');label=MARKERS[lang][3:] if i==0 else heads[i-1]
   rh,_=rendered(ch)
   write(docs/lang/'chapters'/f'{name}.html',page(label+' · v5.0','<p><a href="'+BASE+lang+'/chapters/">'+('章节目录' if lang=='zh-Hans' else 'Chapter index')+'</a> · <a href="'+BASE+lang+'/official-v5.html">'+('完整阅读' if lang=='zh-Hans' else 'Full reader')+'</a></p><article>'+rh+'</article>',lang,True))
   links.append(f'<li><a href="{name}.html">{html.escape(label)}</a></li>')
  write(docs/lang/'chapters/index.html',page(title+' — Chapters','<h1>'+('分章阅读' if lang=='zh-Hans' else 'Chapter-by-chapter reading')+'</h1><p>v5.0 · '+note+'</p><ol>'+''.join(links)+'</ol>',lang))
 home='<section class="hero"><p class="kicker">OFFICIAL EDITION · v5.0</p><h1>可能性网络<br>Field of Possibility</h1><p class="sub">我们一直称作“我”的东西，究竟是什么？<br>What exactly is the thing we have always called “I”?</p><p class="fine">'+DATE+' · 中文源版本 / Official English translation</p></section><section class="cards"><div class="card"><h2>中文正式版</h2><p>第 0—13 章、十个 Q&A、科学附录与参考来源。</p><a class="button primary" href="'+BASE+'zh-Hans/official-v5.html">开始阅读</a><a class="button" href="'+BASE+'zh-Hans/chapters/">分章阅读</a></div><div class="card"><h2>Official English Edition</h2><p>Chapters 0–13, ten practice questions, Appendix A and references.</p><a class="button primary" href="'+BASE+'en/official-v5.html">Read the white paper</a><a class="button" href="'+BASE+'en/chapters/">Browse chapters</a></div></section><h2>同一版本，多种阅读方式<br>One edition, multiple formats</h2><p>PDF · Markdown · Obsidian · Chapter ZIP</p><a class="button" href="'+BASE+'downloads.html">下载中心 / Downloads</a><p><a href="'+BASE+'glossary.html">术语对照 / Terminology</a></p>'
 for stem in ['index','downloads','glossary']:
  old=docs/(stem+'.md')
  if old.exists():old.unlink()
 write(docs/'index.html',page('可能性网络 · Field of Possibility v5.0',home,canonical=''))
 cards=[];rawbase=f'https://raw.githubusercontent.com/{REPO}/main/'
 for lang in SOURCES:
  stem=f'field-of-possibility-whitepaper-v5.0-{lang}';langpaths=[('PDF',f'whitepaper/{lang}/pdf/{stem}.pdf'),('Markdown',f'whitepaper/{lang}/full/{stem}.md'),('Obsidian',f'whitepaper/{lang}/obsidian/{stem}-obsidian.md'),('Chapter ZIP',f'whitepaper/{lang}/packages/{stem}-chapters.zip')]
  links=''.join(f'<a class="button" href="{rawbase+p}">{label}</a>' for label,p in langpaths)
  cards.append('<section class="card"><h2>'+('中文源版本' if lang=='zh-Hans' else 'Official English Edition')+'</h2>'+links+'<p><a href="'+BASE+lang+'/official-v5.html">完整阅读 / Full reader</a> · <a href="'+BASE+lang+'/chapters/">分章 / Chapters</a></p></section>')
 write(docs/'downloads.html',page('Downloads · 下载 · v5.0','<p class="kicker">CURRENT OFFICIAL EDITION</p><h1>下载中心<br>Downloads</h1><p>v5.0 · 所有格式由同一份审定全文生成。<br>Every format is generated from the same approved text.</p><div class="cards">'+''.join(cards)+'</div><p><a href="https://github.com/'+REPO+'/releases/tag/v5.0.0">GitHub Release v5.0.0</a></p>'))
 table='| 中文 | English | 本版使用说明 |\n|---|---|---|\n'+'\n'.join('| '+' | '.join(row)+' |' for row in TERMS)+'\n'
 glossary='# v5.0 中英文术语对照 / Terminology\n\n中文为源版本；术语含义以 v5.0 完整正文为准。Chinese is the source edition; definitions are governed by the v5.0 full text.\n\n'+table
 write('glossary/translation-map.md',glossary);write('glossary/README.md','# Terminology · v5.0\n\n[Current bilingual terminology](translation-map.md)\n')
 write(docs/'glossary.html',page('Terminology · 术语 · v5.0',MD.render(glossary)))
 write('translation/README.md','# Translation workflow · v5.0\n\nThe Chinese v5.0 edition is the source. The official English edition uses the same publication version.\n\n- [Chinese source](../whitepaper/zh-Hans/full/field-of-possibility-whitepaper-v5.0-zh-Hans.md)\n- [Official English](../whitepaper/en/full/field-of-possibility-whitepaper-v5.0-en.md)\n- [Terminology](../glossary/translation-map.md)\n\nChanges must identify the original passage, proposed wording, reason, and whether meaning changes. Knowing, Awareness and Luminosity must not be conflated with consciousness. Substantive changes require author review; no new theory is introduced by translation.\n')
 readme='# Field of Possibility｜可能性网络\n\n**v5.0 正式版 / Official Edition** · '+DATE+'\n\n中文为源版本，英文为同版官方对应译本。Chinese is the source edition; English is its official translation.\n\n## 阅读 / Read\n\n- [项目首页 / Homepage]('+SITE+')\n- [中文完整阅读]('+SITE+'zh-Hans/official-v5.html)\n- [Official English reader]('+SITE+'en/official-v5.html)\n- [下载中心 / Downloads]('+SITE+'downloads.html)\n\n## 文件 / Files\n\n| Edition | Markdown | Obsidian | PDF | Chapters | ZIP |\n|---|---|---|---|---|---|\n'
 for lang in SOURCES:
  s=f'field-of-possibility-whitepaper-v5.0-{lang}';r=f'whitepaper/{lang}'
  readme+=f'| {lang} | [Markdown]({r}/full/{s}.md) | [Obsidian]({r}/obsidian/{s}-obsidian.md) | [PDF]({r}/pdf/{s}.pdf) | [Chapters]({r}/chapters/) | [ZIP]({r}/packages/{s}-chapters.zip) |\n'
 readme+='\n## 项目与协作 / Project and collaboration\n\n本项目是关于能知、显化、意识、生命与实践的开放哲学框架。创作方式与 AI 的参与见正文卷首及第 9 章。\n\nThis is an open philosophical and practical framework. The writing process and AI collaboration are described in the opening note and Chapter 9.\n\n- [术语对照 / Terminology](glossary/translation-map.md)\n- [贡献说明 / Contributing](CONTRIBUTING.md)\n- [翻译流程 / Translation](translation/README.md)\n- [发布记录 / Release notes](releases/v5.0.0.md)\n- [文件校验 / Checksums](releases/v5.0.0-manifest.json)\n\n## 许可 / License\n\n[CC BY-NC-SA 4.0](LICENSE.md)\n\n网站与默认下载入口仅展示当前正式版。历史提交与标签保留；恢复历史版本展示需作者明确授权。The website and default download entries show only the current official edition. Git history and historical tags are retained. Restoring an old edition to the public navigation requires explicit author authorization.\n'
 write('README.md',readme)
 write('CONTRIBUTING.md','# Contributing · Field of Possibility v5.0\n\nThe current official edition is v5.0 in Chinese and English. Both full manuscripts have passed author review.\n\nChinese remains the source edition. Read the [full text](whitepaper/zh-Hans/full/field-of-possibility-whitepaper-v5.0-zh-Hans.md), [English edition](whitepaper/en/full/field-of-possibility-whitepaper-v5.0-en.md), and [terminology map](glossary/translation-map.md) before proposing changes.\n\n## How to contribute\n\nUse Issues for errors, broken links, references and translation corrections. Use Discussions for conceptual questions and reading notes. A pull request should state the exact source passage, proposed wording and reason, and separate a language correction from a change of theory.\n\n## Core distinctions\n\nThe two layers distinguish Knowing from the known without establishing two independent ontological grounds. Awareness is not consciousness. Consciousness, intelligence and life-state are distinct terms. Return is defined in the v5.0 text and must not be replaced by earlier terminology. Scientific analogies are not proof of the ontology.\n\nAI may assist with drafting and comparison, but its output is not final authority. Substantive changes require author review. All generated formats must be regenerated from the same reviewed full text.\n\n## Historical editions\n\nDo not restore historical editions to the site navigation or current download entries without explicit author authorization. Do not rewrite historical tags or replace an old versioned asset with new text.\n\n## License\n\nContributions follow the existing [CC BY-NC-SA 4.0 license](LICENSE.md).\n')
 notes='# 可能性网络白皮书 v5.0｜中英文正式版\n\n'+DATE+' · Tag: `v5.0.0`\n\n本版发布经作者终审通过的中文全文及官方英文对应译本。理论正文不因格式转换而改写。\n\nThis release publishes the author-reviewed Chinese source and its complete official English translation. Formatting does not revise the approved text.\n\n## 主要修订 / Main revisions\n\n- 唯一能知、唯有与本体不二的展开。\n- 意识、生命、智能及 AI 工程支线的进一步区分。\n- 单帧中断与十个实践 Q&A 的完整末端辨认。\n- 人机协作的创作说明、章节衔接与科学附录。\n\n## 格式 / Formats\n\nBoth languages include full Markdown, Obsidian-compatible Markdown, PDF, chapter files and chapter ZIP packages. A manifest records checksums and source-body identity.\n\n## 展示政策 / Display policy\n\nAll current reading and download entries point to v5.0. Old website addresses direct readers to the current edition without serving the old text. Historical Git commits and tags are not rewritten. Reopening older editions in normal public navigation requires explicit author authorization.\n\n## License\n\nCC BY-NC-SA 4.0. See LICENSE.md.\n'
 write('releases/v5.0.0.md',notes)
 changelog=Path('CHANGELOG.md');old=changelog.read_text() if changelog.exists() else '# Changelog\n'
 if '## 2026-09-08｜v5.0' not in old:
  old=old.replace('# Changelog','# Changelog\n\n## 2026-09-08｜v5.0 bilingual official edition\n\nPublished the author-reviewed Chinese source and complete official English translation; regenerated all reading/download formats; aligned terminology and contribution guidance; switched current entry points to v5.0. Historical commits and tags are retained, not replaced.\n',1)
 write(changelog,old);write('VERSION','5.0.0\n')
 for p in list(docs.rglob('*.md')):
  t=p.read_text(errors='replace')
  if 'v4.0' in t or 'official-v4' in t:
   dest='en/official-v5.html' if '/en/' in str(p) else 'zh-Hans/official-v5.html'
   write(p.with_suffix('.html'),retired(dest));p.unlink()
 for lang in SOURCES:
  for name in ['official-v4','read-v4']:
   write(docs/lang/(name+'.html'),retired(lang+'/official-v5.html'))
 for p in release_assets:write(docs/'assets/downloads'/p.name,p.read_bytes())
 all_items={str(p):p.read_bytes() for p in Path('whitepaper').rglob('*') if p.is_file()}
 all_items['LICENSE.md']=Path('LICENSE.md').read_bytes();all_items['README.md']=readme.encode()
 bundle=Path('releases/field-of-possibility-whitepaper-v5.0-bilingual.zip');zip_files(bundle,all_items);release_assets.append(bundle)
 for p in release_assets:manifest['assets'][str(p)]={'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
 link_errors=[]
 for p in docs.rglob('*.html'):
  soup=BeautifulSoup(p.read_text(),'html.parser')
  for a in soup.find_all(['a','link']):
   href=a.get('href','')
   if href.startswith(BASE):
    rel=unquote(href[len(BASE):].split('#')[0]);q=docs/(rel or 'index.html')
    if q.is_dir():q=q/'index.html'
    if not q.exists():link_errors.append([str(p),href])
   elif href.startswith('#') and soup.find(id=href[1:]) is None:link_errors.append([str(p),href])
 if link_errors:raise RuntimeError(f'Broken generated links: {link_errors[:8]}')
 for lang in SOURCES:
  official=(Path('whitepaper')/lang/'full'/f'field-of-possibility-whitepaper-v5.0-{lang}.md').read_text()
  assert official[official.index(MARKERS[lang]+'\n'):]==bodies[lang]
 manifest['validation']={'approved_body_preserved':True,'numbered_chapters_each_language':14,'qa_each_language':10,'appendix_sections_each_language':11,'references_each_language':12,'generated_local_links_checked':True}
 write('releases/v5.0.0-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 write(QA/'retired-current-paths.json',json.dumps({'removed_assets':removed,'old_web_aliases':aliases},ensure_ascii=False,indent=2))
 write(QA/'build-summary.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 write(WORK/'release-assets.txt','\n'.join(str(p) for p in release_assets)+ '\nreleases/v5.0.0-manifest.json\n')
 print(json.dumps(manifest,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
