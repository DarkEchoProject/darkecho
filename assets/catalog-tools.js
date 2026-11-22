/* Pure helpers shared by the browser and the regression checks. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.DarkEchoCatalog=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function normalize(value){
    return String(value??'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase()
      .replace(/['’‘ʻʼ`]/g,'').replace(/[^\p{L}\p{N}]+/gu,' ').trim();
  }
  function matches(text,query){
    const normalized=normalize(text),words=normalize(query).split(' ').filter(Boolean);
    return words.every(word=>normalized.includes(word));
  }
  function cleanSaved(value,allowed){
    if(!Array.isArray(value))return [];
    const ids=value.filter(id=>typeof id==='string'&&/^[A-Za-z0-9_-]{11}$/.test(id)&&(!allowed||allowed.has(id)));
    return [...new Set(ids)].slice(0,200);
  }
  function parseSaved(raw){
    if(typeof raw!=='string'||raw.length>20000)return [];
    try{return cleanSaved(JSON.parse(raw));}catch(_){return [];}
  }
  return Object.freeze({normalize,matches,cleanSaved,parseSaved});
});
