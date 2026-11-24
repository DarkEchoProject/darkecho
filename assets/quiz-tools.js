/* A small immutable state machine shared by the browser and regression checks. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.DarkEchoQuiz=api;
})(typeof window!=='undefined'?window:globalThis,function(){
  'use strict';
  function create(total){
    if(!Number.isInteger(total)||total<1||total>100)throw new TypeError('Invalid question count');
    return {total,answers:[]};
  }
  function record(state,index,choice,answer){
    if(!Number.isInteger(index)||index!==state.answers.length||index>=state.total)throw new RangeError('Answer questions once, in order');
    if(typeof choice!=='boolean'||typeof answer!=='boolean')throw new TypeError('Answers must be booleans');
    return {total:state.total,answers:[...state.answers,choice===answer]};
  }
  const score=state=>state.answers.reduce((total,correct)=>total+(correct?1:0),0);
  const complete=state=>state.answers.length===state.total;
  return {create,record,score,complete};
});
