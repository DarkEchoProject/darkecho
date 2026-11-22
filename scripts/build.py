#!/usr/bin/env python3
"""Build the GitHub Pages site using a single verified video catalog. Python stdlib only."""
from pathlib import Path
from datetime import datetime
from math import ceil
from urllib.parse import urlsplit
import base64,hashlib,html,json,re
from catalog import validate_catalog

ROOT=Path(__file__).resolve().parents[1]
SITE=json.loads((ROOT/'data/site.json').read_text(encoding='utf-8'))
BASE=SITE['baseUrl']
PREFIX=urlsplit(BASE).path
CATALOG=json.loads((ROOT/'data/videos.json').read_text(encoding='utf-8'))
VIDEOS=CATALOG['videos']; BY_ID={v['id']:v for v in VIDEOS}
ARTICLES=json.loads((ROOT/'data/articles.json').read_text(encoding='utf-8'))
SERIES=json.loads((ROOT/'data/series.json').read_text(encoding='utf-8'))
UPDATED=CATALOG['updatedAt']; TODAY=SITE['contentUpdatedAt']
CHANNEL='https://www.youtube.com/@DarkEchoProject'
ISSUES='https://github.com/DarkEchoProject/darkecho/issues/new?template=website-feedback.yml'
GENERATED=[]

def e(value):return html.escape(str(value),quote=True)
def link(path=''):return PREFIX+path
def canonical(path=''):return BASE+('' if path=='index.html' else path)
def date(value):return datetime.fromisoformat(value.replace('Z','+00:00')).strftime('%b %d, %Y').replace(' 0',' ')
def duration(seconds):
 h,rem=divmod(seconds,3600);m,s=divmod(rem,60)
 return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'
def views(n):return f'{n:,}'
def version(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12]
def asset(path):return link(path)+'?v='+version(path)
PLAY='<svg width="18" height="20" viewBox="0 0 18 20" aria-hidden="true"><path d="M3 2v16l13-8Z" fill="currentColor"/></svg>'
MENU='<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M2 4h14M2 9h14M2 14h14" stroke="currentColor" stroke-width="1.5"/></svg>'
CLOSE='<svg width="15" height="15" viewBox="0 0 15 15" aria-hidden="true"><path d="m3 3 9 9M12 3l-9 9" stroke="currentColor" stroke-width="1.6"/></svg>'
BOOKMARK='<svg width="18" height="20" viewBox="0 0 18 20" aria-hidden="true"><path d="M4 2h10v16l-5-3-5 3Z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'

def save_button(v,compact=False):
 return f'<button class="save-video {"save-compact" if compact else "button"}" type="button" data-save-video="{e(v["id"])}" data-save-title="{e(v["title"])}" aria-pressed="false" aria-label="Save for later: {e(v["title"])}" hidden>{BOOKMARK}<span>{"Save" if compact else "Save for later"}</span></button>'

def share_tools(path):
 return f'<div class="share-tools" data-share><button class="button button-small" type="button" data-copy-link="{canonical(path)}" hidden>Copy page link</button><div class="copy-fallback" hidden><label>Page link<input type="text" readonly value="{canonical(path)}"></label><p class="fine-print">Select and copy this link using your browser.</p></div></div>'

def image(video,*,eager=False,css='',alt=None):
 id=video['id'];small=link(f'assets/thumbs/{id}-320.webp');large=link(video['thumbnail'])
 return f'<img class="{e(css)}" src="{large}" srcset="{small} 320w, {large} 640w" sizes="(max-width:480px) calc(100vw - 36px), (max-width:760px) calc((100vw - 52px)/2), 400px" width="640" height="360" alt="{e(alt if alt is not None else video["title"])}" loading="{"eager" if eager else "lazy"}" decoding="async"{(" fetchpriority=\"high\"" if eager else "")}>'

def quick_link(video,*,eager=False):
 return f'<div class="thumbnail-wrap"><a class="video-thumb" href="{link("watch/"+video["id"]+".html")}" data-video-id="{e(video["id"])}" data-video-title="{e(video["title"])}" aria-label="Quick play: {e(video["title"])}">{image(video,eager=eager,alt="")}<span class="play-icon">{PLAY}</span><span class="duration">{duration(video["seconds"])}</span></a>{save_button(video,compact=True)}</div>'

def card(v,heading='h3'):
 text=' '.join([v['title'],v['sourceTitle'],v['summary'],v['topic'],v['channelName']]).lower()
 attrs=f'data-video-card data-channel="{e(v["channel"])}" data-topic="{e(v["topic"])}" data-format="{v["format"]}" data-views="{v["views"]}" data-date="{v["uploadDate"]}" data-title="{e(v["title"])}" data-search="{e(text)}"'
 return f'''<article class="video-card" {attrs}>
{quick_link(v)}<div class="card-body"><p class="card-kicker"><span>{e(v['topic'])}</span><span>{e(v['channelName'])}</span></p>
<{heading}><a href="{link('watch/'+v['id']+'.html')}">{e(v['title'])}</a></{heading}><p class="card-summary">{e(v['summary'])}</p>
<div class="card-bottom"><span>{views(v['views'])} views</span><a href="{link('watch/'+v['id']+'.html')}">Watch video<span class="sr-only">: {e(v['title'])}</span></a></div></div></article>'''

def header(active):
 def nav(path,label,key):return f'<a href="{link(path)}"'+(' aria-current="page"' if active==key else '')+f'>{label}</a>'
 return f'''<a class="skip-link" href="#main-content">Skip to content</a>
<header class="site-header"><div class="container header-inner">
<a class="wordmark" href="{link()}" aria-label="Dark Echo home"><span class="brand-mark" aria-hidden="true"></span>DARK ECHO</a>
<button class="menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false" hidden>{MENU}<span>Menu</span></button>
<nav class="site-nav" id="site-nav" aria-label="Main navigation">{nav('','Home','home')}{nav('more-videos.html','Videos','videos')}{nav('series.html','Series','series')}{nav('blog.html','Stories','stories')}
<details class="nav-more"><summary>More</summary><div class="nav-dropdown">{nav('watch-later.html','Watch later <span data-saved-count hidden>0</span>','saved')}{nav('about.html','About Dark Echo','about')}{nav('contact.html','Contact & feedback','contact')}{nav('earn-with-nasser.html','Earn With Nasser archive','nasser')}{nav('privacy.html','Privacy','privacy')}</div></details>
<a class="nav-subscribe" href="{CHANNEL}?sub_confirmation=1" target="_blank" rel="noopener noreferrer" data-track="subscribe_click">YouTube channel</a></nav></div></header>'''

def footer():
 return f'''<footer class="site-footer"><div class="container"><div class="footer-top"><div><a class="wordmark" href="{link()}"><span class="brand-mark" aria-hidden="true"></span>DARK ECHO</a><p>Short horror stories, unsettling reflections, and one more reason to leave the light on.</p></div><nav class="footer-links" aria-label="Footer navigation"><a href="{link('more-videos.html')}">Video archive</a><a href="{link('series.html')}">Video series</a><a href="{link('watch-later.html')}">Watch later <span data-saved-count hidden>0</span></a><a href="{link('blog.html')}">Horror fiction</a><a href="{link('about.html')}">About</a><a href="{link('contact.html')}">Contact & feedback</a><a href="{link('earn-with-nasser.html')}">Nasser archive</a><a href="{link('privacy.html')}">Privacy</a><button type="button" data-consent-manage hidden>Analytics choices</button><a href="{link('sitemap.xml')}">Sitemap</a></nav></div><div class="footer-bottom"><p>© 2026 Dark Echo. Horror stories are fictional entertainment.</p><p>Video data checked {date(UPDATED)}.</p></div></div></footer>'''

def player():
 return f'''<dialog class="video-dialog" id="video-player" aria-labelledby="player-title"><div class="dialog-bar"><h2 id="player-title">Video player</h2><button class="dialog-close" type="button" aria-label="Close video player" autofocus>{CLOSE}<span>Close</span></button></div><div class="dialog-frame"></div><div class="dialog-footer"><a data-player-details href="{link('more-videos.html')}">Open watch page</a><a data-player-youtube href="{CHANNEL}" target="_blank" rel="noopener noreferrer">Watch on YouTube</a></div></dialog>'''

def write_page(path,title,description,body,*,active='',schema=None,social=None,index=True,article=False,legacy=False,modified=None):
 schema=schema or {'@context':'https://schema.org','@type':'WebPage','name':title,'url':canonical(path),'inLanguage':'en'}
 raw=json.dumps(schema,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
 json_hash=base64.b64encode(hashlib.sha256(raw.encode()).digest()).decode()
 policy=("default-src 'self'; script-src 'self' https://www.googletagmanager.com 'sha256-"+json_hash+"'; style-src 'self'; img-src 'self' data: https://www.google-analytics.com https://*.google-analytics.com; frame-src https://www.youtube-nocookie.com; connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'")
 social=social or 'assets/brand/atmosphere.webp'
 text=f'''<!DOCTYPE html>
<html lang="en" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="{e(policy)}"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="site-base" content="{PREFIX}"><meta name="theme-color" content="#09090c"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="{'index, follow, max-image-preview:large, max-video-preview:-1' if index else 'noindex, follow'}"><link rel="canonical" href="{canonical(path)}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:site_name" content="Dark Echo"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{canonical(path)}"><meta property="og:image" content="{BASE+social}"><meta property="og:image:alt" content="{e(title)}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{BASE+social}"><link rel="icon" type="image/png" sizes="48x48" href="{link('assets/brand/icon-48.png')}"><link rel="apple-touch-icon" sizes="180x180" href="{link('assets/brand/icon-180.png')}"><link rel="stylesheet" href="{asset('assets/site.css')}"><script defer src="{asset('assets/consent.js')}"></script><script defer src="{asset('assets/catalog-tools.js')}"></script><script defer src="{asset('assets/site.js')}"></script><script type="application/ld+json">{raw}</script></head>
<body{' class="legacy"' if legacy else ''}>{header(active)}<main id="main-content" tabindex="-1">{body}</main>{footer()}{player()}</body></html>
'''
 dest=ROOT/path;dest.parent.mkdir(exist_ok=True,parents=True);dest.write_text(text,encoding='utf-8')
 GENERATED.append({'path':path,'index':index,'modified':modified or TODAY})

def section(id,title,subtitle,items,more_url=None):
 more=f'<a href="{e(more_url)}">Browse all videos</a>' if more_url else ''
 return f'<section class="section" id="{id}"><div class="container"><div class="section-heading"><div><h2>{e(title)}</h2><p>{e(subtitle)}</p></div>{more}</div><div class="video-grid">'+''.join(card(v) for v in items)+'</div></div></section>'

def subscribe():
 return f'<section class="section" id="join"><div class="container"><div class="subscribe-panel"><div><h2>The story is not over.</h2><p>Find more Dark Echo stories on YouTube. Headphones on, lights optional.</p></div><a class="button button-primary" href="{CHANNEL}?sub_confirmation=1" target="_blank" rel="noopener noreferrer" data-track="subscribe_click">Explore the channel</a></div></div></section>'

def story_cards(heading='h2'):
 result=[]
 for a in ARTICLES:
  v=BY_ID[a['image']]
  result.append(f'<article class="story-card"><a href="{link(a["file"])}" aria-label="Read {e(a["title"])}">{image(v,alt="")}</a><div class="card-body"><span class="label">Original horror fiction</span><{heading}><a href="{link(a["file"])}">{e(a["title"])}</a></{heading}><p>{e(a["deck"])}</p><a class="story-link" href="{link(a["file"])}" data-track="article_open">Read the story<span class="sr-only">: {e(a["title"])}</span></a></div></article>')
 return '<div class="story-grid">'+''.join(result)+'</div>'

def home():
 horror=[v for v in VIDEOS if v['channel']=='darkecho'];latest=sorted(horror,key=lambda v:v['uploadDate'],reverse=True);popular=sorted(horror,key=lambda v:v['views'],reverse=True);featured=latest[0]
 body=f'''<section class="hero" id="featured"><div class="container hero-grid"><div><p class="eyebrow">Dark Echo · Horror stories & films</p><h1>Stay for the <em>last frame.</em></h1><p class="hero-description">A reflection moves. A camera catches the impossible. Explore short horror stories and dark cinema, one unsettling moment at a time.</p><div class="actions"><a class="button button-primary" href="#latest">Find your next watch</a><a class="button" href="{link('blog.html')}">Read the stories</a></div><p class="fine-print">Fictional scares. Real curiosity.</p></div><article class="hero-feature" id="big-feature">{quick_link(featured,eager=True)}<div class="feature-caption"><span class="label">Featured from the collection</span><h2><a href="{link('watch/'+featured['id']+'.html')}">{e(featured['title'])}</a></h2><p class="fine-print">{e(featured['summary'])}</p></div></article></div></section>'''
 body+=section('latest','Latest in the collection','Newest additions by original video publication date. Clips and longer videos are labelled by duration.',latest[:6],link('more-videos.html?channel=darkecho'))
 body+=section('most-watched','Most watched','Dark Echo videos in this collection, ranked by views. Counts checked '+date(UPDATED)+'.',popular[:6],link('more-videos.html?channel=darkecho&sort=popular'))
 clips=sorted([v for v in horror if v['format']=='clip'],key=lambda v:v['uploadDate'],reverse=True)
 body+=section('stories','A few minutes in the dark','Short clips up to three minutes. Every card leads to its own watch page.',clips[:6],link('more-videos.html?channel=darkecho&format=clip'))
 body+=series_teaser()
 body+='<section class="section"><div class="container"><div class="section-heading"><div><h2>Read after dark</h2><p>Original fictional encounters for the moments between videos.</p></div><a href="'+link('blog.html')+'">All stories</a></div>'+story_cards('h3')+'</div></section>'+subscribe()
 schema={'@context':'https://schema.org','@type':'WebSite','name':'Dark Echo','url':BASE,'inLanguage':'en','description':'Horror stories, short clips, and dark cinema from Dark Echo.'}
 write_page('index.html','Dark Echo | Horror Stories, Short Clips & Dark Cinema','Discover Dark Echo horror stories and videos. Watch eerie short clips, explore dark cinema, and read original fictional encounters.',body,active='home',schema=schema)

def options(values,label):return '<option value="all">'+label+'</option>'+''.join(f'<option value="{e(value)}">{e(text)}</option>' for value,text in values)

def library_page(legacy=False):
 items=[v for v in VIDEOS if (v['channel']=='nasser')==legacy];items.sort(key=lambda v:v['uploadDate'],reverse=True)
 topics=sorted(set(v['topic'] for v in items));path='earn-with-nasser.html' if legacy else 'more-videos.html'
 title='Earn With Nasser — The Tutorial Archive' if legacy else 'The Video Archive'
 intro='An independent archive of older tutorials on AI tools, online work, wallets, automation, and gaming.' if legacy else 'Search Dark Echo horror stories and the Extreme Events collection. Choose a channel, a topic, or a little more time in the dark.'
 note='<aside class="notice"><p><strong>Historical tutorial archive.</strong> These videos were published at different times, including older platforms and offers. Availability, prices, software, rewards, and instructions may have changed. The archive does not promise current earnings or active offers.</p><p>The original uploads now appear on the creator’s PC Board Repair channel. This separate collection preserves those earlier tutorials.</p></aside>' if legacy else ''
 channels='' if legacy else '<label>Channel<select name="channel" aria-label="Channel">'+options([('darkecho','Dark Echo'),('extreme','Extreme Events')],'All channels')+'</select></label>'
 filters=f'''<form class="filters" role="search" aria-label="Filter video archive" hidden><label class="filter-search">Search videos<input type="search" name="q" placeholder="Try mirrors, volcanoes, or a video title" autocomplete="off" maxlength="200"></label>{channels}<label>Length<select name="format" aria-label="Length">{options([('clip','Clips · up to 3 minutes'),('video','Longer videos')],'All lengths')}</select></label><label>Topic<select name="topic" aria-label="Topic">{options([(t,t) for t in topics],'All topics')}</select></label><label>Sort by<select name="sort" aria-label="Sort by"><option value="latest">Newest first</option><option value="popular">Most watched</option><option value="title">Title A–Z</option></select></label></form>'''
 # Search is handled locally; prevent native form submission from replacing the filtered state.
 body=f'<div class="container"><header class="page-intro"><p class="eyebrow">'+('A separate collection' if legacy else 'Find your next watch')+f'</p><h1>{e(title)}</h1><p>{e(intro)}</p></header>{note}<section data-library aria-label="Video collection">{filters}<div class="library-toolbar"><p data-result-count role="status" aria-live="polite">{len(items)} videos</p><button type="button" data-reset-filters hidden>Clear filters</button></div><noscript><p>All videos are displayed below. Search and filters are available when JavaScript is enabled.</p></noscript><div class="video-grid">'+''.join(card(v,heading='h2') for v in items)+'</div><div class="empty-state" data-empty hidden><h2>No matching videos</h2><p>Try a different title, channel, or topic.</p><button class="button" type="button" data-reset-filters>Clear all filters</button></div><div class="load-more"><button class="button" type="button" data-load-more hidden>Show more videos</button></div></section><p class="fine-print">View counts checked '+date(UPDATED)+'. “Short clips” describes running time, rather than a claim about YouTube’s platform classification.</p></div><div class="section"></div>'
 write_page(path,title+' | Dark Echo',intro,body,active='nasser' if legacy else 'videos',index=not legacy,legacy=legacy)

def blog():
 body='<div class="container"><header class="page-intro"><p class="eyebrow">The reading room</p><h1>Stories that follow you into the dark.</h1><p>Original horror fiction, camera-inspired encounters, and strange reflections. Every story here is written for entertainment, not presented as a verified paranormal event.</p></header>'+story_cards()+'</div>'+subscribe()
 write_page('blog.html','Dark Echo Stories | Original Horror Fiction','Read original fictional horror stories from Dark Echo: unsettling cameras, unexplained sounds, mirrors, and ordinary places with one impossible detail.',body,active='stories')

def article_pages():
 for a in ARTICLES:
  updated=a.get('updated',TODAY);minutes=max(1,ceil(sum(len(p.split()) for s in a['sections'] for p in s['paragraphs'])/200))
  v=BY_ID[a['image']];body=f'<article class="reading-layout"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{link()}">Home</a><span aria-hidden="true">/</span><a href="{link("blog.html")}">Stories</a></nav><header><p class="eyebrow">Original horror fiction</p><h1 class="article-title">{e(a["title"])}</h1><p class="article-deck">{e(a["deck"])}</p><p class="article-meta"><span>By Dark Echo Editorial</span><span>Published <time datetime="{a["published"]}">{date(a["published"])}</time></span><span>Updated <time datetime="{updated}">{date(updated)}</time></span><span>About {minutes} min read</span></p>{share_tools(a["file"])}</header><aside class="notice"><p>These stories are original fiction and dramatizations for entertainment. They are not authenticated camera footage or reports of verified events.</p></aside>'+image(v,eager=True,css='article-image')
  body+='<nav class="story-contents" aria-label="Story chapters"><h2>In this collection</h2><ol>'+''.join(f'<li><a href="#chapter-{i}">{e(s["title"])}</a></li>' for i,s in enumerate(a['sections'],1))+'</ol></nav><div class="prose">'
  for i,s in enumerate(a['sections'],1):body+=f'<section id="chapter-{i}"><h2>'+e(s['title'])+'</h2>'+''.join('<p>'+e(p)+'</p>' for p in s['paragraphs'])+'</section>'
  body+='</div><section class="related-box"><h2>Continue watching</h2><ul>'+''.join(f'<li><a href="{link("watch/"+id+".html")}" data-track="article_to_video">{e(BY_ID[id]["title"])}</a></li>' for id in a['related'])+'</ul></section><section class="related-box"><h2>More original fiction</h2><ul>'+''.join(f'<li><a href="{link(other["file"])}">{e(other["title"])}</a></li>' for other in ARTICLES if other!=a)+'</ul></section></article>'
  schema={'@context':'https://schema.org','@type':'BlogPosting','headline':a['title'],'description':a['deck'],'url':canonical(a['file']),'mainEntityOfPage':{'@type':'WebPage','@id':canonical(a['file'])},'genre':'Horror fiction','inLanguage':'en','datePublished':a['published'],'dateModified':updated,'image':BASE+v['thumbnail'],'author':{'@type':'Organization','name':'Dark Echo Editorial','url':canonical('about.html')},'publisher':{'@type':'Organization','name':'Dark Echo','url':BASE,'logo':{'@type':'ImageObject','url':BASE+'assets/brand/icon-512.png'}}}
  write_page(a['file'],a['title']+' | Dark Echo',a['deck'],body,active='stories',schema=schema,social=v['thumbnail'],article=True,modified=updated)

def watch_pages():
 for v in VIDEOS:
  legacy=v['channel']=='nasser';path='watch/'+v['id']+'.html';return_path='earn-with-nasser.html' if legacy else 'more-videos.html'
  embed='https://www.youtube-nocookie.com/embed/'+v['id']+'?rel=0'
  body=f'''<article class="container watch-layout"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{link()}">Home</a><span aria-hidden="true">/</span><a href="{link(return_path)}">{'Nasser archive' if legacy else 'Video archive'}</a></nav><div class="watch-heading"><p class="eyebrow">{e(v['channelName'])} · {e(v['topic'])}</p><h1>{e(v['title'])}</h1><p class="article-meta"><span>Published <time datetime="{v['uploadDate']}">{date(v['uploadDate'])}</time></span><span>{duration(v['seconds'])}</span><span>{views(v['views'])} views · checked {date(UPDATED)}</span></p></div><div class="watch-video"><iframe src="{embed}" title="{e(v['title'])}" width="1280" height="720" loading="eager" referrerpolicy="strict-origin-when-cross-origin" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div><div class="watch-info"><div class="watch-description"><p>{e(v['summary'])}</p>'''
  if v['channel']=='darkecho':body+='<p>Dark Echo presents fictional horror and entertainment. Scenes and stories are not offered as verified paranormal evidence.</p>'
  elif legacy:body+='<aside class="notice"><p>This is a historical tutorial. Platforms, software, rewards, and instructions may have changed. It is not a promise of current availability or income.</p></aside>'
  else:body+='<p class="notice">From the Extreme Events archive, originally published '+date(v['uploadDate'])+'. Dates, scenarios, and statements belong to the original video; this archive is not a live disaster alert or a current forecast.</p>'
  body+=f'''<p><a href="{link(return_path)}">Browse the collection</a></p><div class="actions">{save_button(v)}{share_tools(path)}</div>{series_navigation(v['id'])}</div><aside class="watch-facts" aria-label="Video details"><dl><dt>Length</dt><dd>{duration(v['seconds'])}</dd><dt>Format</dt><dd>{'Short clip' if v['format']=='clip' else 'Longer video'}</dd><dt>Topic</dt><dd>{e(v['topic'])}</dd></dl><a class="button" href="https://www.youtube.com/watch?v={v['id']}" target="_blank" rel="noopener noreferrer" data-track="youtube_watch">Watch on YouTube</a><p class="fine-print">Embedded using YouTube’s privacy-enhanced player. YouTube may process playback information independently of optional site analytics.</p></aside></div></article>'''
  related=[other for other in VIDEOS if other['channel']==v['channel'] and other['id']!=v['id']]
  related.sort(key=lambda other:(other['topic']==v['topic'],other['views']),reverse=True)
  body+=section('related-videos','Continue watching','More from this collection.',related[:3])
  schema={'@context':'https://schema.org','@type':'VideoObject','name':v['title'],'description':v['summary'],'thumbnailUrl':[BASE+v['thumbnail']],'uploadDate':v['uploadDate'],'duration':v['duration'],'embedUrl':embed,'url':canonical(path),'mainEntityOfPage':canonical(path),'author':{'@type':'Organization','name':v['channelName'],'url':v['channelUrl']}}
  write_page(path,v['title']+' | Dark Echo',v['summary'],body,active='nasser' if legacy else 'videos',schema=schema,social=v['thumbnail'],index=not legacy,legacy=legacy)

def validate_series():
 slugs=set();members=set()
 for series in SERIES:
  slug=series['slug'];ids=series['parts']+[series['complete']]
  if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug) or slug in slugs:raise ValueError('Invalid or duplicate series slug')
  if len(series['parts'])<2 or len(set(ids))!=len(ids):raise ValueError('A series needs distinct ordered parts and a complete story')
  for id in ids:
   if id not in BY_ID or BY_ID[id]['channel']!='darkecho' or id in members:raise ValueError('Invalid or repeated series video: '+id)
   members.add(id)
  slugs.add(slug)

def series_cards():
 result=[]
 for series in SERIES:
  path='series/'+series['slug']+'.html';v=BY_ID[series['parts'][0]]
  result.append(f'<article class="series-card"><a href="{link(path)}" aria-label="Explore {e(series["title"])}">{image(v,alt="")}</a><div class="card-body"><p class="label">{len(series["parts"])} chapters · complete story available</p><h3><a href="{link(path)}">{e(series["title"])}</a></h3><p>{e(series["summary"])}</p><a href="{link(path)}">Watch in order<span class="sr-only">: {e(series["title"])}</span></a></div></article>')
 return '<div class="series-grid">'+''.join(result)+'</div>'

def series_teaser():
 return '<section class="section"><div class="container"><div class="section-heading"><div><h2>One story. Every chapter.</h2><p>Start at the beginning and follow each part in order.</p></div><a href="'+link('series.html')+'">Explore the series</a></div>'+series_cards()+'</div></section>'

def series_navigation(id):
 for series in SERIES:
  if id not in series['parts']+[series['complete']]:continue
  parts=series['parts'];path='series/'+series['slug']+'.html'
  body=f'<nav class="series-navigation" aria-label="{e(series["title"])} chapters"><h2><a href="{link(path)}">{e(series["title"])}</a></h2><ol>'
  for i,part in enumerate(parts,1):body+=f'<li><a href="{link("watch/"+part+".html")}"'+(' aria-current="page"' if id==part else '')+f'>Part {i}<span class="sr-only">: {e(BY_ID[part]["title"])}</span></a></li>'
  body+='</ol><p><a href="'+link('watch/'+series['complete']+'.html')+'"'+(' aria-current="page"' if id==series['complete'] else '')+'>Watch the complete story</a></p>'
  if id in parts:
   current=parts.index(id);adjacent=[]
   if current:adjacent.append(('Previous part',parts[current-1]))
   if current+1<len(parts):adjacent.append(('Next part',parts[current+1]))
   body+='<div class="chapter-actions">'+''.join(f'<a href="{link("watch/"+target+".html")}">{label}<span class="sr-only">: {e(BY_ID[target]["title"])}</span></a>' for label,target in adjacent)+'</div>'
  return body+'</nav>'
 return ''

def series_pages():
 body='<div class="container"><header class="page-intro"><p class="eyebrow">Follow the story</p><h1>Every chapter, in order.</h1><p>Two fictional Dark Echo stories told in short chapters. Start with part one, continue to the next chapter, or watch the complete version.</p></header><section aria-labelledby="all-series-title"><h2 class="sr-only" id="all-series-title">Dark Echo video series</h2>'+series_cards()+'</section></div><div class="section"></div>'
 schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Dark Echo video series','url':canonical('series.html'),'description':'Ordered chapters and complete versions of fictional Dark Echo horror stories.','mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'name':s['title'],'url':canonical('series/'+s['slug']+'.html')} for i,s in enumerate(SERIES,1)]}}
 write_page('series.html','Dark Echo Series | Watch Horror Stories in Order','Follow Dark Echo horror series in chapter order. Find Inside the Wall and The Reflection, with short parts and complete versions.',body,active='series',schema=schema)
 for series in SERIES:
  path='series/'+series['slug']+'.html';parts=[BY_ID[id] for id in series['parts']];complete=BY_ID[series['complete']]
  body=f'<div class="container"><header class="page-intro"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{link()}">Home</a><span aria-hidden="true">/</span><a href="{link("series.html")}">Series</a></nav><p class="eyebrow">Original horror fiction · {len(parts)} chapters</p><h1>{e(series["title"])}</h1><p>{e(series["summary"])}</p>{share_tools(path)}</header><aside class="notice"><p>A fictional horror story for entertainment. Choose the ordered short chapters below or the complete version.</p></aside><section aria-labelledby="chapter-list-title"><div class="section-heading"><div><h2 id="chapter-list-title">Watch the chapters in order</h2><p>Begin with part one. Each watch page links to the next chapter.</p></div></div><div class="video-grid">'+''.join(card(v) for v in parts)+'</div></section></div>'
  body+=section('complete-story','The complete story','Prefer one video? Watch the story without changing chapters.',[complete])
  schema={'@context':'https://schema.org','@type':'CollectionPage','name':series['title']+' | Dark Echo','url':canonical(path),'description':series['summary'],'inLanguage':'en','mainEntity':{'@type':'ItemList','itemListOrder':'https://schema.org/ItemListOrderAscending','itemListElement':[{'@type':'ListItem','position':i,'name':v['title'],'url':canonical('watch/'+v['id']+'.html')} for i,v in enumerate(parts,1)]}}
  write_page(path,series['title']+' | Dark Echo Horror Series',series['summary'],body,active='series',schema=schema,social=parts[0]['thumbnail'])

def saved_page():
 body=f'<div class="container"><header class="page-intro"><p class="eyebrow">A little darkness for later</p><h1>Watch later</h1><p>Use the Save button on any video to keep it here. This list stays in this browser on this device; it is not an account or a record of what you have watched.</p></header><noscript><aside class="notice"><p>Saving videos requires JavaScript and browser storage. You can still <a href="{link("more-videos.html")}">browse the entire video archive</a> and bookmark individual watch pages in your browser.</p></aside></noscript><section data-saved-library aria-labelledby="saved-title" hidden><div class="library-toolbar"><h2 id="saved-title" tabindex="-1">Your saved videos</h2><button type="button" data-clear-saved hidden>Clear saved list</button></div><p class="fine-print" data-saved-summary role="status" aria-live="polite"></p><div class="video-grid" data-saved-grid></div><div class="empty-state" data-saved-empty><h2 tabindex="-1">Your next story is waiting.</h2><p>You have no saved videos in this browser yet.</p><a class="button button-primary" href="{link("more-videos.html")}">Find a video to save</a></div></section><p class="fine-print">Clearing site data or switching browsers removes access to this list. Saving a video does not download it. <a href="{link("privacy.html")}">How browser storage is used</a>.</p></div><div class="section"></div>'
 body+=''.join(f'<template data-saved-template="{e(v["id"])}">{card(v,heading="h3")}</template>' for v in VIDEOS)
 write_page('watch-later.html','Watch Later | Your Saved Dark Echo Videos','Keep a personal list of Dark Echo videos to watch later in this browser, without creating an account.',body,active='saved',index=False)

def information():
 about=f'''<article class="reading-layout"><p class="eyebrow">Behind the stories</p><h1 class="article-title">About Dark Echo</h1><div class="prose"><p>Dark Echo is a creator-led horror project built around unsettling stories, strange reflections, and ordinary places that become unfamiliar after dark.</p><h2>What you will find here</h2><p>The main collection brings together Dark Echo videos and original written horror fiction. Every video has a watch page, so you can return to a story or share the exact video you discovered.</p><p>The video archive also includes a clearly labelled Extreme Events collection about nature, disasters, and space. These older videos are presented with their original dates, rather than as current alerts.</p><h2>Our editorial approach</h2><p>Dark Echo horror stories and dramatized scenes are entertainment. They are not presented as authenticated paranormal footage. Written stories are labelled as fiction, and video titles, descriptions, images, and running times are linked to a single catalog entry.</p><h2>A separate tutorial archive</h2><p><a href="{link('earn-with-nasser.html')}">Earn With Nasser</a> preserves earlier tutorials by the creator. Its topics include software, online work, and gaming, and its historical information may no longer describe current services.</p><h2>Get in touch</h2><p>Have a suggestion or spotted an incorrect video? <a href="{link('contact.html')}">Send website feedback</a> or join the conversation on the <a href="{CHANNEL}" target="_blank" rel="noopener noreferrer">Dark Echo channel</a>.</p></div></article>'''
 write_page('about.html','About Dark Echo | Horror Fiction & Video Collections','Learn about Dark Echo, its fictional horror stories, video collections, editorial approach, and separate historical tutorial archive.',about,active='about')
 contact=f'''<div class="container"><header class="page-intro"><p class="eyebrow">Tell us what you found</p><h1>Contact & feedback</h1><p>Report an incorrect title, a broken page, a playback problem, or an idea for the site.</p></header><div class="contact-grid"><section class="contact-box"><h2>Report a website problem</h2><p>Open the short feedback form and include the page link, what happened, and what you expected. A clear example makes the problem easier to fix.</p><a class="button button-primary" href="{ISSUES}" target="_blank" rel="noopener noreferrer" data-track="feedback_open">Send website feedback</a><p class="fine-print">The form opens on GitHub. You will need a GitHub account, and submitted reports are public.</p></section><section class="contact-box"><h2>Talk about the videos</h2><p>For story suggestions, questions about a clip, or a conversation with the creator, visit Dark Echo on YouTube and leave a comment on the relevant video.</p><a class="button" href="{CHANNEL}" target="_blank" rel="noopener noreferrer" data-track="channel_open">Visit Dark Echo on YouTube</a></section></div><section class="section prose"><h2>Useful details to include</h2><ul><li>The exact page or video title.</li><li>Your browser and whether you are on a phone or computer.</li><li>What you clicked and what appeared.</li></ul><p>For questions about analytics, read the <a href="{link('privacy.html')}">privacy policy</a>. <button class="button button-small" type="button" data-consent-manage hidden>Change analytics choices</button></p></section></div>'''
 write_page('contact.html','Contact Dark Echo | Website Feedback & Video Questions','Report a broken page, incorrect video title, or playback problem using Dark Echo’s website feedback form, or join the conversation on YouTube.',contact,active='contact')
 privacy=f'''<article class="reading-layout"><p class="eyebrow">Your choices</p><h1 class="article-title">Privacy policy</h1><p class="article-meta">Updated <time datetime="{TODAY}">{date(TODAY)}</time></p><div class="prose"><h2>Browsing the website</h2><p>Dark Echo does not require an account or collect messages through a form hosted on this website. The hosting provider may process technical request information needed to serve pages. Search and filters run in your browser; their state may be included in the page URL so you can share the same results.</p><h2>Your watch-later list</h2><p>If you use Save for later, video identifiers are stored in this browser on this device. We do not send this list to a server or synchronize it to an account. You can remove individual videos or clear the list on the <a href="{link('watch-later.html')}">Watch later page</a>. If storage is unavailable, saves last only for the current page. Clearing site data removes saved videos and the remembered Analytics choice.</p><h2>Optional Google Analytics</h2><p>Google Analytics loads only after you choose “Allow analytics,” or if your browser remembers an earlier agreement. Choosing “Reject analytics” lets you browse without loading the Analytics tag.</p><p>When allowed, Analytics can receive page, browser, device, approximate location, and engagement information. We also measure actions such as opening a video, following a YouTube link, or moving from a story to a video. Advertising storage and personalization remain disabled in this site’s configuration.</p><h2>Remembering and changing your choice</h2><p>Your choice is stored in browser local storage. If Analytics is enabled, it may use cookies. You can change the choice using the button below or “Analytics choices” in the footer. Changing from allow to reject disables measurement, clears known Analytics cookies for this site, and reloads the page.</p><p><button class="button" type="button" data-consent-manage hidden>Change analytics preference</button></p><h2>YouTube playback</h2><p>Collection pages use locally hosted thumbnail images. Their YouTube player loads when you choose quick play. Individual watch pages include a visible YouTube player as the main content of the page.</p><p>We use YouTube’s privacy-enhanced player. Viewing or interacting with embedded videos may still involve Google or YouTube processing information under their own policies. The Analytics choice controls this website’s optional Analytics tag; it does not control YouTube playback or its separate processing.</p><h2>External links and feedback</h2><p>Following a YouTube or GitHub link takes you to that provider. The website feedback form is hosted on GitHub, requires an account, and creates a public report when you submit it. We do not submit that form on your behalf.</p><h2>Questions and updates</h2><p>Use the <a href="{link('contact.html')}">contact page</a> for questions about the site or this policy. This page will be updated when the site’s services or choices change.</p></div></article>'''
 write_page('privacy.html','Privacy Policy | Dark Echo','Read how Dark Echo handles optional Google Analytics, YouTube embeds, stored privacy choices, search filters, and website feedback.',privacy,active='privacy')
 error=f'<section class="page-intro container"><p class="eyebrow">404 · A missing scene</p><h1>This page slipped into the dark.</h1><p>The address may be incomplete, or the page may have moved. Find a new story or return to the video archive.</p><div class="section actions"><a class="button button-primary" href="{link()}">Back to Dark Echo</a><a class="button" href="{link("more-videos.html")}">Browse videos</a></div></section>'
 write_page('404.html','Page Not Found | Dark Echo','This Dark Echo page could not be found. Return home or explore the video archive.',error,index=False)

def sitemap():
 urls=[p for p in GENERATED if p['index']]
 body='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
 for p in urls:body+=f'  <url><loc>{e(canonical(p["path"]))}</loc><lastmod>{p["modified"]}</lastmod></url>\n'
 body+='</urlset>\n';(ROOT/'sitemap.xml').write_text(body)
 (ROOT/'robots.txt').write_text('# Project-path copy. Host robots rules must be served from /robots.txt.\nUser-agent: *\nAllow: /\n\nSitemap: '+BASE+'sitemap.xml\n')
 (ROOT/'data/build-manifest.json').write_text(json.dumps({'version':SITE['revision'],'catalogUpdated':UPDATED,'generated':GENERATED},indent=2)+'\n')

def main():
 GENERATED.clear()
 validate_catalog(CATALOG)
 if len(BY_ID)!=len(VIDEOS):raise ValueError('Duplicate video IDs in canonical catalog')
 for v in VIDEOS:
  if not re.fullmatch(r'[A-Za-z0-9_-]{11}',v['id']):raise ValueError('Invalid video ID')
  if not (ROOT/v['thumbnail']).exists():raise ValueError('Missing thumbnail: '+v['id'])
 validate_series();home();library_page();library_page(legacy=True);blog();article_pages();watch_pages();series_pages();saved_page();information();sitemap()
 print(f'Built {len(GENERATED)} pages; {len(VIDEOS)} videos; {sum(p["index"] for p in GENERATED)} sitemap URLs.')

if __name__=='__main__':main()
