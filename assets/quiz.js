/* Answers are page-local. A result is shared only after the visitor chooses it. */
(() => {
  'use strict';
  const root=document.querySelector('[data-quiz]'),engine=window.DarkEchoQuiz;
  if(!root||!engine)return;
  const ar=root.dataset.lang==='ar';
  const tr=(en,arabic)=>ar?arabic:en;
  const questions=[...root.querySelectorAll('[data-quiz-question]')];
  const group=root.querySelector('[data-quiz-questions]');
  const controls=[...root.querySelectorAll('[data-quiz-controls]')];
  const check=root.querySelector('[data-quiz-check]'),next=root.querySelector('[data-quiz-next]');
  const progress=root.querySelector('progress'),progressText=root.querySelector('[data-quiz-progress]');
  const result=root.querySelector('[data-quiz-result]'),review=root.querySelector('[data-quiz-review]');
  let state=engine.create(questions.length),current=0;
  function drawProgress(){
    progress.value=state.answers.length;
    progressText.textContent=tr(`Question ${current+1} of ${questions.length}`,`السؤال ${current+1} من ${questions.length}`);
  }
  function start(focus=false){
    state=engine.create(questions.length);current=0;group.hidden=false;result.hidden=true;review.replaceChildren();
    controls.forEach(node=>node.hidden=false);
    root.querySelectorAll('[data-quiz-nojs]').forEach(node=>node.hidden=true);
    questions.forEach((q,i)=>{
      q.hidden=i!==0;q.classList.remove('is-correct','is-incorrect');
      q.querySelector('[data-quiz-feedback]').hidden=true;
      q.querySelectorAll('input').forEach(input=>{input.checked=false;input.disabled=false;});
    });
    check.hidden=false;check.disabled=true;next.hidden=true;drawProgress();
    if(focus){questions[0].querySelector('legend').tabIndex=-1;questions[0].querySelector('legend').focus();}
  }
  root.addEventListener('change',event=>{
    if(event.target.matches('input[type=radio]')&&event.target.closest('[data-quiz-question]')===questions[current])check.disabled=false;
  });
  check.addEventListener('click',()=>{
    const q=questions[current],chosen=q.querySelector('input:checked');
    if(!chosen||state.answers.length!==current)return;
    state=engine.record(state,current,chosen.value==='true',q.dataset.answer==='true');
    const correct=state.answers[current];q.classList.add(correct?'is-correct':'is-incorrect');
    q.querySelectorAll('input').forEach(input=>input.disabled=true);
    q.querySelector('[data-quiz-answer-status]').textContent=correct?tr('Correct. Follow the evidence below.','إجابة صحيحة. اقرأ الدليل والتفسير.'):tr('Take another look at the evidence.','لنراجع ما تثبته الأدلة.');
    q.querySelector('[data-quiz-feedback]').hidden=false;
    check.hidden=true;next.hidden=false;next.textContent=engine.complete(state)?tr('See your result','اعرض النتيجة'):tr('Next question','السؤال التالي');
    progress.value=state.answers.length;
  });
  function showResult(){
    if(!engine.complete(state))return;
    group.hidden=true;controls.forEach(node=>node.hidden=true);result.hidden=false;
    const score=engine.score(state);
    root.querySelector('[data-quiz-score]').textContent=`${score} / ${questions.length}`;
    root.querySelector('[data-quiz-result-text]').textContent=score===questions.length?tr('You kept publication records and story framing apart. Keep that habit on your next mystery.','ميّزت بين سجل النشر وإطار القصة. جرّب المنهج نفسه مع الفيديو الغامض التالي.'):tr('The useful part is the explanation. Revisit the records below, especially where a caption seemed stronger than its evidence.','القيمة الأهم في تفسير الإجابات. راجع السجل أدناه، خصوصًا حين بدا التعليق أقوى من دليله.');
    review.replaceChildren(...questions.map((q,i)=>{
      const item=document.createElement('li'),title=document.createElement('h3'),label=document.createElement('p'),paragraph=document.createElement('p');
      title.textContent=q.querySelector('legend').lastChild.textContent;
      label.className='label';label.textContent=state.answers[i]?tr('Correct','إجابة صحيحة'):tr('Worth another look','تستحق مراجعة');
      paragraph.textContent=q.querySelector('[data-quiz-explanation]').textContent;
      const source=q.querySelector('[data-quiz-source]').cloneNode(true);source.removeAttribute('data-quiz-source');
      item.append(label,title,paragraph,source);return item;
    }));
    root.querySelector('#quiz-result-title').focus();
    window.darkEchoTrack?.('quiz_complete',{quiz_language:ar?'ar':'en'});
  }
  next.addEventListener('click',()=>{
    if(state.answers.length!==current+1)return;
    if(engine.complete(state)){showResult();return;}
    questions[current].hidden=true;current++;questions[current].hidden=false;check.hidden=false;check.disabled=true;next.hidden=true;drawProgress();
    const legend=questions[current].querySelector('legend');legend.tabIndex=-1;legend.focus();
  });
  root.querySelector('[data-quiz-restart]').addEventListener('click',()=>{
    root.querySelector('[data-quiz-share-fallback]').hidden=true;shareStatus.textContent='';start(true);
  });
  const shareStatus=document.createElement('p');shareStatus.setAttribute('role','status');shareStatus.setAttribute('aria-live','polite');shareStatus.className='fine-print';result.append(shareStatus);
  root.querySelector('[data-quiz-share]').addEventListener('click',async()=>{
    if(!engine.complete(state))return;
    const title=tr('Fact or Fiction? | Dark Echo','حقيقة أم تمثيل؟ | دارك إيكو');
    const url=document.querySelector('link[rel=canonical]').href;
    const text=tr(`I scored ${engine.score(state)}/${state.total} on Dark Echo’s evidence quiz. Can you follow the sources?`,`نتيجتي ${engine.score(state)}/${state.total} في اختبار أدلة دارك إيكو. هل تميّز ما تثبته المصادر؟`);
    try{
      if(typeof navigator.share==='function'){await navigator.share({title,text,url});return;}
      if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(text+'\n'+url);shareStatus.textContent=tr('Your result and link were copied.','نُسخت النتيجة ورابط الاختبار.');
    }catch(error){
      if(error.name==='AbortError')return;
      const fallback=root.querySelector('[data-quiz-share-fallback]'),field=root.querySelector('[data-quiz-share-text]');
      fallback.hidden=false;field.value=text+'\n'+url;field.focus();field.select();
      shareStatus.textContent=tr('Select and copy the result below.','حدّد نص النتيجة أدناه وانسخه.');
    }
  });
  start();
})();
