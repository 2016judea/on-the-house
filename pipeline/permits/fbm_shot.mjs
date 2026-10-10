import { chromium } from 'playwright';
const toks=process.argv.slice(2);
const b=await chromium.launch();
for (const [w,h] of [[390,664],[1440,900]]){
 const p=await b.newPage({viewport:{width:w,height:h}});
 const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 for (const t of toks){ await p.goto('http://localhost:8793/for/'+t+'/'); await p.waitForTimeout(600);
  await p.screenshot({path:'/private/tmp/claude-501/-Users-aidan-Desktop-bricks/d688afbf-fdc2-490b-b20f-b66e6385dccd/scratchpad/'+t+'_'+w+'.png'});
  const r=await p.evaluate(async()=>{const s=document.getElementById('sort');const out=[];for(const o of s.options){s.value=o.value;s.dispatchEvent(new Event('change'));out.push(o.value+':'+document.querySelectorAll('#list li').length)}document.querySelectorAll('.chip')[1].click();return [document.documentElement.scrollWidth,out.join(' '),document.getElementById('count').textContent,typeof window.posthog]});
  console.log(w,t,JSON.stringify(r)); }
 console.log('errors',errs); await p.close();}
await b.close();
