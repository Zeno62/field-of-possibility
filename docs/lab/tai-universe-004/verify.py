"""Self-contained lab 004 QA. Requires playwright + Pillow, Chromium (CHROMIUM env).
Run: python verify.py --html index.html --out qa
Optional --url permits testing a deployed HTTPS URL when network access is available.
No network is needed for local content tests. Device emulation != physical iPhone.
"""
import argparse, hashlib, json, os, time
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

def run():
    parser=argparse.ArgumentParser()
    parser.add_argument('--html',default=str(Path(__file__).with_name('index.html')))
    parser.add_argument('--out',default=str(Path(__file__).with_name('qa')))
    parser.add_argument('--url',default=None)
    args=parser.parse_args()
    root=Path(args.out);root.mkdir(parents=True,exist_ok=True)
    html=Path(args.html).read_text()
    report={'build':'0.4.0','html_sha256':hashlib.sha256(html.encode()).hexdigest(), 'html_bytes':len(html.encode()),'delivery':'deployed-url' if args.url else 'local HTML via browser set_content','tests':[], 'viewports':[], 'boundaries':['Chromium only; not physical iPhone or Safari/WebKit certification.','This is dependency/projection validation, not proof of Yijing-derived physics.']}
    def check(name,cond,detail=None):
        report['tests'].append({'name':name,'pass':bool(cond),'detail':detail})
        if not cond: print('FAIL',name,detail)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        report['browser']=browser.version
        def load(page):
            if args.url:page.goto(args.url,wait_until='networkidle')
            else:page.set_content(html,wait_until='load')
            page.wait_for_function("document.documentElement.dataset.ready === 'true'",timeout=20000)
            page.wait_for_timeout(150)
        context=browser.new_context(viewport={'width':1440,'height':1100},device_scale_factor=1)
        page=context.new_page();errors=[];requests=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.on('request',lambda r:requests.append(r.url))
        t=time.perf_counter();load(page)
        report['initialization_ms_local']=round((time.perf_counter()-t)*1000)
        report['model']=page.evaluate('FieldLab.checks')
        check('33 model groups pass',report['model']['passed']==report['model']['total']==33)
        check('no external asset requests',len(requests)==(1 if args.url else 0),requests)
        before=page.evaluate('FieldLab.signature')
        page.screenshot(path=str(root/'desktop-before.png'),full_page=True)
        page.locator('#canvas-c').screenshot(path=str(root/'control-before.png'))
        for k in range(1,7):page.click(f'[data-line="{k}"]')
        check('all six line inspections leave state unchanged',before==page.evaluate('FieldLab.signature'))
        page.click('[data-line="2"]');page.click('#commit');page.wait_for_timeout(150)
        changed=page.evaluate('FieldLab.signature');metrics=page.evaluate('FieldLab.metrics')
        check('shared one-line action updates A/B but not C',[metrics[x]['paths'] for x in ['a','b','c']]==[5,5,6],metrics)
        report['single_line_audit']=page.evaluate('FieldLab.audit')
        page.screenshot(path=str(root/'desktop-after.png'),full_page=True)
        page.locator('#canvas-c').screenshot(path=str(root/'control-after.png'))
        equal=ImageChops.difference(Image.open(root/'control-before.png'),Image.open(root/'control-after.png')).getbbox() is None
        check('control C canvas pixel-identical before/after',equal)
        with page.expect_download() as event:
            page.locator('summary').filter(has_text='当前相存档与重建').click()
            page.click('#export')
        download=event.value;download.save_as(root/'current-graph.json')
        saved=(root/'current-graph.json').read_text()
        check('current graph export contains no event log',not any(k in json.loads(saved) for k in ['history','audit','events','cache']))
        page.click('#restore-current');check('cache/log free rebuild is equivalent',changed==page.evaluate('FieldLab.signature'))
        page.click('#commit');expected=page.evaluate('FieldLab.signature')
        page.set_input_files('#import',str(root/'current-graph.json'))
        page.wait_for_function("document.getElementById('restore-result').textContent.includes('已由当前卦网恢复')")
        check('file import restores previous state',changed==page.evaluate('FieldLab.signature'))
        page.click('#commit');check('restore then continue matches uninterrupted run',expected==page.evaluate('FieldLab.signature'))
        # Fresh browser, without any old UI/history/cache.
        fresh=browser.new_page(viewport={'width':1440,'height':1100});load(fresh)
        fresh.evaluate('(s)=>FieldLab.importDoc(s)',saved)
        check('fresh page restoration matches saved state',fresh.evaluate('FieldLab.signature')==changed)
        fresh.close()
        # Reject malformed snapshot, preserving current world.
        bad=json.loads(saved);bad['records'][0]['bits']='1111';(root/'invalid.json').write_text(json.dumps(bad))
        before_bad=page.evaluate('FieldLab.signature');page.set_input_files('#import',str(root/'invalid.json'))
        page.wait_for_function("document.getElementById('restore-result').textContent.startsWith('未载入')")
        check('bad import rejected without replacing state',page.evaluate('FieldLab.signature')==before_bad)
        page.click('#reset-world');page.click('[data-root="56"]')
        check('Pi high-level condition closes all branches',all(v['paths']==0 for v in page.evaluate('FieldLab.metrics').values()))
        page.click('#commit');page.click('[data-root="7"]')
        check('local changes survive high-level condition swap',[v['paths'] for v in page.evaluate('FieldLab.metrics').values()]==[5,5,6])
        page.screenshot(path=str(root/'tai-after-context-swap.png'),full_page=True)
        # Numeric property must causally affect outputs.
        page.click('#reset-world');page.click('[data-root="3"]')
        doc=page.evaluate('FieldLab.snapshot')
        for record in doc['records']:
            if record['id']=='threshold.value':record['bits']='101'
        page.evaluate('(x)=>FieldLab.importDoc(JSON.stringify(x))',doc)
        check('number gua threshold participates in output',all(v['paths']==0 for v in page.evaluate('FieldLab.metrics').values()))
        page.click('#reset-world');page.click('#commit');before_camera=page.evaluate('FieldLab.signature')
        box=page.locator('#canvas-a').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
        page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+65,y+20,steps=10);page.mouse.up()
        page.click('#zoom-in');page.click('#zoom-out');page.locator('#canvas-a').focus();page.keyboard.press('ArrowLeft')
        check('drag/zoom/keyboard camera do not alter gua',page.evaluate('FieldLab.signature')==before_camera)
        page.click('#reset-view')
        page.select_option('#inspect','threshold')
        check('attribute/value/rule provenance exposed',all(s in page.locator('#trace').inner_text() for s in ['threshold.value','attribute.threshold','rule.CONCAT']))
        page.select_option('#inspect','a.open.1')
        check('passage provenance reaches shared source and common root',all(s in page.locator('#trace').inner_text() for s in ['shared','root','reference','position.1']))
        check('desktop no runtime errors',not errors,errors)
        # Responsive/touch/landscape tests.
        for width,height,dpr,mobile in [(320,568,2,True),(390,844,3,True),(430,932,3,True),(844,390,2,True),(1024,768,1,False)]:
            ctx=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=dpr,is_mobile=mobile,has_touch=mobile,reduced_motion='reduce')
            p=ctx.new_page();errs=[];p.on('pageerror',lambda er:errs.append(str(er)));load(p)
            p.click('#commit');p.wait_for_timeout(100)
            overflow=p.evaluate('document.documentElement.scrollWidth>innerWidth')
            check(f'{width}x{height}: no horizontal overflow',not overflow)
            if width<=820:
                sig=p.evaluate('FieldLab.signature')
                for region in ['b','c','a']:
                    p.click(f'.tabs [data-region="{region}"]');p.wait_for_timeout(100)
                    check(f'{width}x{height}: {region} visible canvas',p.locator(f'#world-{region}').is_visible() and p.locator(f'#canvas-{region}').evaluate("c=>c.width>100 && c.parentElement.classList.contains('ready')"))
                check(f'{width}x{height}: tab changes leave state unchanged',p.evaluate('FieldLab.signature')==sig)
                # Inject real Chromium touch input through CDP, not DOM event stubs.
                box=p.locator('#canvas-a').bounding_box()
                cx=box['x']+box['width']/2;cy=box['y']+box['height']/2
                initial_zoom=p.evaluate('FieldLab.camera.zoom')
                session=ctx.new_cdp_session(p)
                session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':cx-30,'y':cy,'id':1},{'x':cx+30,'y':cy,'id':2}]})
                session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':cx-50,'y':cy,'id':1},{'x':cx+50,'y':cy,'id':2}]})
                session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
                p.wait_for_timeout(100)
                check(f'{width}x{height}: touch pinch changes zoom',p.evaluate('FieldLab.camera.zoom')!=initial_zoom)
                check(f'{width}x{height}: pinch preserves current gua',p.evaluate('FieldLab.signature')==sig)
                p.click('#reset-view');p.wait_for_timeout(100)
            check(f'{width}x{height}: no JS errors',not errs,errs)
            report['viewports'].append({'width':width,'height':height,'dpr':dpr,'is_mobile_emulation':mobile,'errors':errs})
            if width==390:p.screenshot(path=str(root/'mobile-after.png'),full_page=True)
            if width==844:p.screenshot(path=str(root/'landscape-after.png'),full_page=True)
            ctx.close()
        # Disabled JS: fixed diagram, explicit note, controls disabled.
        nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        p=nojs.new_page();p.set_content(html)
        check('no-JS preview is visible and explicitly static',p.locator('#fallback').is_visible() and p.locator('#world-a .still').is_visible() and p.locator('#commit').is_disabled())
        p.screenshot(path=str(root/'mobile-no-js.png'),full_page=True);nojs.close()
        # Canvas failure shows error rather than falsely claiming READY.
        p=browser.new_page(viewport={'width':390,'height':844})
        broken=html.replace('<!-- unused -->','')
        broken=broken.replace('<script>','<script>HTMLCanvasElement.prototype.getContext=function(){return null;};</script><script>',1)
        p.set_content(broken,wait_until='load');p.wait_for_timeout(400)
        check('Canvas unavailable is reported, with static fallback',p.evaluate("document.documentElement.dataset.ready==='error'") and p.locator('#fallback').is_visible())
        p.close();context.close();browser.close()
    report['passed']=sum(x['pass'] for x in report['tests']);report['total']=len(report['tests'])
    (root/'self-check-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'passed':report['passed'],'total':report['total'],'model':report['model']['passed'],'init_ms':report['initialization_ms_local']},ensure_ascii=False))
    return 0 if report['passed']==report['total'] else 1
if __name__=='__main__':raise SystemExit(run())
