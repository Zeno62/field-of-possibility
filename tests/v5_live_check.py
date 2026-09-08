#!/usr/bin/env python3
"""Read-only acceptance test for the deployed author-approved v5.0 release."""
from __future__ import annotations
import hashlib, io, json, os, re, time, urllib.request, zipfile
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

REPO='Zeno62/field-of-possibility'
SITE='https://zeno62.github.io/field-of-possibility/'
RAW=f'https://raw.githubusercontent.com/{REPO}/main/'
OUT=Path('qa-v5-live');OUT.mkdir(exist_ok=True)
manifest=json.loads(Path('releases/v5.0.0-manifest.json').read_text())
report={'version':'5.0.0','pages':[],'downloads':[],'release_assets':[],'retired_urls':[],'screenshots':[],'errors':[]}

def digest(data):return hashlib.sha256(data).hexdigest()
def fetch(url):
 headers={'User-Agent':'Field-of-Possibility-v5-acceptance','Cache-Control':'no-cache'}
 if urlparse(url).netloc=='api.github.com' and os.environ.get('GH_TOKEN'):
  headers['Authorization']='Bearer '+os.environ['GH_TOKEN'];headers['Accept']='application/vnd.github+json'
 last=None
 for retry in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=45) as r:return r.status,r.read(),r.geturl()
  except Exception as exc:last=exc;time.sleep(3*(retry+1))
 raise last

def run():
 readers=['','downloads.html','glossary.html','assets/css/v5.css']
 for lang in ['zh-Hans','en']:
  readers += [f'{lang}/official-v5.html',f'{lang}/chapters/index.html',f'{lang}/chapters/front-matter.html',f'{lang}/chapters/appendix-a.html']
  readers += [f'{lang}/chapters/chapter-{i:02d}.html' for i in range(14)]
 for route in readers:
  status,body,final=fetch(SITE+route)
  local=Path('docs')/(route or 'index.html')
  assert status==200 and digest(body)==digest(local.read_bytes()),'Deployed page differs: '+route
  report['pages'].append({'url':SITE+route,'status':status,'sha256':digest(body),'matches_committed_file':True})
 for path,entry in manifest['assets'].items():
  status,body,_=fetch(RAW+path)
  assert status==200 and digest(body)==entry['sha256'],'Download mismatch: '+path
  report['downloads'].append({'url':RAW+path,'status':status,'sha256':digest(body),'bytes':len(body)})
 for lang in ['zh-Hans','en']:
  marker='## 创作说明\n' if lang=='zh-Hans' else '## Note on the Writing Process\n'
  stem=f'field-of-possibility-whitepaper-v5.0-{lang}'
  full=(Path('whitepaper')/lang/'full'/(stem+'.md')).read_text()
  body=full[full.index(marker):]
  assert digest(body.encode())==manifest['sources'][lang]['approved_body_sha256']
  obs=(Path('whitepaper')/lang/'obsidian'/(stem+'-obsidian.md')).read_text()
  assert obs[obs.index(marker):]==body
  with zipfile.ZipFile(Path('whitepaper')/lang/'packages'/(stem+'-chapters.zip')) as z:
   names=['00-front-matter.md']+[f'chapter-{i:02d}.md' for i in range(14)]+['appendix-a.md']
   assert ''.join(z.read(n).decode() for n in names)==body
   assert z.testzip() is None
  for name in ['official-v4','read-v4']:
   for suffix in ['', '.html']:
    url=SITE+lang+'/'+name+suffix
    status,data,final=fetch(url);soup=BeautifulSoup(data.decode(),'html.parser')
    refresh=soup.find('meta',attrs={'http-equiv':'refresh'})
    assert status==200 and refresh and f'{lang}/official-v5.html' in refresh.get('content',''),url
    assert soup.find('article') is None,'Old text still shown: '+url
    report['retired_urls'].append({'url':url,'status':status,'destination':f'{lang}/official-v5.html','old_body_displayed':False})
 status,data,_=fetch(f'https://api.github.com/repos/{REPO}/releases/latest')
 release=json.loads(data);assert release['tag_name']=='v5.0.0' and not release['draft'] and not release['prerelease']
 expected={Path(p).name:d['sha256'] for p,d in manifest['assets'].items()}
 expected['v5.0.0-manifest.json']=digest(Path('releases/v5.0.0-manifest.json').read_bytes())
 assert set(expected)=={a['name'] for a in release['assets']},'Release attachment set mismatch'
 for asset in release['assets']:
  status,data,_=fetch(asset['browser_download_url'])
  assert status==200 and digest(data)==expected[asset['name']],asset['name']
  report['release_assets'].append({'name':asset['name'],'url':asset['browser_download_url'],'status':status,'sha256':digest(data)})
 report['release']={'tag':release['tag_name'],'url':release['html_url'],'published_at':release['published_at'],'is_latest':True}
 with sync_playwright() as p:
  browser=p.chromium.launch()
  for label,width,height in [('desktop',1365,900),('mobile',390,844)]:
   page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
   for name,route in [('home',''),('downloads','downloads.html'),('zh-reader','zh-Hans/official-v5.html'),('en-reader','en/official-v5.html')]:
    response=page.goto(SITE+route,wait_until='networkidle');assert response and response.status==200
    page.evaluate('document.fonts.ready');page.wait_for_timeout(300)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'),'Horizontal overflow: '+label+' '+route
    path=OUT/f'{label}-{name}.png';page.screenshot(path=str(path),full_page=name in ['home','downloads'])
    report['screenshots'].append(str(path))
   for lang in ['zh-Hans','en']:
    page.goto(SITE+lang+'/official-v5.html#chapter-7',wait_until='networkidle');page.wait_for_timeout(500)
    path=OUT/f'{label}-{lang}-practice.png';page.screenshot(path=str(path));report['screenshots'].append(str(path))
   page.close()
  browser.close()
 report['passed']=True

try:run()
except Exception as exc:
 report['passed']=False;report['errors'].append(repr(exc));raise
finally:
 (OUT/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
