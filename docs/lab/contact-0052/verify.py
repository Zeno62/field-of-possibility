"""Self-observation without user screenshots; assets are intercepted locally.
No claim of physical iPhone / Safari certification or live HTTP navigation.
"""
from pathlib import Path
from urllib.parse import urlparse
import json, re, hashlib
from playwright.sync_api import sync_playwright
HERE=Path(__file__).parent
CORE=HERE.parent/'local-dynamics-005'/'core.js'
OUT=HERE/'qa';OUT.mkdir(exist_ok=True)
HTML=(HERE/'index.html').read_text().replace('<head>','<head><base href="https://field.local/lab/contact-0052/">',1)
report={'method':'Chromium set_content + intercepted classic same-origin scripts','physical_iphone':False,'live_navigation':False,'cases':[]}

def load(browser,w,h,dpr=1,js=True,fail=None):
    ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,java_script_enabled=js)
    page=ctx.new_page();errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def handler(route):
        path=urlparse(route.request.url).path;requests.append(path)
        if fail and path.endswith('/'+fail):route.abort();return
        p=CORE if path.endswith('/local-dynamics-005/core.js') else HERE/Path(path).name
        if not p.is_file():route.fulfill(status=404,body='not found');return
        route.fulfill(status=200,content_type='text/javascript; charset=utf-8',body=p.read_bytes())
    page.route('**/*',handler)
    page.set_content(HTML,wait_until='load')
    if js and not fail:page.wait_for_selector('html[data-ready="true"]',timeout=10000)
    return ctx,page,errors,requests

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    report['browser']=browser.version
    for w,h,dpr in [(1440,1080,1),(390,844,3),(320,568,2),(430,932,3),(844,390,1)]:
        ctx,p,errors,req=load(browser,w,h,dpr)
        assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(w,'overflow')
        # Confirm actual paint, not only canvas dimensions.
        paint=p.evaluate("""()=>{const c=document.getElementById('canvasA'),a=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<a.length;i+=4)if(a[i]<150&&a[i+3]>0)n++;return {darkPixels:n,width:c.width,height:c.height};}""")
        assert paint['darkPixels']>500,paint
        snapshots=p.evaluate('__LAB.snapshot()')
        p.locator('#line2').click();assert p.evaluate('__LAB.snapshot()')==snapshots
        # Default test fixture is R19, fourth line, Dui -> Jie.
        p.locator('#line3').click();p.locator('#commit').click()
        after=p.evaluate('__LAB.N.differences(...__LAB.worlds)');assert len(after['regions'])==1 and len(after['gates'])==0
        p.locator('#sixteen').click();p.wait_for_function('!__LAB.busy',timeout=15000)
        m=p.evaluate('__LAB.metrics()');assert m[0]['mass']==m[1]['mass']==1851
        if w<761:
            p.locator('#tabB').click();assert p.locator('#panelB').is_visible() and not p.locator('#panelA').is_visible()
        p.screenshot(path=str(OUT/f'view-{w}.png'),full_page=True)
        # Camera motion and view changes must be display-only.
        before=p.evaluate('__LAB.snapshot()');canvas=p.locator('#canvasB' if w<761 else '#canvasA');box=canvas.bounding_box()
        p.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.5);p.mouse.down();p.mouse.move(box['x']+box['width']*.65,box['y']+box['height']*.58,steps=8);p.mouse.up();assert p.evaluate('__LAB.snapshot()')==before
        p.locator('#network').click();assert p.evaluate('__LAB.snapshot()')==before
        if w in (1440,390):p.screenshot(path=str(OUT/f'network-{w}.png'),full_page=True)
        # Real file-input restoration, not a shortcut to state assignment.
        saved=p.evaluate('__LAB.N.snapshot(__LAB.worlds[1])');f=OUT/f'snapshot-{w}.json';f.write_text(saved)
        p.locator('#one').click();p.wait_for_function('!__LAB.busy')
        p.locator('#file').set_input_files(str(f));p.wait_for_function('document.getElementById("message").textContent.includes("已恢复")')
        assert p.evaluate('__LAB.N.snapshot(__LAB.worlds[1])')==saved
        # Pause/resume and mobile compare presets.
        p.locator('#run').click();p.wait_for_function('__LAB.steps>1088');p.locator('#run').click();stop=p.evaluate('__LAB.steps');p.wait_for_timeout(300);assert p.evaluate('__LAB.steps')==stop
        p.locator('#mode').select_option('tai-pi');assert p.evaluate('__LAB.N.F.hex(__LAB.worlds[1].g.common.bits).name')=='否'
        assert not errors,errors;assert len(req)==3,req
        report['cases'].append({'viewport':[w,h],'dpr':dpr,'pass':True,'paint':paint,'requests':req,'errors':errors,'metricsAfter16Rounds':m})
        ctx.close()
    # Two matched 64-round worlds for the main evidence images.
    ctx,p,errors,req=load(browser,1440,1080)
    p.locator('#commit').click();p.evaluate('__LAB.advance(4096)');p.screenshot(path=str(OUT/'desktop-64-rounds.png'),full_page=True)
    p.locator('#network').click();p.screenshot(path=str(OUT/'network-64-rounds.png'),full_page=True)
    report['at64Rounds']=p.evaluate('__LAB.metrics()');ctx.close()
    ctx,p,errors,req=load(browser,390,844,3);p.locator('#commit').click();p.evaluate('__LAB.advance(4096)');p.locator('#tabB').click();p.screenshot(path=str(OUT/'mobile-64-rounds.png'),full_page=True);ctx.close()
    ctx,p,errors,req=load(browser,390,844,js=False);assert p.locator('#fallback').is_visible();assert not p.locator('.live').is_visible();report['noJavaScriptFallback']=True;ctx.close()
    ctx,p,errors,req=load(browser,390,844,fail='app.js');assert p.locator('#fallback').is_visible();assert '未加载' in p.locator('#status').inner_text();report['scriptFailureFallback']=True;ctx.close()
    # Explicit Canvas-failure test, including fallback surviving partial setup.
    ctx=browser.new_context(viewport={'width':390,'height':844});p=ctx.new_page();p.evaluate('HTMLCanvasElement.prototype.getContext=()=>null')
    text=HTML
    for url,file in [('../local-dynamics-005/core.js?v=e7bf6be',CORE),('contact.js?v=0052-1',HERE/'contact.js'),('app.js?v=0052-1',HERE/'app.js')]:
        text=text.replace(f'<script src="{url}" onerror="loadError()"></script>','<script>'+file.read_text()+'</script>')
    p.set_content(text,wait_until='load');assert p.locator('#fallback').is_visible();assert p.locator('html').get_attribute('data-ready')=='false';report['canvasFailureFallback']=True;ctx.close()
    browser.close()
report['assetSha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [CORE,HERE/'index.html',HERE/'contact.js',HERE/'app.js']}
report['runtimeBytes']=sum(p.stat().st_size for p in [CORE,HERE/'index.html',HERE/'contact.js',HERE/'app.js'])
(OUT/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'cases':len(report['cases']),'browser':report['browser'],'runtimeBytes':report['runtimeBytes'],'at64Rounds':report['at64Rounds']},ensure_ascii=False))
