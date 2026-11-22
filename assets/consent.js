/* Basic opt-in mode: no Analytics script or custom events before permission. */
(() => {
  'use strict';
  const key='darkecho-analytics-choice-v1',measurement='G-QSKD08ZSXE',base=document.querySelector('meta[name=site-base]')?.content||'/darkecho/';
  let decision=null,loaded=false,previousFocus=null;
  try{const value=localStorage.getItem(key);if(value==='yes'||value==='no')decision=value;}catch(_){}
  function start(){
    if(loaded||decision!=='yes')return;loaded=true;window['ga-disable-'+measurement]=false;window.dataLayer=window.dataLayer||[];
    window.gtag=function(){window.dataLayer.push(arguments);};
    window.gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
    window.gtag('consent','update',{analytics_storage:'granted'});window.gtag('js',new Date());
    window.gtag('config',measurement,{allow_google_signals:false,allow_ad_personalization_signals:false,cookie_path:base,cookie_flags:'SameSite=Lax;Secure'});
    const tag=document.createElement('script');tag.async=true;tag.src='https://www.googletagmanager.com/gtag/js?id='+measurement;document.head.appendChild(tag);
  }
  window.darkEchoTrack=(name,properties={})=>{if(decision==='yes'&&loaded&&typeof window.gtag==='function')window.gtag('event',name,properties);};
  const panel=document.createElement('section');panel.id='de-consent-panel';panel.className='de-consent-panel';panel.setAttribute('aria-label','Analytics privacy choices');panel.hidden=decision!==null;
  const paragraph=document.createElement('p');paragraph.append('May we use optional Google Analytics to understand visits? You can reject analytics and browse normally. ');
  const privacy=document.createElement('a');privacy.href=base+'privacy.html';privacy.textContent='Privacy policy';paragraph.append(privacy);
  const actions=document.createElement('div');actions.className='de-consent-actions';
  for(const[value,label]of[['no','Reject analytics'],['yes','Allow analytics']]){const button=document.createElement('button');button.type='button';button.dataset.choice=value;button.textContent=label;actions.append(button);}
  panel.append(paragraph,actions);document.body.appendChild(panel);
  function clearCookies(){for(const name of['_ga','_ga_QSKD08ZSXE'])for(const path of['/',base])for(const domain of['',`;domain=${location.hostname}`,`;domain=.${location.hostname}`])document.cookie=`${name}=;Max-Age=0;path=${path}${domain};SameSite=Lax`;}
  panel.addEventListener('click',event=>{const button=event.target.closest('button[data-choice]');if(!button)return;const wasAllowed=decision==='yes';decision=button.dataset.choice;try{localStorage.setItem(key,decision);}catch(_){}panel.hidden=true;if(decision==='yes')start();else if(wasAllowed&&loaded){window['ga-disable-'+measurement]=true;clearCookies();location.reload();return;}if(previousFocus?.isConnected)previousFocus.focus();});
  document.addEventListener('click',event=>{const button=event.target.closest?.('[data-consent-manage],#de-privacy-manage');if(!button)return;previousFocus=button;panel.hidden=false;panel.querySelector('button').focus();});
  document.querySelectorAll('[data-consent-manage],#de-privacy-manage').forEach(button=>{button.setAttribute('aria-controls',panel.id);button.hidden=false;});
  if(decision==='yes')start();
})();
