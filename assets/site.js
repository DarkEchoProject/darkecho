/* Progressive enhancements. Ordinary watch and chapter links always remain usable. */
(() => {
  'use strict';
  const catalog=window.DarkEchoCatalog;
  document.documentElement.classList.add('js');
  const menuButton=document.querySelector('.menu-toggle'),menu=document.getElementById('site-nav'),more=document.querySelector('.nav-more');
  if(menuButton)menuButton.hidden=false;
  function closeMenu(restore=false){
    if(!menuButton||!menu)return;
    menu.classList.remove('is-open');menuButton.setAttribute('aria-expanded','false');
    if(more)more.open=false;if(restore)menuButton.focus();
  }
  menuButton?.addEventListener('click',()=>{
    const open=menuButton.getAttribute('aria-expanded')!=='true';
    menuButton.setAttribute('aria-expanded',String(open));menu?.classList.toggle('is-open',open);
  });
  menu?.addEventListener('click',event=>{if(event.target.closest('a'))closeMenu();});
  document.addEventListener('click',event=>{if(!event.target.closest('.header-inner'))closeMenu();});
  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape')return;
    if(menuButton?.getAttribute('aria-expanded')==='true')closeMenu(true);
    else if(more?.open){more.open=false;more.querySelector('summary').focus();}
  });

  const status=document.createElement('p');status.className='site-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');status.hidden=true;document.body.append(status);
  let statusTimer;
  function announce(message){
    clearTimeout(statusTimer);status.textContent=message;status.hidden=false;
    statusTimer=setTimeout(()=>{status.hidden=true;},6500);
  }
  const savedKey='darkecho-watch-later-v1',savedLibrary=document.querySelector('[data-saved-library]');
  const savedGrid=savedLibrary?.querySelector('[data-saved-grid]');
  const templates=new Map([...document.querySelectorAll('template[data-saved-template]')].map(t=>[t.dataset.savedTemplate,t]));
  let saved=[];
  try{saved=catalog.parseSaved(localStorage.getItem(savedKey));}catch(_){}
  function storeSaved(ids){
    saved=catalog.cleanSaved(ids);
    try{localStorage.setItem(savedKey,JSON.stringify(saved));return true;}catch(_){return false;}
  }
  function renderSavedList(){
    if(!savedLibrary)return;
    const focused=savedGrid.contains(document.activeElement),previous=[...savedGrid.children].findIndex(card=>card.contains(document.activeElement));
    const available=saved.filter(id=>templates.has(id));
    savedGrid.replaceChildren(...available.map(id=>templates.get(id).content.cloneNode(true)));
    savedLibrary.hidden=false;
    savedLibrary.querySelector('[data-saved-empty]').hidden=available.length!==0;
    savedLibrary.querySelector('[data-clear-saved]').hidden=saved.length===0;
    savedLibrary.querySelector('[data-saved-summary]').textContent=`${available.length} saved ${available.length===1?'video':'videos'}${saved.length>available.length?' · some saved videos are no longer in this collection':''}`;
    if(focused){
      const target=savedGrid.children[Math.min(Math.max(0,previous),available.length-1)]?.querySelector('h3 a')||savedLibrary.querySelector('[data-saved-empty] h2');
      target?.focus({preventScroll:true});
    }
  }
  function syncSaved(){
    renderSavedList();
    for(const button of document.querySelectorAll('[data-save-video]')){
      const selected=saved.includes(button.dataset.saveVideo),compact=button.classList.contains('save-compact');
      button.hidden=false;button.setAttribute('aria-pressed',String(selected));
      button.setAttribute('aria-label',`${selected?'Remove from watch later':'Save for later'}: ${button.dataset.saveTitle}`);
      button.querySelector('span').textContent=selected?'Saved':compact?'Save':'Save for later';
    }
    for(const count of document.querySelectorAll('[data-saved-count]')){count.textContent=String(saved.length);count.hidden=saved.length===0;}
  }
  document.addEventListener('click',event=>{
    const button=event.target.closest?.('[data-save-video]');if(!button)return;
    const id=button.dataset.saveVideo;if(!/^[A-Za-z0-9_-]{11}$/.test(id||''))return;
    const selected=saved.includes(id),persisted=storeSaved(selected?saved.filter(x=>x!==id):[id,...saved]);
    syncSaved();
    announce(`${selected?'Removed from watch later':'Saved for later'}: ${button.dataset.saveTitle}.${persisted?'':' Browser storage is unavailable; changes last only on this page.'}`);
  });
  savedLibrary?.querySelector('[data-clear-saved]').addEventListener('click',()=>{
    const persisted=storeSaved([]);syncSaved();savedLibrary.querySelector('[data-saved-empty] h2').focus();
    announce('Saved list cleared.'+(persisted?'':' Browser storage is unavailable; this change is temporary.'));
  });
  window.addEventListener('storage',event=>{
    if(event.key!==savedKey&&event.key!==null)return;
    try{saved=catalog.parseSaved(localStorage.getItem(savedKey));}catch(_){return;}
    syncSaved();
  });
  syncSaved();

  for(const button of document.querySelectorAll('[data-copy-link]')){
    button.hidden=false;
    button.addEventListener('click',async()=>{
      try{
        if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(button.dataset.copyLink);announce('Page link copied.');
      }catch(_){
        const fallback=button.closest('[data-share]').querySelector('.copy-fallback');fallback.hidden=false;
        const input=fallback.querySelector('input');input.focus();input.select();announce('Select and copy the page link shown below.');
      }
    });
  }

  const dialog=document.getElementById('video-player'),frameContainer=dialog?.querySelector('.dialog-frame');
  let videoTrigger=null;
  function closeVideo(){
    if(!dialog)return;frameContainer?.replaceChildren();if(dialog.open)dialog.close();document.body.classList.remove('modal-open');
    const trigger=videoTrigger;videoTrigger=null;
    if(trigger?.isConnected&&trigger.getClientRects().length)trigger.focus({preventScroll:true});
  }
  dialog?.querySelector('.dialog-close')?.addEventListener('click',closeVideo);
  dialog?.addEventListener('cancel',event=>{event.preventDefault();closeVideo();});
  dialog?.addEventListener('close',()=>{if(dialog.open)return;frameContainer?.replaceChildren();document.body.classList.remove('modal-open');});
  dialog?.addEventListener('click',event=>{
    if(event.target!==dialog)return;const r=dialog.getBoundingClientRect();
    if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)closeVideo();
  });
  document.addEventListener('click',event=>{
    if(!(event.target instanceof Element))return;
    const link=event.target.closest('a[data-video-id]');
    if(!link||!dialog||typeof dialog.showModal!=='function'||event.button!==0||event.ctrlKey||event.metaKey||event.altKey||event.shiftKey)return;
    const id=link.dataset.videoId;if(!/^[A-Za-z0-9_-]{11}$/.test(id||''))return;
    event.preventDefault();closeMenu();videoTrigger=link;
    const title=link.dataset.videoTitle||'Video';
    dialog.querySelector('#player-title').textContent=title;
    dialog.querySelector('[data-player-details]').href=link.href;
    dialog.querySelector('[data-player-youtube]').href='https://www.youtube.com/watch?v='+id;
    const iframe=document.createElement('iframe');iframe.title=title;iframe.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';iframe.allowFullscreen=true;iframe.referrerPolicy='strict-origin-when-cross-origin';iframe.src='https://www.youtube-nocookie.com/embed/'+id+'?autoplay=1&rel=0';
    frameContainer.replaceChildren(iframe);
    document.querySelectorAll('.watch-video iframe').forEach(frame=>{const url=frame.src;frame.src=url;});
    if(!dialog.open)dialog.showModal();document.body.classList.add('modal-open');dialog.querySelector('.dialog-close').focus();
    window.darkEchoTrack?.('video_open',{video_id:id,video_title:title,interaction:'quick_play'});
  });
  document.addEventListener('click',event=>{const link=event.target.closest?.('a[data-track]');if(link)window.darkEchoTrack?.(link.dataset.track,{link_url:link.href});});

  for(const library of document.querySelectorAll('[data-library]')){
    const grid=library.querySelector('.video-grid'),cards=[...grid.querySelectorAll('[data-video-card]')];
    library.querySelector('.filters').addEventListener('submit',event=>event.preventDefault());
    const search=library.querySelector('[name=q]'),channel=library.querySelector('[name=channel]'),format=library.querySelector('[name=format]'),topic=library.querySelector('[name=topic]'),sort=library.querySelector('[name=sort]');
    const count=library.querySelector('[data-result-count]'),empty=library.querySelector('[data-empty]'),moreButton=library.querySelector('[data-load-more]');
    const controls={q:search,channel,format,topic,sort},defaults={q:'',channel:'all',format:'all',topic:'all',sort:'latest'};let limit=18;
    function readLocation(){
      const params=new URLSearchParams(location.search);
      for(const[name,input]of Object.entries(controls)){
        if(!input)continue;const value=(params.get(name)||defaults[name]).slice(0,name==='q'?200:100);
        input.value=input instanceof HTMLSelectElement&&![...input.options].some(o=>o.value===value)?defaults[name]:value;
      }
      const stored=history.state?.darkechoLimit;limit=Number.isInteger(stored)&&stored>=18&&stored<=cards.length+18?stored:18;
    }
    function render(updateLocation=true){
      const matched=cards.filter(card=>catalog.matches(card.dataset.search,search.value)&&(!channel||channel.value==='all'||card.dataset.channel===channel.value)&&(format.value==='all'||card.dataset.format===format.value)&&(topic.value==='all'||card.dataset.topic===topic.value));
      matched.sort((a,b)=>sort.value==='popular'?Number(b.dataset.views)-Number(a.dataset.views)||b.dataset.date.localeCompare(a.dataset.date):sort.value==='title'?a.dataset.title.localeCompare(b.dataset.title):b.dataset.date.localeCompare(a.dataset.date)||a.dataset.title.localeCompare(b.dataset.title));
      cards.forEach(card=>{card.hidden=true;});matched.forEach((card,i)=>{grid.appendChild(card);card.hidden=i>=limit;});
      const shown=Math.min(limit,matched.length);count.textContent=matched.length?`${matched.length} ${matched.length===1?'video':'videos'} · showing ${shown}`:'No matching videos';
      empty.hidden=matched.length!==0;moreButton.hidden=shown>=matched.length;moreButton.textContent=`Show ${Math.min(18,matched.length-shown)} more videos`;
      if(updateLocation){
        const url=new URL(location.href);
        for(const[name,input]of Object.entries(controls)){
          if(!input)continue;const value=name==='q'?input.value.trim():input.value;
          if(value&&value!==defaults[name])url.searchParams.set(name,value);else url.searchParams.delete(name);
        }
        history.replaceState({...history.state,darkechoLimit:limit},'',url);
      }
    }
    for(const input of Object.values(controls).filter(Boolean))input.addEventListener(input===search?'input':'change',()=>{limit=18;render();});
    for(const reset of library.querySelectorAll('[data-reset-filters]'))reset.addEventListener('click',()=>{for(const[name,input]of Object.entries(controls))if(input)input.value=defaults[name];limit=18;render();search.focus();});
    moreButton.addEventListener('click',()=>{
      const before=[...grid.querySelectorAll('[data-video-card]')].filter(card=>!card.hidden).length;limit+=18;render();
      [...grid.querySelectorAll('[data-video-card]')].filter(card=>!card.hidden)[before]?.querySelector('h2 a')?.focus({preventScroll:true});
    });
    window.addEventListener('popstate',()=>{readLocation();render(false);});
    readLocation();render(false);library.querySelector('.filters').hidden=false;library.querySelector('[data-reset-filters]').hidden=false;
  }
})();
