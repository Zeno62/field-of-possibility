/* Field Lab 005. Classical names/line order are data; the integer dynamics
   below are versioned experimental rules, NOT equations from the Yijing. */
(function (root) {
'use strict';
const VERSION='field-005.1';
const TRIS=[
 ['乾',[1,1,1],'健','定向输运'],['兑',[1,1,0],'说','邻域均衡'],
 ['离',[1,0,1],'丽','释放收纳'],['震',[1,0,0],'动','局部激发'],
 ['巽',[0,1,1],'入','横向散布'],['坎',[0,1,0],'陷','循高差转移'],
 ['艮',[0,0,1],'止','截留成形'],['坤',[0,0,0],'顺','收纳暂存']
];
const TABLE=[
 [['乾',1],['夬',43],['大有',14],['大壮',34],['小畜',9],['需',5],['大畜',26],['泰',11]],
 [['履',10],['兑',58],['睽',38],['归妹',54],['中孚',61],['节',60],['损',41],['临',19]],
 [['同人',13],['革',49],['离',30],['丰',55],['家人',37],['既济',63],['贲',22],['明夷',36]],
 [['无妄',25],['随',17],['噬嗑',21],['震',51],['益',42],['屯',3],['颐',27],['复',24]],
 [['姤',44],['大过',28],['鼎',50],['恒',32],['巽',57],['井',48],['蛊',18],['升',46]],
 [['讼',6],['困',47],['未济',64],['解',40],['涣',59],['坎',29],['蒙',4],['师',7]],
 [['遁',33],['咸',31],['旅',56],['小过',62],['渐',53],['蹇',39],['艮',52],['谦',15]],
 [['否',12],['萃',45],['晋',35],['豫',16],['观',20],['比',8],['剥',23],['坤',2]]
];
const KIND=['shape','solid','mobile','store'];
const clone=x=>JSON.parse(JSON.stringify(x));
const bits=n=>Array.from({length:6},(_,i)=>(n>>i)&1);
const val=b=>b.reduce((a,v,i)=>a+(v<<i),0);
const tri=b=>TRIS.findIndex(t=>t[1].every((v,i)=>v===b[i]));
function hex(b){const l=tri(b.slice(0,3)),u=tri(b.slice(3,6));if(l<0||u<0)throw Error('Invalid six-line gua');const [name,number]=TABLE[l][u];return {name,number,lower:l,upper:u};}
function flip(b,k){if(!Number.isInteger(k)||k<0||k>5)throw Error('Line must be 0..5');const a=b.slice();a[k]^=1;return a;}
function gray(n){return bits(n^(n>>1));}
function ungray(b){let g=val(b),n=g;while(g>>=1)n^=g;return n;}
function atom(s,id,b,links=[]){s.g[id]={bits:b,links};return id;}
function num(s,id,n){if(!Number.isInteger(n)||n<0||n>63)throw Error('Out-of-range value: '+id);return atom(s,id,gray(n),['codec/gray6']);}
function read(s,id){return ungray(s.g[id].bits);}
function write(s,id,n){if(!Number.isInteger(n)||n<0||n>63)throw Error('Invalid quantity');s.g[id].bits=gray(n);}
const quantity=(s,i,k)=>read(s,`${k}/${i}`);
function canonical(s){const ordered={};for(const k of Object.keys(s.g).sort())ordered[k]=s.g[k];return JSON.stringify({version:s.version,g:ordered});}
function digest(s){let h=2166136261;for(const c of canonical(s)){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return (h>>>0).toString(16).padStart(8,'0');}
function pos(s,i){return {r:read(s,'row/'+i),c:read(s,'col/'+i)};}
function initial(rootBits=TRIS[0][1].concat(TRIS[7][1])){
 if(rootBits.length!==6||rootBits.some(b=>b!==0&&b!==1))throw Error('Invalid initial gua');
 const s={version:VERSION,g:{}};
 atom(s,'codec/gray6',[],[]);atom(s,'common',rootBits.slice());num(s,'cursor',0);num(s,'size',7);num(s,'contact-mode',1);
 const regions=[],edges=[],rules=[];
 for(let k=0;k<8;k++){const id='rule/'+k;num(s,id,k);num(s,'enabled/'+k,1);s.g[id].links.push('enabled/'+k);rules.push(id);}
 num(s,'retain-min',1);num(s,'release-max',16);num(s,'form-max',54);num(s,'solid-min',5);num(s,'exchange-gap',1);
 atom(s,'rules',[],rules.concat(['retain-min','release-max','form-max','solid-min','exchange-gap']));atom(s,'participation',[],[]);
 // Shared, fixed boundary condition for Tai/Pi: not claimed to emerge from the classics.
 for(let r=0;r<7;r++)for(let c=0;c<7;c++){
  const i=r*7+c,x=(c-3)/3,z=(r-3)/3;
  const ridge=12+29*Math.exp(-((x+.45)**2/.25+(z+.28)**2/.36))+24*Math.exp(-((x-.48)**2/.22+(z-.35)**2/.30));
  num(s,'row/'+i,r);num(s,'col/'+i,c);
  atom(s,'place/'+i,[],['row/'+i,'col/'+i]);
  const lo=TRIS[(c+2*r)%8][1],up=TRIS[(3*c+r)%8][1];
  atom(s,'shape/'+i,lo.concat(up));num(s,'solid/'+i,Math.round(ridge));num(s,'mobile/'+i,5+(c*3+r*2)%8);num(s,'store/'+i,6+(c+r)%7);
  const id='region/'+i;atom(s,id,[],KIND.map(k=>k+'/'+i).concat('place/'+i));regions.push(id);
 }
 // Genuine six-neighbour contact graph; regular embedding is a disclosed test scaffold.
 for(let i=0;i<49;i++)for(let j=i+1;j<49;j++){
  const a=pos(s,i),b=pos(s,j),dr=b.r-a.r,dc=b.c-a.c;
  const adjacent=(dr===0&&dc===1)||(dr===1&&(dc===0||dc===(a.r%2?1:-1)));
  if(adjacent){const id=`contact/${i}/${j}`;num(s,id,(Math.min(a.c,b.c)+Math.min(a.r,b.r))%3);s.g[id].links.push('region/'+i,'region/'+j,'common');edges.push(id);}
 }
 atom(s,'regions',[],regions);atom(s,'contacts',[],edges);
 // Shared references: each region participates in its row AND column organization.
 const groups=[];for(let k=0;k<7;k++){atom(s,'row-group/'+k,[],regions.filter((_,i)=>Math.floor(i/7)===k));atom(s,'col-group/'+k,[],regions.filter((_,i)=>i%7===k));groups.push('row-group/'+k,'col-group/'+k);}
 atom(s,'groups',[],groups);atom(s,'world',[],['common','regions','contacts','groups','rules','cursor','size','contact-mode','participation']);
 return s;
}
function validate(s){
 if(!s||s.version!==VERSION||!s.g||typeof s.g!=='object'||Array.isArray(s.g))throw Error('Unsupported snapshot');
 const keys=Object.keys(s.g);if(keys.length>1600||keys.includes('__proto__')||keys.includes('constructor'))throw Error('Invalid snapshot size/keys');
 const base=initial();const expected=Object.keys(base.g);
 for(const id of expected)if(!Object.hasOwn(s.g,id))throw Error('Missing gua: '+id);
 for(const id of keys){const n=s.g[id];if(!n||!Array.isArray(n.bits)||!Array.isArray(n.links)||n.bits.length>24||n.bits.some(b=>b!==0&&b!==1)||n.links.length>160||n.links.some(l=>typeof l!=='string'||!Object.hasOwn(s.g,l)))throw Error('Invalid gua: '+id);}
 for(const id of expected){if(s.g[id].bits.length!==base.g[id].bits.length)throw Error('Invalid bit width: '+id);if(id!=='participation'&&JSON.stringify(s.g[id].links)!==JSON.stringify(base.g[id].links))throw Error('Unsupported topology change: '+id);}
 if(read(s,'size')!==7||read(s,'contact-mode')>1)throw Error('Unsupported world scaffold');
 for(let i=0;i<49;i++)if(read(s,'row/'+i)!==Math.floor(i/7)||read(s,'col/'+i)!==i%7)throw Error('Invalid embedding');
 for(let k=0;k<8;k++)if(read(s,'rule/'+k)!==k||read(s,'enabled/'+k)>1)throw Error('Invalid rule registry');
 for(const id of s.g.contacts.links)if(read(s,id)>2)throw Error('Invalid port');
 const allowed=new Set(expected.concat(['player/test','input/line','input/target','input/before','input/after','participant-contact']));
 if(keys.some(id=>!allowed.has(id)))throw Error('Unknown gua in snapshot');
 return s;
}
function fromJSON(text){if(typeof text!=='string'||text.length>500000)throw Error('Snapshot too large');return validate(JSON.parse(text));}
function contactOpen(s,id){
 const links=s.g[id].links,ii=Number(links[1].split('/')[1]),jj=Number(links[2].split('/')[1]);
 const a=pos(s,ii),b=pos(s,jj),k=read(s,id),g=s.g.common.bits;
 // A contact needs at least one outward local line at its corresponding port.
 if(!s.g['shape/'+ii].bits[k]&&!s.g['shape/'+jj].bits[k])return false;
 if(read(s,'contact-mode')===0||(a.r<3)===(b.r<3))return true;
 // Experimental ordered port: a lower outward 1 faces an upper inward 0.
 return g[k]===1&&g[k+3]===0;
}
function neighbours(s,i){const out=[];for(const id of s.g.contacts.links){const ls=s.g[id].links,a=Number(ls[1].split('/')[1]),b=Number(ls[2].split('/')[1]);if(a===i||b===i)out.push({j:a===i?b:a,contact:id,open:contactOpen(s,id)});}return out.sort((a,b)=>a.j-b.j);}
function mass(s){let n=0;for(let i=0;i<49;i++)for(const k of KIND.slice(1))n+=quantity(s,i,k);return n;}
function suggest(s,i){
 const h=hex(s.g['shape/'+i].bits),op=h.upper,active=read(s,'enabled/'+op)===1;
 const v=k=>quantity(s,i,k),p=pos(s,i),ns=neighbours(s,i),open=ns.filter(n=>n.open);
 const reads=['shape/'+i,'solid/'+i,'mobile/'+i,'store/'+i,'rule/'+op,'enabled/'+op,'common','contact-mode','place/'+i,'retain-min','release-max','form-max','solid-min','exchange-gap'];
 for(const n of ns)reads.push(n.contact,'shape/'+n.j,'solid/'+n.j,'mobile/'+n.j,'place/'+n.j);
 function transfer(from,to,reason,edge=null){if(read(s,from)<1||read(s,to)>62)return null;return {from,to,reason,edge,source:i,target:edge?Number(to.split('/')[1]):i,op,reads:[...new Set(reads)]};}
 const local=(a,b,why)=>transfer(a+'/'+i,b+'/'+i,why);
 const toward=(candidates,score,reason)=>{const ranked=candidates.filter(n=>quantity(s,n.j,'mobile')<63).map(n=>({...n,score:score(n)})).filter(n=>n.score>0).sort((a,b)=>b.score-a.score||a.j-b.j);return ranked.length&&v('mobile')>0?transfer('mobile/'+i,'mobile/'+ranked[0].j,reason,ranked[0].contact):null;};
 if(!active)return {proposal:null,op,reads,reason:'此作用被测试开关停用'};
 let a=null;
 switch(op){
  case 0:a=toward(open,n=>pos(s,n.j).r>p.r?1+Math.max(0,v('mobile')-quantity(s,n.j,'mobile')):0,'乾：沿有序邻接，持续移一份');break;
  case 1:{const ranked=open.map(n=>({...n,d:v('mobile')-quantity(s,n.j,'mobile')})).filter(n=>Math.abs(n.d)>read(s,'exchange-gap')).sort((a,b)=>Math.abs(b.d)-Math.abs(a.d)||a.j-b.j);if(ranked.length){const n=ranked[0];a=transfer('mobile/'+(n.d>0?i:n.j),'mobile/'+(n.d>0?n.j:i),'兑：在可通接面双向均衡流动份额',n.contact);}break;}
  case 2:if(v('mobile')<read(s,'release-max'))a=local('store','mobile','离：在局部可显位置释放一份收纳');break;
  case 3:if(v('mobile')<read(s,'release-max')&&v('solid')>read(s,'solid-min'))a=local('solid','mobile','震：将一份成形量转为可迁移量');break;
  case 4:a=toward(open,n=>v('mobile')-quantity(s,n.j,'mobile')-read(s,'exchange-gap')+(pos(s,n.j).c>p.c?.25:0),'巽：按份额差散布；同差时偏向右侧');break;
  case 5:a=toward(open,n=>v('solid')+v('mobile')-quantity(s,n.j,'solid')-quantity(s,n.j,'mobile')-read(s,'exchange-gap'),'坎：沿当前成形量与流动量的合计高差转移');break;
  case 6:if(v('mobile')>read(s,'retain-min')&&v('solid')<read(s,'form-max'))a=local('mobile','solid','艮：截留一份流动量，使局部成形');break;
  case 7:if(v('mobile')>read(s,'retain-min'))a=local('mobile','store','坤：将一份流动量收纳于当前局部');break;
 }
 return {proposal:a,op,reads,reason:a?a.reason:'局部条件未满足，当前量不改变'};
}
function step(s){
 const i=read(s,'cursor'),oldMass=mass(s);let trace={region:i,op:null,changed:[],reads:['cursor'],reason:'调度空位，不发生事务相变',edge:null};
 if(i<49){const d=suggest(s,i);trace={region:i,op:d.op,changed:[],reads:d.reads,reason:d.reason,edge:null};if(d.proposal){const p=d.proposal,from=read(s,p.from),to=read(s,p.to);write(s,p.from,from-1);write(s,p.to,to+1);trace.changed=[{id:p.from,before:from,after:from-1},{id:p.to,before:to,after:to+1}];trace.edge=p.edge;}}
 write(s,'cursor',(i+1)%64);
 if(mass(s)!==oldMass)throw Error('Conservation invariant failed');
 return trace;
}
function advance(s,n){if(!Number.isInteger(n)||n<0||n>65536)throw Error('Invalid iteration count');const events=[],ops=Array(8).fill(0);let crossing=0;for(let k=0;k<n;k++){const t=step(s);if(t.changed.length){events.push(t);ops[t.op]++;if(t.edge){const [i,j]=t.edge.split('/').slice(1).map(Number);if((pos(s,i).r<3)!==(pos(s,j).r<3))crossing++;}}}return {events,ops,crossing};}
function intervene(s,i,k){
 if(!Number.isInteger(i)||i<0||i>48)throw Error('Invalid participant target');
 const before=s.g['shape/'+i].bits.slice(),after=flip(before,k);
 atom(s,'player/test',[1,0,1,0,1,1]);num(s,'input/line',k);num(s,'input/target',i);atom(s,'input/before',before);atom(s,'input/after',after);
 atom(s,'participant-contact',[],['player/test','region/'+i,'input/line','input/target','input/before','input/after']);s.g.participation.links=['participant-contact'];
 s.g['shape/'+i].bits=after;
 return {target:i,line:k+1,before:hex(before),after:hex(after),reason:'测试参与相经共同关系相，提交一次局部变爻'};
}
function differences(a,b){const out=[];for(let i=0;i<49;i++){const changed=KIND.filter(k=>a.g[k+'/'+i].bits.join('')!==b.g[k+'/'+i].bits.join(''));if(changed.length)out.push({region:i,changed});}return out;}
function metrics(s){const open=s.g.contacts.links.filter(id=>contactOpen(s,id)).length,counts=Array(8).fill(0);for(let i=0;i<49;i++)counts[hex(s.g['shape/'+i].bits).upper]++;return {mass:mass(s),contacts:s.g.contacts.links.length,open,regions:49,nodes:Object.keys(s.g).length,counts,hash:digest(s)};}
function snapshot(s){return canonical(s);}
const api={VERSION,TRIS,TABLE,clone,bits,val,tri,hex,flip,gray,ungray,initial,validate,fromJSON,read,write,quantity,pos,contactOpen,neighbours,suggest,step,advance,intervene,differences,metrics,snapshot,digest,mass};
if(typeof module!=='undefined'&&module.exports)module.exports=api;root.Field005=api;
})(typeof globalThis!=='undefined'?globalThis:this);
