// usage: node send.js <port> <messages.json> <outlog.jsonl> <shotsdir> [onlyIndex]
setTimeout(()=>{console.log('TIMEOUT');process.exit(1)},900000);
const fs=require('fs');
const pp=require(process.env.HOME+'/.claude/skills/lomo-likes/scripts/node_modules/puppeteer-core');
const [port,mf,logf,shots,only]=process.argv.slice(2);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const BLOCK=/checkpoint|captcha|security check|temporarily blocked|confirm (it's|that it's) you|we limit how often/i;
let msgs=JSON.parse(fs.readFileSync(mf,'utf8')); if(only!==undefined) msgs=only.split(',').map(i=>msgs[+i]);
(async()=>{
 const b=await pp.connect({browserURL:'http://localhost:'+port,defaultViewport:{width:1280,height:900}});
 const p=(await b.pages()).find(x=>x.url().includes('facebook'))||(await b.pages())[0];
 for(const [i,m] of msgs.entries()){
  await p.goto('https://www.facebook.com/marketplace/item/'+m.item_id+'/',{waitUntil:'domcontentloaded',timeout:60000}).catch(()=>{});
  await sleep(7000);
  if(BLOCK.test(await p.evaluate(()=>document.body.innerText))){console.log('STOP gate',m.seller);break}
  const vis=()=>p.evaluateHandle(()=>[...document.querySelectorAll('[role=dialog] textarea, [role=dialog] [role=textbox], textarea')].find(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0}));
  let ta=await vis();
  if(!ta.asElement()){const mb=await p.evaluateHandle(()=>[...document.querySelectorAll('[role=button]')].find(e=>(e.getAttribute('aria-label')||e.innerText).trim()==='Message'&&e.getBoundingClientRect().width>0));
   if(mb.asElement()){const q=await mb.asElement().boundingBox();await p.mouse.click(q.x+q.width/2,q.y+q.height/2);await sleep(4000);await p.screenshot({path:shots+'/'+m.token+'_dialog.png'});ta=await vis();}}
  if(!ta.asElement()){console.log('SKIP nobox',m.seller);fs.appendFileSync(logf,JSON.stringify({seller:m.seller,status:'nobox'})+'\n');continue}
  await ta.asElement().evaluate(e=>e.scrollIntoView({block:'center'})); await sleep(500);
  const bb=await ta.asElement().boundingBox(); await p.mouse.click(bb.x+bb.width/2,bb.y+bb.height/2);
  await p.keyboard.down('Meta');await p.keyboard.press('KeyA');await p.keyboard.up('Meta');await p.keyboard.press('Backspace');
  const parts=m.message_text.split('\n');
  for(const [k,line] of parts.entries()){await p.keyboard.type(line,{delay:5}); if(k<parts.length-1){await p.keyboard.down('Shift');await p.keyboard.press('Enter');await p.keyboard.up('Shift');}}
  const typed=await ta.asElement().evaluate(e=>e.value||e.textContent);
  if(!typed.includes(m.url||'vercel.app')){console.log('SKIP typed mismatch',m.seller,typed.slice(0,80));fs.appendFileSync(logf,JSON.stringify({seller:m.seller,status:'typefail'})+'\n');continue}
  const btn=await p.evaluateHandle(()=>[...document.querySelectorAll('[role="button"],button')].find(e=>/^(send message|send$|press enter to send)/i.test(e.getAttribute('aria-label')||'')&&e.getBoundingClientRect().width>0));
  if(!btn.asElement()){console.log('SKIP nobutton',m.seller);continue}
  const b2=await btn.asElement().boundingBox(); await p.mouse.click(b2.x+b2.width/2,b2.y+b2.height/2);
  await sleep(8000);
  await p.screenshot({path:shots+'/'+m.token+'_sent.png'});
  const after=await p.evaluate(()=>document.body.innerText);
  const status=BLOCK.test(after)?'gate':(/message sent|see conversation|view conversation|sent/i.test(after)?'sent':'clicked_unverified');
  const snip=(after.match(/.{0,80}(Message sent|See conversation|View conversation).{0,80}/s)||[''])[0];
  console.log(status,m.seller,JSON.stringify(snip));
  fs.appendFileSync(logf,JSON.stringify({seller:m.seller,item_id:m.item_id,token:m.token,status,at:new Date().toISOString()})+'\n');
  if(status==='gate')break;
  if(i<msgs.length-1) await sleep(60000);
 }
 process.exit(0);
})();
