"""Reproducible Lab 005 tests. Browser network navigation is optional.
Run: python verify.py. Requires Playwright + Chromium, no JS dependencies.
Tests bundle the exact local classic scripts into HTML to avoid CDN/network needs.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, hashlib, time
OUT=Path(__file__).resolve().parent
html=(OUT/'index.html').read_text()
for name in ['core','checks','app']:
 html=html.replace(f'<script src="{name}.js?v=0051"></script>','<script>'+ (OUT/f'{name}.js').read_text()+'</script>')
rows=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for name,w,h,dpr,mobile in [('desktop',1440,1100,1,False),('mobile',390,844,3,True),('narrow',320,568,2,True),('wide-phone',430,932,3,True),('landscape',844,390,2,True)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,is_mobile=mobile,has_touch=mobile)
  page=ctx.new_page();page.set_default_timeout(5000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content(html,wait_until='load')
  page.wait_for_function("document.documentElement.dataset.ready==='true'")
  hash0=page.evaluate("window.__FIELD005__.hash('B')")
  page.locator('#lineControls button').nth(0).click()
  readonly=page.evaluate("window.__FIELD005__.hash('B')")==hash0
  page.evaluate("window.__FIELD005__.select(19,3)")
  before=page.evaluate("window.__FIELD005__.metrics()")
  page.locator('#commit').click()
  after=page.evaluate("window.__FIELD005__.metrics()")
  start=time.perf_counter();page.locator('#many').click();runtime=(time.perf_counter()-start)*1000
  metrics=page.evaluate("window.__FIELD005__.metrics()")
  overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
  painted=page.evaluate("(()=>{const c=document.getElementById('canvasB'),a=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<a.length;i+=4)if(a[i]<200)n++;return n;})()")
  dragHash=page.evaluate("window.__FIELD005__.hash('B')")
  box=page.locator('#canvasB').bounding_box()
  page.mouse.move(box['x']+box['width']*.45,box['y']+box['height']*.55)
  page.mouse.down();page.mouse.move(box['x']+box['width']*.55,box['y']+box['height']*.59,steps=4);page.mouse.up()
  noViewMutation=page.evaluate("window.__FIELD005__.hash('B')")==dragHash
  page.locator('#view').click()
  if mobile and w<=760:
   page.locator('#tabA').click();page.locator('#tabB').click()
  if name in ('desktop','mobile','narrow'):
   page.screenshot(path=str(OUT/f'{name}.png'),full_page=True)
  if name=='desktop':
   page.locator('.worlds').screenshot(path=str(OUT/'comparison-16-rounds.png'))
   state=page.evaluate("window.Field005.snapshot(window.__FIELD005__.state('B'))")
   (OUT/'current-snapshot.json').write_text(state)
   # Import current state into a new baseline without logs, via real file input.
   page.locator('#file').set_input_files(str(OUT/'current-snapshot.json'))
   page.wait_for_function("document.getElementById('notice').textContent.includes('已恢复')")
   imported=page.evaluate("window.__FIELD005__.metrics()")
   assert imported['diff']==0
   page.locator('#many').click()
   assert page.evaluate("window.__FIELD005__.metrics().diff")==0
   # Actual pause, play and resume; no camera-induced writes.
   page.locator('#play').click();page.wait_for_timeout(500);page.locator('#play').click()
   paused=page.evaluate("window.__FIELD005__.hash('B')");page.wait_for_timeout(350)
   assert paused==page.evaluate("window.__FIELD005__.hash('B')")
   start=time.perf_counter();report=page.evaluate("window.__FIELD005__.checks()")
   report['browserSeconds']=time.perf_counter()-start
   assert report['passed']==report['total']
   (OUT/'model-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
   # Same renderer, pristine root comparison after 64 rounds.
   page.evaluate("window.__FIELD005__.reset([1,1,1,0,0,0]);window.__FIELD005__.advance(4096)")
   tai=page.evaluate("window.__FIELD005__.metrics()")
   page.locator('#panelA').screenshot(path=str(OUT/'tai-64-rounds.png'))
   page.evaluate("window.__FIELD005__.reset([0,0,0,1,1,1]);window.__FIELD005__.advance(4096)")
   pi=page.evaluate("window.__FIELD005__.metrics()")
   page.locator('#panelA').screenshot(path=str(OUT/'pi-64-rounds.png'))
   (OUT/'tai-pi-measurements.json').write_text(json.dumps({'tai':tai,'pi':pi},ensure_ascii=False,indent=2))
  assert readonly and noViewMutation and not overflow and painted>1000 and not errors
  assert before['diff']==0 and after['diff']==1 and metrics['diff']==16
  assert metrics['A']['mass']==metrics['B']['mass']==1851
  rows.append({'viewport':name,'width':w,'height':h,'dpr':dpr,'javascriptErrors':errors,'horizontalOverflow':overflow,'paintedDarkPixels':painted,'previewReadOnly':readonly,'cameraReadOnly':noViewMutation,'diffAtCommit':after['diff'],'diffAt16Rounds':metrics['diff'],'advance16RoundsBrowserMs':round(runtime,2)})
  ctx.close()
 # JS-off fallback genuinely exists.
 ctx=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
 page=ctx.new_page();page.set_content(html)
 assert page.locator('noscript').inner_text().strip()
 page.screenshot(path=str(OUT/'no-js.png'),full_page=True)
 ctx.close();browser.close()
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.js')}
files['index.html']=hashlib.sha256((OUT/'index.html').read_bytes()).hexdigest()
result={'model':'field-005.1','sourceSha256':files,'browserTests':rows,'noJsFallback':True,'method':'Chromium set_content with inline copies of the exact local classic scripts; actual online navigation blocked by environment policy','notTested':['physical iPhone Safari','WebKit browser','multiuser backend','personal information mapping'],'allPassed':True}
(OUT/'self-check-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'allPassed':True,'modelChecks':report['passed'],'browserCases':len(rows),'timings':[r['advance16RoundsBrowserMs'] for r in rows]},ensure_ascii=False))
