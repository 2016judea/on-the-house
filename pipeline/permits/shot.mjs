import { chromium } from 'playwright';
const b=await chromium.launch(); const p=await b.newPage({viewport:{width:390,height:664},deviceScaleFactor:2});
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
for (const s of ['survhey','treforge','bestlatech']){ await p.goto(`http://localhost:8765/${s}/`); await p.waitForTimeout(800);
 await p.screenshot({path:`out/${s}.png`,fullPage:false});
 console.log(s, await p.evaluate(()=>[document.querySelectorAll('#list li').length, document.documentElement.scrollWidth]));}
console.log('errors',errs); await b.close();
