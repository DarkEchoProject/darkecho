/* Shared progressive enhancements. All watch links work without JavaScript. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const menuButton=document.querySelector('.menu-toggle'),menu=document.getElementById('site-nav'),more=document.querySelector('.nav-more');
  function closeMenu(restore=false){if(!menuButton||!menu)return;menu.classList.remove('is-open');menuButton.setAttribute('aria-expanded','false');if(more)more.open=false;if(restore)menuButton.focus();}
  menuButton?.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));menu?.classList.toggle('is-open',open);});
  menu?.addEventListener('click',event=>{if(event.target.closest('a'))closeMenu();});
  document.addEventListener('click',event=>{if(!event.target.closest('.header-inner'))closeMenu();});
  document.addEventListener('keydown',event=>{if(event.key!=='Escape')return;if(menuButton?.getAttribute('aria-expanded')==='true')closeMenu(true);else if(more?.open){more.open=false;more.querySelector('summary').focus();}});
  const dialog=document.getElementById('video-player'),frameContainer=dialog?.querySelector('.dialog-frame');
  let videoTrigger=null;
  function closeVideo(){if(!dialog)return;frameContainer?.replaceChildren();if(dialog.open)dialog.close();document.body.classList.remove('modal-open');const trigger=videoTrigger;videoTrigger=null;if(trigger?.isConnected)trigger.focus({preventScroll:true});}
  dialog?.querySelector('.dialog-close')?.addEventListener('click',closeVideo);
  dialog?.addEventListener('cancel',event=>{event.preventDefault();closeVideo();});
  dialog?.addEventListener('close',()=>{frameContainer?.replaceChildren();document.body.classList.remove('modal-open');});
  dialog?.addEventListener('click',event=>{if(event.target!==dialog)return;const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)closeVideo();});
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
    dialog.showModal();document.body.classList.add('modal-open');dialog.querySelector('.dialog-close').focus();
    window.darkEchoTrack?.('video_open',{video_id:id,video_title:title,interaction:'quick_play'});
  });
  document.addEventListener('click',event=>{const link=event.target.closest?.('a[data-track]');if(link)window.darkEchoTrack?.(link.dataset.track,{link_url:link.href});});
  for(const library of document.querySelectorAll('[data-library]')){
    const grid=library.querySelector('.video-grid'),cards=[...grid.querySelectorAll('[data-video-card]')];
    library.querySelector('.filters').addEventListener('submit',event=>event.preventDefault());
    const search=library.querySelector('[name=q]'),channel=library.querySelector('[name=channel]'),format=library.querySelector('[name=format]'),topic=library.querySelector('[name=topic]'),sort=library.querySelector('[name=sort]');
    const count=library.querySelector('[data-result-count]'),empty=library.querySelector('[data-empty]'),moreButton=library.querySelector('[data-load-more]');
    const controls={q:search,channel,format,topic,sort},defaults={q:'',channel:'all',format:'all',topic:'all',sort:'latest'};let limit=18;
    function readLocation(){const params=new URLSearchParams(location.search);for(const[name,input]of Object.entries(controls)){if(!input)continue;const value=params.get(name)||defaults[name];input.value=input instanceof HTMLSelectElement&&![...input.options].some(o=>o.value===value)?defaults[name]:value;}}
    function render(updateLocation=true){
      const needle=search.value.trim().toLocaleLowerCase();
      const matched=cards.filter(card=>(!needle||card.dataset.search.includes(needle))&&(!channel||channel.value==='all'||card.dataset.channel===channel.value)&&(format.value==='all'||card.dataset.format===format.value)&&(topic.value==='all'||card.dataset.topic===topic.value));
      matched.sort((a,b)=>sort.value==='popular'?Number(b.dataset.views)-Number(a.dataset.views)||b.dataset.date.localeCompare(a.dataset.date):sort.value==='title'?a.dataset.title.localeCompare(b.dataset.title):b.dataset.date.localeCompare(a.dataset.date)||a.dataset.title.localeCompare(b.dataset.title));
      cards.forEach(card=>{card.hidden=true;});matched.forEach((card,i)=>{grid.appendChild(card);card.hidden=i>=limit;});
      const shown=Math.min(limit,matched.length);count.textContent=matched.length?`${matched.length} ${matched.length===1?'video':'videos'} · showing ${shown}`:'No matching videos';empty.hidden=matched.length!==0;moreButton.hidden=shown>=matched.length;moreButton.textContent=`Show ${Math.min(18,matched.length-shown)} more videos`;
      if(updateLocation){const url=new URL(location.href);for(const[name,input]of Object.entries(controls)){if(!input)continue;const value=name==='q'?input.value.trim():input.value;if(value&&value!==defaults[name])url.searchParams.set(name,value);else url.searchParams.delete(name);}history.replaceState(null,'',url);}
    }
    for(const input of Object.values(controls).filter(Boolean))input.addEventListener(input===search?'input':'change',()=>{limit=18;render();});
    for(const reset of library.querySelectorAll('[data-reset-filters]'))reset.addEventListener('click',()=>{for(const[name,input]of Object.entries(controls))if(input)input.value=defaults[name];limit=18;render();search.focus();});
    moreButton.addEventListener('click',()=>{const before=[...grid.querySelectorAll('[data-video-card]')].filter(card=>!card.hidden).length;limit+=18;render();[...grid.querySelectorAll('[data-video-card]')].filter(card=>!card.hidden)[before]?.querySelector('h3 a')?.focus({preventScroll:true});});
    window.addEventListener('popstate',()=>{readLocation();limit=18;render(false);});
    readLocation();render(false);library.querySelector('.filters').hidden=false;library.querySelector('[data-reset-filters]').hidden=false;
  }
})();
