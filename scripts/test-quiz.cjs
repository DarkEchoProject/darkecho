const test=require('node:test');
const assert=require('node:assert/strict');
const quiz=require('../assets/quiz-tools.js');

test('a new attempt has no answers and no score',()=>{
  const state=quiz.create(5);assert.equal(quiz.score(state),0);assert.equal(quiz.complete(state),false);
});
test('false answers are compared as booleans',()=>{
  assert.equal(quiz.score(quiz.record(quiz.create(1),0,false,false)),1);
  assert.equal(quiz.score(quiz.record(quiz.create(1),0,true,false)),0);
});
test('checking an answer twice cannot inflate the score',()=>{
  const state=quiz.record(quiz.create(5),0,true,true);
  assert.throws(()=>quiz.record(state,0,true,true),RangeError);assert.equal(quiz.score(state),1);
});
test('questions must be answered in order and within the attempt',()=>{
  assert.throws(()=>quiz.record(quiz.create(5),2,true,true),RangeError);
  const done=quiz.record(quiz.create(1),0,true,true);
  assert.throws(()=>quiz.record(done,1,true,true),RangeError);
});
test('a five-question mixed attempt has a bounded reproducible result',()=>{
  let state=quiz.create(5);
  for(const [i,choice] of [true,false,false,true,true].entries())state=quiz.record(state,i,choice,true);
  assert.equal(quiz.score(state),3);assert.equal(quiz.complete(state),true);
  assert.deepEqual(state.answers,[true,false,false,true,true]);
});
test('answering does not mutate a previous attempt state',()=>{
  const initial=quiz.create(5);quiz.record(initial,0,true,true);assert.deepEqual(initial.answers,[]);
});
test('malformed totals and string answers are rejected',()=>{
  for(const total of [0,-1,1.5,NaN,101,'5'])assert.throws(()=>quiz.create(total),TypeError);
  assert.throws(()=>quiz.record(quiz.create(5),0,'false',false),TypeError);
});
