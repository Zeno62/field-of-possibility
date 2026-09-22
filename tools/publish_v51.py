#!/usr/bin/env python3
"""Publish the exact approved bilingual readers; never rewrite their prose.

Staging pieces are checked individually and as a complete Git blob. Only piece
boundary newlines are restored to their specified count before verification.
Historical v5.0 assets and tags are not modified. --verify-only never builds.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, shutil, time, unicodedata, urllib.request, zipfile
from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup
from weasyprint import HTML
import fitz

ROOT = Path(__file__).resolve().parents[1]
VERSION = '5.1.0'
DATE = '2026-09-22'
BASE = '/field-of-possibility/'
SITE = 'https://zeno62.github.io' + BASE
REPO = 'Zeno62/field-of-possibility'
QA = ROOT / '.build-v51/qa'
MANIFEST = ROOT / 'releases/v5.1.0-manifest.json'
APPROVED = {'zh-Hans': '04ee29a5112b1007de24ccfa5408a6b19e6e91d9', 'en': 'c973a7cb6983b809025b71bf02b9e57f2bfec3ce'}
CHUNKS = {
 'zh-Hans': [('1b1260bb2b1f29fdffc504392a570f769c2f160c',2),('41be2e5387bd00c609a484861d333ae0416760a7',1),('04dd25d8d73701f6316a99196640ae048c149baf',2),('b9f4041520c09bba2d5d27f9c50b3514b1627655',1)],
 'en': [('a0e9f57ad2d8e672f108c955d6faec0a2ff36452',2),('2362718de0fe3179f12730757a77a7bc1e56a54c',1),('e42928c04984df528edca3c918811537764a1d2b',2),('0d3217a21946f868383e91e5985e5d04ffaa2260',1),('e531666076e3ecdd8a2442b4a09d30e0d1bfb130',2),('c446d89b1fc015e0b6f88704e08230591972bd02',2),('86a17ced8ca71a3ed3244d8f956decac0c5de6ee',1),('2a10ab0995931b5b700335286325d300a1e7f722',1)]}
TITLES = {'zh-Hans':'可能性网络','en':'Field of Possibility'}
MD = MarkdownIt('commonmark', {'html':True}).enable('table')
GENERATED: set[str] = set()
PRINT = '''
@page{size:A4;margin:22mm 22mm 21mm;@top-left{content:'FIELD OF POSSIBILITY';font-family:'Noto Sans';font-size:8pt;color:#62747c}@bottom-left{content:'CC BY-NC-SA 4.0';font-family:'Noto Sans';font-size:7.5pt;color:#6b777c}@bottom-right{content:counter(page);font-family:'Noto Sans';font-size:8pt;color:#6b777c}}
@page:first{@top-left{content:none}@bottom-left{content:none}@bottom-right{content:none}}
*{box-sizing:border-box}body{font-family:'Noto Serif','Noto Serif CJK SC',serif;font-size:10.5pt;line-height:1.6;color:#182f38;font-variant-ligatures:none}body.zh{font-family:'Noto Serif CJK SC','Noto Serif',serif;font-size:10.4pt;line-height:1.8}
h1,h2,h3{font-family:'Noto Sans','Noto Sans CJK SC',sans-serif;line-height:1.4;break-after:avoid}h1{font-size:21pt;break-before:page;margin:0 0 9mm;bookmark-level:1}h2{font-size:13.5pt;margin:6mm 0 3mm;bookmark-level:2}h3{font-size:11.5pt;margin:5mm 0 2mm;bookmark-level:3}p{margin:0 0 3mm;orphans:3;widows:3}blockquote{border-left:2pt solid #316570;margin:4mm 0;padding:2mm 0 1mm 5mm;break-inside:avoid}blockquote p{margin:0 0 2mm}pre{font:8.2pt/1.65 'Noto Sans Mono','Noto Sans CJK SC',monospace;white-space:pre-wrap;overflow-wrap:anywhere;padding:3.5mm;background:#eff4f3;break-inside:avoid}a{color:#245c68;text-decoration:none;overflow-wrap:anywhere}hr{border:0;height:0;margin:4mm 0}ol,ul{padding-left:6mm}li{margin-bottom:2mm;orphans:3;widows:3}.cover{height:246mm;padding-top:40mm;break-after:page}.cover h1{break-before:auto;bookmark-level:none;font-size:34pt;margin:12mm 0 8mm}.cover .subtitle{font:19pt 'Noto Sans','Noto Sans CJK SC',sans-serif;color:#4c626b}.cover .license{margin-top:30mm;font:10pt 'Noto Sans',sans-serif;color:#62747c}.contents{break-after:page}.contents h1{break-before:auto;bookmark-level:none}.contents ol{list-style:none;padding:0}.contents li{font:10pt/1.65 'Noto Sans','Noto Sans CJK SC',sans-serif;margin:0 0 3mm}.contents a:after{content:leader('.') target-counter(attr(href),page)}#book-title{display:none}.refs{font-size:8.5pt;line-height:1.5}.keep{break-inside:avoid}.keep h2{margin-top:0}sub{font-size:75%}table{border-collapse:collapse;width:100%}td,th{padding:2mm;border-bottom:.5pt solid #ddd}
'''

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def blob(b: bytes) -> str: return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def norm(s: str) -> str: return re.sub(r'\s+','',unicodedata.normalize('NFKC',s)).replace('\u00ad','')
def write(path: str | Path, value: str | bytes) -> Path:
 p = ROOT/path; p.parent.mkdir(parents=True, exist_ok=True)
 p.write_bytes(value.encode() if isinstance(value,str) else value)
 if not str(p.relative_to(ROOT)).startswith('.build-v51'): GENERATED.add(str(p.relative_to(ROOT)))
 return p

def source(lang: str) -> bytes:
 data=[]
 for i,(expected,nl) in enumerate(CHUNKS[lang],1):
  p=ROOT/f'releases/v5.1.0-source/{lang}.{i:02}.md'
  b=p.read_bytes().rstrip(b'\n')+b'\n'*nl
  if blob(b)!=expected: raise ValueError(f'Approved piece mismatch: {p.name}: {blob(b)} != {expected}')
  data.append(b)
 raw=b''.join(data)
 if blob(raw)!=APPROVED[lang]: raise ValueError(f'Approved full source mismatch: {lang}')
 text=raw.decode(); nums=re.findall(r'^# (\d+)\s*[｜|]',text,re.M)
 assert nums==list(map(str,range(14))),nums
 assert len(re.findall(r'^## Q\d+\s*[｜|]',text,re.M))==10
 assert len(re.findall(r'^## A\.\d+\s*[｜|]',text,re.M))==11
 assert '<a id="afterword"></a>' in text
 return raw

def render(text: str):
 soup=BeautifulSoup(MD.render(text),'html.parser'); toc=[]
 for empty in soup.find_all('a',id='afterword'): empty.decompose()
 for i,h in enumerate(soup.find_all(['h1','h2','h3'])):
  label=h.get_text(); n=re.match(r'^(\d+)\s*[｜|]',label); q=re.match(r'^Q(\d+)\s*[｜|]',label); a=re.match(r'^A\.(\d+)\s*[｜|]',label)
  if n and h.name=='h1': key='chapter-'+n.group(1)
  elif h.name=='h1' and (label.startswith('后记') or label.startswith('Afterword')): key='afterword'
  elif h.name=='h1' and (label.startswith('附录') or label.startswith('Appendix')): key='appendix-a'
  elif h.name=='h1': key='book-title'
  elif q: key='q'+q.group(1)
  elif a: key='a'+a.group(1)
  elif label in ['参考来源','References']: key='references'
  else: key='section-'+str(i)
  h['id']=key
  if h.name=='h1' and key!='book-title': toc.append((key,label))
 refs=soup.find(id='references')
 if refs:
  ol=refs.find_next_sibling('ol'); assert ol and len(ol.find_all('li',recursive=False))==14
  ol['class']='refs'
  for i,li in enumerate(ol.find_all('li',recursive=False),1): li['id']='ref-'+str(i)
 for node in list(soup.find_all(string=True)):
  if node.find_parent(['a','pre','code','style','script']): continue
  for part in re.split(r'(https?://[^\s<>]+|\[\d+\])',str(node)):
   if re.fullmatch(r'\[\d+\]',part) and refs:
    a=soup.new_tag('a',href='#ref-'+part[1:-1]);a.string=part;node.insert_before(a)
   elif part.startswith(('http://','https://')):
    a=soup.new_tag('a',href=part);a.string=part;node.insert_before(a)
   elif part: node.insert_before(part)
  node.extract()
 for h in soup.find_all('h2'):
  if h.get_text().startswith(('最短实操','The Shortest Practice')):
   box=soup.new_tag('section',attrs={'class':'keep'});h.insert_before(box)
   cur=h
   while cur and cur.name not in ['hr','h1']:
    nxt=cur.find_next_sibling()
    if cur!=h and cur.name=='h2': break
    box.append(cur.extract());cur=nxt
 for bq in list(soup.find_all('blockquote')):
  if bq.get_text(strip=True) in ['回归 = 明性认得自身为全知','Return = Luminosity recognizing itself as Total Knowing']:
   nxt=bq.find_next_sibling();box=soup.new_tag('div',attrs={'class':'keep'});bq.insert_before(box);box.append(bq.extract())
   if nxt and nxt.name=='p': box.append(nxt.extract())
 return soup,toc

def nav() -> str:
 return f'<nav class="top"><a class="brand" href="{BASE}">Field of Possibility · 可能性网络</a><a href="{BASE}zh-Hans/official-v5.html">中文</a><a href="{BASE}en/official-v5.html">English</a><a href="{BASE}downloads.html">下载 / Downloads</a><a href="https://github.com/{REPO}">GitHub</a></nav>'
def page(title: str, body: str, lang='zh-Hans', reader=False) -> str:
 return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="fop-release" content="{VERSION}"><title>{html.escape(title)}</title><link rel="stylesheet" href="{BASE}assets/css/v5.css"></head><body>{nav()}<main class="'+('reader' if reader else '')+'">'+body+'</main><footer>CC BY-NC-SA 4.0 · '+DATE+' · v5.1</footer></body></html>'
def toc_html(toc): return '<ol>'+''.join(f'<li><a href="#{key}">{html.escape(label)}</a></li>' for key,label in toc)+'</ol>'
def stem(lang): return f'field-of-possibility-whitepaper-v5.1-{lang}'
def web_reader(lang,soup,toc):
 return page(TITLES[lang], '<p class="fine">v5.1 · '+DATE+'</p><p><a href="'+BASE+'downloads.html">PDF · Markdown · Obsidian · ZIP</a></p><details class="toc"><summary>'+('目录' if lang=='zh-Hans' else 'Contents')+'</summary>'+toc_html(toc)+'</details><article>'+str(soup)+'</article>',lang,True)

def pdf_build(lang,soup,toc,path):
 title=TITLES[lang];other='Field of Possibility' if lang=='zh-Hans' else '可能性网络'
 body=f'<section class="cover"><h1>{title}</h1><p class="subtitle">{other}</p><p class="license">CC BY-NC-SA 4.0</p></section><section class="contents"><h1>'+('目录' if lang=='zh-Hans' else 'Contents')+'</h1>'+toc_html(toc)+'</section><article>'+str(soup)+'</article>'
 doc=f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title><style>{PRINT}</style></head><body class="'+('zh' if lang=='zh-Hans' else 'en')+'">'+body+'</body></html>'
 path.parent.mkdir(parents=True,exist_ok=True); HTML(string=doc,base_url=str(ROOT)).write_pdf(path)
 GENERATED.add(str(path.relative_to(ROOT))); pdf=fitz.open(path)
 full=norm(''.join(p.get_text() for p in pdf));cursor=0;missing=[];blocks=0
 for el in soup.find_all(['h1','h2','h3','p','pre','li']):
  if el.get('id')=='book-title' or el.find_parent(['li','pre']):continue
  value=norm(el.get_text());
  if not value: continue
  pos=full.find(value,cursor)
  if pos<0:missing.append(el.get_text()[:90])
  else:cursor=pos+len(value)
  blocks+=1
 assert not missing, f'{lang} PDF missing content: {missing[:8]}'
 errors=[]
 for i,p in enumerate(pdf):
  for b in p.get_text('dict')['blocks']:
   for ln in b.get('lines',[]):
    for sp in ln.get('spans',[]):
     x0,y0,x1,y1=sp['bbox']
     if x0<0 or x1>p.rect.width+.1 or y0<0 or y1>p.rect.height+.1: errors.append(i+1)
     assert '\ufffd' not in sp['text']
 assert not errors, f'PDF overflow {lang}: {errors}'
 for key,label in toc: assert any(norm(t[1])==norm(label) for t in pdf.get_toc()),key
 QA.mkdir(parents=True,exist_ok=True)
 for i in [0,1,len(pdf)-1]:pdf[i].get_pixmap(matrix=fitz.Matrix(.9,.9)).save(QA/f'{lang}-page-{i+1}.png')
 from PIL import Image, ImageDraw
 for start in range(0,len(pdf),16):
  sheet=Image.new('RGB',(800,1190),'white');draw=ImageDraw.Draw(sheet)
  for j in range(start,min(start+16,len(pdf))):
   pix=pdf[j].get_pixmap(matrix=fitz.Matrix(.29,.29));im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
   x=((j-start)%4)*200+12;y=((j-start)//4)*295+22;sheet.paste(im,(x,y));draw.text((x,y-16),str(j+1),fill='black')
  sheet.save(QA/f'{lang}-contact-{start+1:02}.png')
 report={'pages':len(pdf),'source_blocks_checked':blocks,'bookmarks':len(pdf.get_toc()),'missing_blocks':missing,'overflow_pages':errors}
 print(lang,report,flush=True);return report

def split_source(text):
 matches=list(re.finditer(r'^# (.+)$',text,re.M));out=[]
 for i,m in enumerate(matches):
  label=m.group(1);n=re.match(r'^(\d+)\s*[｜|]',label)
  name=f'chapter-{int(n.group(1)):02}' if n else ('afterword' if label.startswith(('后记','Afterword')) else 'appendix-a' if label.startswith(('附录','Appendix')) else 'front-matter')
  out.append((name,label,text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)]))
 assert len(out)==17 and ''.join(c for _,_,c in out)==text
 return out

def check_links(paths):
 checked=0
 for rel in paths:
  if not rel.startswith('docs/') or not rel.endswith('.html'): continue
  p=ROOT/rel;s=BeautifulSoup(p.read_text(),'html.parser');ids={n.get('id') for n in s.find_all(id=True)}
  for a in s.find_all(['a','link'],href=True):
   href=a['href'];u=urlsplit(href)
   if u.scheme or u.netloc:continue
   if not u.path: assert not u.fragment or unquote(u.fragment) in ids,(rel,href)
   else:
    target=ROOT/'docs'/unquote(u.path[len(BASE):]) if u.path.startswith(BASE) else p.parent/unquote(u.path)
    if u.path.endswith('/'):target=target/'index.html'
    assert target.exists(),(rel,href,str(target))
    if u.fragment and target.suffix=='.html':assert BeautifulSoup(target.read_text(),'html.parser').find(id=unquote(u.fragment)),(rel,href)
   checked+=1
 return checked

def build():
 hist={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in ROOT.rglob('*v5.0*') if p.is_file() and '.git' not in p.parts}
 manifest={'version':VERSION,'released':DATE,'sources':{},'assets':[],'files':{},'historical_assets':hist}
 for lang in APPROVED:
  raw=source(lang);text=raw.decode();st=stem(lang);root=f'whitepaper/{lang}'
  full=write(f'{root}/full/{st}.md',raw);manifest['assets'].append(str(full.relative_to(ROOT)))
  soup,toc=render(text);assert len(toc)==16
  obs='# '+TITLES[lang]+'\n\n## '+('目录' if lang=='zh-Hans' else 'Contents')+'\n\n'+'\n'.join(f'- [{label}](#{quote(label, safe="")})' for _,label in toc)+'\n\n'+text.split('\n',1)[1]
  obs=obs.replace('](#afterword)','](#'+quote(next(label for key,label in toc if key=='afterword'),safe='')+')')
  op=write(f'{root}/obsidian/{st}-obsidian.md',obs);manifest['assets'].append(str(op.relative_to(ROOT)))
  pdf=ROOT/f'{root}/pdf/{st}.pdf';report=pdf_build(lang,soup,toc,pdf);manifest['assets'].append(str(pdf.relative_to(ROOT)))
  manifest['sources'][lang]={'git_blob':blob(raw),'sha256':sha(raw),'bytes':len(raw),'path':str(full.relative_to(ROOT)),'pdf_validation':report}
  write(f'docs/{lang}/official-v5.html',web_reader(lang,soup,toc))
  for alias in ['index.html','read-v5.html','official-v5.1.html']:
   write(f'docs/{lang}/{alias}',f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=official-v5.html"><a href="official-v5.html">'+TITLES[lang]+'</a>')
  index=[];zipdata={}
  for name,label,chunk in split_source(text):
   cm=chunk.replace('](#afterword)','](afterword.md#afterword)') if name!='afterword' else chunk
   write(f'{root}/chapters/{name}.md',cm);zipdata[name+'.md']=cm.encode();index.append((name,label))
   cs,_=render(chunk)
   for a in cs.find_all('a',href='#afterword'):
    if name!='afterword':a['href']='afterword.html#afterword'
   content='<p><a href="index.html">'+('章节目录' if lang=='zh-Hans' else 'Chapters')+'</a> · <a href="../official-v5.html">'+('完整阅读' if lang=='zh-Hans' else 'Full reader')+'</a></p><article>'+str(cs)+'</article>'
   write(f'docs/{lang}/chapters/{name}.html',page(label,content,lang,True))
  ix='# '+TITLES[lang]+'\n\n'+'\n'.join(f'- [{label}]({name}.md)' for name,label in index)+'\n'
  write(f'{root}/chapters/README.md',ix);zipdata['README.md']=ix.encode()
  if (ROOT/'LICENSE.md').exists():zipdata['LICENSE.md']=(ROOT/'LICENSE.md').read_bytes()
  zp=ROOT/f'{root}/packages/{st}-chapters.zip';zp.parent.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
   for n,b in zipdata.items():info=zipfile.ZipInfo(n,(2026,9,22,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
  GENERATED.add(str(zp.relative_to(ROOT)));manifest['assets'].append(str(zp.relative_to(ROOT)))
  write(f'docs/{lang}/chapters/index.html',page(TITLES[lang],'<h1>'+('分章阅读' if lang=='zh-Hans' else 'Chapters')+'</h1><ol>'+''.join(f'<li><a href="{n}.html">{html.escape(l)}</a></li>' for n,l in index)+'</ol>',lang))
  for f in [full,op,pdf,zp]:write('docs/assets/downloads/'+f.name,f.read_bytes())
 home='<section class="hero"><p class="kicker">OFFICIAL EDITION · v5.1</p><h1>可能性网络<br>Field of Possibility</h1><p class="sub">我们一直称作“我”的东西，究竟是什么？<br>What exactly is the thing we have always called “I”?</p><p class="fine">'+DATE+' · 中文源版本 / Official English translation</p></section><section class="cards">'
 for lang,title,desc,read in [('zh-Hans','中文正式版','第 0—13 章、十个实践问答、哲学后记与科学附录。','开始阅读'),('en','Official English Edition','Chapters 0–13, ten practice questions, the philosophical afterword, and Appendix A.','Read the white paper')]:
  home+=f'<div class="card"><h2>{title}</h2><p>{desc}</p><a class="button primary" href="{BASE}{lang}/official-v5.html">{read}</a><a class="button" href="{BASE}{lang}/chapters/">分章 / Chapters</a></div>'
 home+='</section><h2>同一版本，多种阅读方式<br>One edition, multiple formats</h2><p>PDF · Markdown · Obsidian · Chapter ZIP</p><a class="button" href="'+BASE+'downloads.html">下载中心 / Downloads</a><p><a href="'+BASE+'glossary.html">术语对照 / Terminology</a></p>'
 write('docs/index.html',page('可能性网络 · Field of Possibility',home))
 cards=''
 for lang in APPROVED:
  st=stem(lang);cards+='<section class="card"><h2>'+TITLES[lang]+'</h2>'
  for label,suffix in [('PDF','.pdf'),('Markdown','.md'),('Obsidian','-obsidian.md'),('Chapter ZIP','-chapters.zip')]:cards+=f'<a class="button" href="{BASE}assets/downloads/{st}{suffix}">{label}</a>'
  cards+=f'<p><a href="{BASE}{lang}/official-v5.html">完整阅读 / Full reader</a></p></section>'
 write('docs/downloads.html',page('下载 · Downloads','<h1>下载中心<br>Downloads</h1><p>v5.1 · '+DATE+' · 同一审定全文 / The same approved text</p><div class="cards">'+cards+'</div><p><a href="https://github.com/'+REPO+'/releases/tag/v5.1.0">GitHub Release v5.1.0</a></p>'))
 for name in ['glossary/translation-map.md','glossary/README.md','translation/README.md','CONTRIBUTING.md']:
  p=ROOT/name
  if p.exists():write(name,p.read_text().replace('v5.0','v5.1'))
 gp=ROOT/'glossary/translation-map.md'
 if gp.exists():write('docs/glossary.html',page('术语 · Terminology',MD.render(gp.read_text())))
 readme='# Field of Possibility｜可能性网络\n\n**v5.1 中英文正式版 / Bilingual official edition** · '+DATE+'\n\n中文为源版本，英文为对应译本。Chinese is the source edition.\n\n## 阅读 / Read\n\n'
 readme+=f'- [项目首页 / Homepage]({SITE})\n- [中文完整阅读]({SITE}zh-Hans/official-v5.html)\n- [English reader]({SITE}en/official-v5.html)\n- [下载中心 / Downloads]({SITE}downloads.html)\n\n## 文件 / Files\n\n| 语言 / Language | Markdown | PDF | Obsidian | 分章 / Chapters | ZIP |\n|---|---|---|---|---|---|\n'
 for l in APPROVED:
  st=stem(l);p=f'whitepaper/{l}';readme+=f'| {l} | [全文]({p}/full/{st}.md) | [PDF]({p}/pdf/{st}.pdf) | [Obsidian]({p}/obsidian/{st}-obsidian.md) | [Chapters]({p}/chapters/) | [ZIP]({p}/packages/{st}-chapters.zip) |\n'
 readme+='\n## 项目与协作 / Project and collaboration\n\n本项目是关于能知、显化、意识、生命与实践的开放哲学框架。创作方式与 AI 的参与见卷首及第 9 章。\n\nAn open philosophical and practical framework. The writing process and AI collaboration are described in the opening note and Chapter 9.\n\n- [术语 / Terminology](glossary/translation-map.md)\n- [贡献 / Contributing](CONTRIBUTING.md)\n- [翻译 / Translation](translation/README.md)\n- [发布记录 / Release notes](releases/v5.1.0.md)\n- [文件校验 / Checksums](releases/v5.1.0-manifest.json)\n\n## License\n\n[CC BY-NC-SA 4.0](LICENSE.md)\n\n默认阅读与下载入口指向当前正式版；旧标签、版本文件和提交保留为历史，不覆盖。Current entries show this edition; historical tags, versioned assets and commits are retained unchanged.\n'
 write('README.md',readme);write('VERSION',VERSION+'\n')
 notes='# 可能性网络 · Field of Possibility v5.1\n\n'+DATE+'\n\n作者已批准中文阅读版，并授权合并、替换公开中英文版本。本次发布保留已批准正文，不在打包时改写内容。\n\nThe author approved the Chinese reader and authorized merging and publishing both complete editions. Approved source texts are not rewritten during packaging.\n\n## 本版 / This edition\n\n- 正文与哲学后记分层；十个实践问答、科学附录与十四项来源完整收录。\n- 完成人文关怀、文笔与叙述姿态修订及对应英文。\n- 阅读稿不包含候选标签或编辑说明；网页、PDF、Markdown、Obsidian 和分章包使用同一内容。\n- 历史 v5.0.0 标签和资产不改写；当前导航切至 v5.1。\n\nPDF pagination is generated for publication from the exact approved Markdown; source identity and rendered text coverage are recorded in the manifest. This is not a new scientific, clinical, or reader-effect validation.\n\nCC BY-NC-SA 4.0.\n'
 write('releases/v5.1.0.md',notes)
 cp=ROOT/'CHANGELOG.md';old=cp.read_text() if cp.exists() else '# Changelog\n'
 entry='\n\n## 2026-09-22｜v5.1 bilingual reading edition\n\nPublished the approved revised Chinese reader and corresponding English translation; separated the philosophical afterword; refreshed all current reading and download entries. Historical versioned assets remain unchanged.\n'
 if '## 2026-09-22｜v5.1' not in old:old=old.replace('# Changelog','# Changelog'+entry,1)
 write('CHANGELOG.md',old)
 for rel,value in hist.items():assert sha((ROOT/rel).read_bytes())==value,'Historical asset changed: '+rel
 manifest['internal_links_checked']=check_links(sorted(GENERATED))
 manifest['files']={rel:sha((ROOT/rel).read_bytes()) for rel in sorted(GENERATED)}
 write('docs/release.json',json.dumps({'version':VERSION,'released':DATE,'sources':APPROVED},indent=2)+'\n')
 manifest['files']['docs/release.json']=sha((ROOT/'docs/release.json').read_bytes())
 write(MANIFEST,json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 verify();return manifest

def verify():
 m=json.loads(MANIFEST.read_text());assert (ROOT/'VERSION').read_text().strip()==VERSION
 for lang,meta in m['sources'].items():assert blob((ROOT/meta['path']).read_bytes())==APPROVED[lang]
 for rel,digest in m['files'].items():assert sha((ROOT/rel).read_bytes())==digest,'Asset hash mismatch: '+rel
 for rel,digest in m['historical_assets'].items():assert sha((ROOT/rel).read_bytes())==digest,'Historical asset changed: '+rel
 links=check_links(m['files']);print('Verified',len(m['files']),'assets and',links,'internal links',flush=True)
 return m

def live_check():
 m=verify();checks={
  'release.json':None,'':None,'downloads.html':None,
  'zh-Hans/official-v5.html':None,'en/official-v5.html':None,
  'zh-Hans/chapters/afterword.html':None,'en/chapters/afterword.html':None}
 for rel,digest in m['files'].items():
  if rel.startswith('docs/assets/downloads/'):checks[rel[5:]]=digest
 errors=[];results=[]
 for path,digest in checks.items():
  for attempt in range(12):
   try:
    req=urllib.request.Request(SITE+path+'?release=5.1.0&attempt='+str(attempt),headers={'User-Agent':'fop-publication-check'})
    with urllib.request.urlopen(req,timeout=40) as r:data=r.read();status=r.status
    if digest:assert sha(data)==digest,'content hash mismatch'
    elif path=='release.json':assert json.loads(data)['sources']==APPROVED
    else:assert b'5.1.0' in data or b'v5.1' in data,'stale edition'
    results.append({'path':path,'status':status,'sha256':sha(data)});break
   except Exception as e:
    if attempt==11:errors.append({'path':path,'error':str(e)})
    else:time.sleep(10)
 QA.mkdir(parents=True,exist_ok=True);(QA/'live-check.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2))
 assert not errors,errors
 print('Live HTTP and download hashes verified:',len(results),flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--verify-only',action='store_true');parser.add_argument('--live-check',action='store_true');a=parser.parse_args()
 if a.live_check:live_check()
 elif a.verify_only:verify()
 else:build()
