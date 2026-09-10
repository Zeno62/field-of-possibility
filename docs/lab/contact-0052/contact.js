/* Field 005.2: an auditable contact-state experiment built on the frozen 005.1 core.
   Thresholds and contact hysteresis below are authored rules, not classical physics. */
(function(root){'use strict';
const F=root.Field005||(typeof require==='function'?require('../local-dynamics-005/core.js'):null);
if(!F||F.VERSION!=='field-005.1')throw Error('Requires Field 005.1 core');
const VERSION='field-contact-005.2';
const gid=id=>'gate/'+id.slice('contact/'.length);
const ends=id=>id.split('/').slice(1).map(Number);
const number=(s,id,n,refs=[])=>s.g[id]={bits:F.gray(n),links:['codec/gray6',...refs]};
function initial(common,dynamic=1){
 const s=F.initial(common);s.version=VERSION;
 number(s,'gate-mode',dynamic);number(s,'gate-open-gap',4);number(s,'gate-close-gap',1);
 const gs=[];for(const id of s.g.contacts.links){const g=gid(id);number(s,g,0,[id,'gate-open-gap','gate-close-gap']);gs.push(g);}
 s.g['gate-model']={bits:[],links:['gate-mode','gate-open-gap','gate-close-gap',...gs]};s.g.world.links.push('gate-model');return s;
}
function snapshot(s){const g={};for(const id of Object.keys(s.g).sort())g[id]={bits:s.g[id].bits.slice(),links:s.g[id].links.slice()};return JSON.stringify({version:VERSION,g});}
function validate(s){
 if(!s||s.version!==VERSION||!s.g||Array.isArray(s.g)||typeof s.g!=='object')throw Error('不是本版本的当前相');
 if(Object.keys(s).some(k=>!['version','g'].includes(k)))throw Error('快照不接受历史或缓存字段');
 const template=initial(),keys=Object.keys(s.g),ext=Object.keys(template.g).filter(k=>k.startsWith('gate'));
 if(keys.length>800)throw Error('快照超出实验规模');
 for(const id of keys){const n=s.g[id];if(!n||Object.keys(n).sort().join(',')!=='bits,links'||!Array.isArray(n.bits)||!Array.isArray(n.links)||n.bits.length>6||n.bits.some(b=>b!==0&&b!==1)||n.links.length>160||n.links.some(r=>typeof r!=='string'||!Object.hasOwn(s.g,r)))throw Error('无效卦记录：'+id);}
 for(const id of ext){const a=s.g[id],b=template.g[id];if(!a||a.bits.length!==b.bits.length||JSON.stringify(a.links)!==JSON.stringify(b.links))throw Error('接触模型结构不匹配：'+id);}
 if(JSON.stringify(s.g.world.links)!==JSON.stringify(template.g.world.links))throw Error('世界引用不匹配');
 if(F.read(s,'gate-mode')>1||F.read(s,'gate-close-gap')>=F.read(s,'gate-open-gap'))throw Error('开闭条件必须有间隔');
 for(const id of s.g.contacts.links)if(F.read(s,gid(id))>1)throw Error('开闭位只能是 0/1');
 const b=F.clone(s);b.version=F.VERSION;b.g.world.links=b.g.world.links.filter(k=>k!=='gate-model');for(const k of ext)delete b.g[k];F.validate(b);
 const part=['player/test','input/line','input/target','input/before','input/after','participant-contact'];
 if(s.g.participation.links.length){
  if(s.g.participation.links.join('')!=='participant-contact'||part.some(k=>!s.g[k]))throw Error('参入相不完整');
  for(const k of part.filter(x=>x!=='participant-contact'))if(s.g[k].bits.length!==6)throw Error('参入编码宽度不匹配');
  if(F.read(s,'input/line')>5||F.read(s,'input/target')>48)throw Error('参入位置越界');
  const target=F.read(s,'input/target'),k=F.read(s,'input/line');
  if(s.g['participant-contact'].links.join('|')!==['player/test','region/'+target,'input/line','input/target','input/before','input/after'].join('|')||F.flip(s.g['input/before'].bits,k).join('')!==s.g['input/after'].bits.join(''))throw Error('参入关系不一致');
 }else if(part.some(k=>s.g[k]))throw Error('孤立参入记录');
 return s;
}
function restore(text){if(typeof text!=='string'||text.length>500000)throw Error('快照过大');return validate(JSON.parse(text));}
function detail(s,id){
 if(!s.g.contacts.links.includes(id))throw Error('未知接面');
 const [a,b]=ends(id),latched=F.read(s,gid(id)),eligible=F.contactOpen(s,id),gap=Math.abs(F.quantity(s,a,'mobile')-F.quantity(s,b,'mobile'));
 const on=F.read(s,'gate-open-gap'),off=F.read(s,'gate-close-gap');let next=latched;
 if(!eligible||gap<=off)next=0;else if(gap>=on)next=1;
 return {id,a,b,eligible,latched,gap,on,off,next,open:eligible&&(F.read(s,'gate-mode')===0||latched===1),reads:[id,gid(id),'gate-mode','gate-open-gap','gate-close-gap','common','contact-mode','shape/'+a,'shape/'+b,'mobile/'+a,'mobile/'+b,'row/'+a,'row/'+b]};
}
function contacts(s){return s.g.contacts.links.map(id=>detail(s,id));}
function inspect(s,i){
 if(!Number.isInteger(i)||i<0||i>48)throw Error('区域越界');
 const local=F.neighbours(s,i).map(n=>detail(s,n.contact));const dependencies=[...new Set(local.flatMap(d=>d.reads))];
 if(F.read(s,'gate-mode')){const change=local.find(d=>d.next!==d.latched);if(change)return {kind:change.next?'open':'close',region:i,op:null,gate:change,changed:[{id:gid(change.id),before:change.latched,after:change.next}],reads:change.reads,reason:!change.eligible?'对应端口条件不成立，关闭接面':change.next?`局部流动差 ${change.gap} ≥ 开启条件 ${change.on}`:`局部流动差 ${change.gap} ≤ 关闭条件 ${change.off}`};}
 // A read-only derived view filters contacts. Nothing in the source graph is mutated.
 const ids=F.read(s,'gate-mode')?s.g.contacts.links.filter(id=>F.read(s,gid(id))===1):s.g.contacts.links;
 const view={version:F.VERSION,g:{...s.g,contacts:{bits:[],links:ids}}};
 const d=F.suggest(view,i);return {kind:d.proposal?'transfer':'idle',region:i,op:d.op,proposal:d.proposal,changed:[],reads:[...new Set([...d.reads,...dependencies])],reason:d.reason};
}
function step(s){
 const i=F.read(s,'cursor'),total=F.mass(s);let t={kind:'idle',region:i,op:null,changed:[],reads:['cursor'],reason:'调度空位',edge:null};
 if(i<49){t=inspect(s,i);t.edge=null;
  if(t.gate){const d=t.gate;F.write(s,gid(d.id),d.next);t.edge=d.id;}
  else if(t.proposal){const p=t.proposal,a=F.read(s,p.from),b=F.read(s,p.to);F.write(s,p.from,a-1);F.write(s,p.to,b+1);t.changed=[{id:p.from,before:a,after:a-1},{id:p.to,before:b,after:b+1}];t.edge=p.edge;}
 }
 F.write(s,'cursor',(i+1)%64);if(F.mass(s)!==total)throw Error('份额守恒失败');return t;
}
function advance(s,n){if(!Number.isInteger(n)||n<0||n>65536)throw Error('步数越界');const out={open:0,close:0,transfer:0,idle:0,crossing:0,ops:Array(8).fill(0),tail:[]};for(let j=0;j<n;j++){const t=step(s);out[t.kind]++;if(t.kind==='transfer'){out.ops[t.op]++;if(t.edge){const [a,b]=ends(t.edge);if((F.pos(s,a).r<3)!==(F.pos(s,b).r<3))out.crossing++;}}if(t.changed.length){out.tail.push(t);if(out.tail.length>8)out.tail.shift();}}return out;}
function components(s){const ds=contacts(s),adj=Array.from({length:49},()=>[]);for(const d of ds)if(d.open){adj[d.a].push(d.b);adj[d.b].push(d.a);}const seen=new Set(),out=[];for(let i=0;i<49;i++)if(!seen.has(i)){const todo=[i],members=[];seen.add(i);while(todo.length){const n=todo.pop();members.push(n);for(const j of adj[n])if(!seen.has(j)){seen.add(j);todo.push(j);}}members.sort((a,b)=>a-b);const set=new Set(members),links=members.map(n=>'region/'+n).concat(ds.filter(d=>d.open&&set.has(d.a)&&set.has(d.b)).map(d=>gid(d.id)));out.push({bits:[],links,members});}return out.sort((a,b)=>b.members.length-a.members.length||a.members[0]-b.members[0]);}
function metrics(s){const ds=contacts(s),c=components(s);return {mass:F.mass(s),open:ds.filter(d=>d.open).length,eligible:ds.filter(d=>d.eligible).length,groups:c.length,largest:c[0].members.length,nodes:Object.keys(s.g).length};}
function differences(a,b){return {regions:F.differences(a,b),gates:a.g.contacts.links.filter(id=>F.read(a,gid(id))!==F.read(b,gid(id)))};}
const api={VERSION,F,initial,snapshot,validate,restore,detail,contacts,inspect,step,advance,components,metrics,differences,gid,ends};
root.FieldContact=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
