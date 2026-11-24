#!/usr/bin/env python3
"""Validate generated links, media identity, structured data and index boundaries."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import base64,hashlib,json,re,xml.etree.ElementTree as ET
from catalog import validate_catalog

ROOT=Path(__file__).resolve().parents[1]
BASE=json.loads((ROOT/'data/site.json').read_text())['baseUrl']
PREFIX=urlsplit(BASE).path
catalog=json.loads((ROOT/'data/videos.json').read_text(encoding='utf-8'))
videos={v['id']:v for v in catalog['videos']}
manifest=json.loads((ROOT/'data/build-manifest.json').read_text())['generated']

class Document(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.nodes=[];self.ids=[];self.title='';self.h1=0;self.main=0;self.schemas=[];self._schema=None;self._title=False;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.nodes.append((tag,a))
  if a.get('id'):self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='main':self.main+=1
  if tag=='title':self._title=True
  if tag=='script' and a.get('type')=='application/ld+json':self._schema=''
 def handle_endtag(self,tag):
  if tag=='title':self._title=False
  if tag=='script' and self._schema is not None:self.schemas.append(self._schema);self._schema=None
 def handle_data(self,data):
  if self._title:self.title+=data
  if self._schema is not None:self._schema+=data

docs={item['path']:Document((ROOT/item['path']).read_text(encoding='utf-8')) for item in manifest}
errors=[];link_count=0;card_count=0
def require(condition,message):
 if not condition:errors.append(message)
for item in manifest:
 path=item['path'];doc=docs[path]
 require(doc.h1==1,f'{path}: expected one H1')
 require(doc.main==1,f'{path}: expected one main landmark')
 require(bool(doc.title.strip()),f'{path}: missing title')
 require(not [key for key,n in Counter(doc.ids).items() if n>1],f'{path}: duplicate element IDs')
 metas={a.get('name') or a.get('property') or a.get('http-equiv'):a.get('content') for tag,a in doc.nodes if tag=='meta'}
 expected=BASE+('' if path=='index.html' else path)
 require(any(tag=='link' and a.get('rel')=='canonical' and a.get('href')==expected for tag,a in doc.nodes),f'{path}: incorrect canonical')
 require(('noindex' not in metas.get('robots',''))==item['index'],f'{path}: index policy mismatch')
 require(bool(metas.get('description')),f'{path}: missing description')
 require(metas.get('referrer')=='strict-origin-when-cross-origin',f'{path}: missing referrer policy')
 for raw in doc.schemas:
  try:schema=json.loads(raw)
  except Exception as ex:errors.append(f'{path}: invalid JSON-LD {ex}');continue
  digest=base64.b64encode(hashlib.sha256(raw.encode()).digest()).decode()
  require('sha256-'+digest in metas.get('Content-Security-Policy',''),f'{path}: structured-data CSP hash mismatch')
  if path.startswith('watch/'):
   id=Path(path).stem;v=videos[id]
   require(schema.get('@type')=='VideoObject',f'{path}: missing VideoObject')
   require(schema.get('name')==v['title'] and schema.get('duration')==v['duration'] and schema.get('uploadDate')==v['uploadDate'],f'{path}: video schema differs from catalog')
   require('/embed/'+id+'?' in schema.get('embedUrl',''),f'{path}: schema embed points to another video')
   require(any(t=='iframe' and '/embed/'+id+'?' in a.get('src','') for t,a in doc.nodes),f'{path}: no directly rendered watch iframe')
 for tag,a in doc.nodes:
  for attr in ['aria-controls','aria-labelledby','aria-describedby']:
   for target in a.get(attr,'').split():require(target in doc.ids,f'{path}: {attr} references missing ID {target}')
  require(not any(key.startswith('on') for key in a),f'{path}: inline event handler disallowed by CSP')
  require('style' not in a,f'{path}: inline style disallowed by CSP')
  if tag=='a' and a.get('target')=='_blank':require({'noopener','noreferrer'}<=set(a.get('rel','').split()),f'{path}: unsafe external window link')
  if tag=='img':
   require('alt' in a and bool(a.get('width')) and bool(a.get('height')),f'{path}: missing image dimensions or alternative text')
   for candidate in a.get('srcset','').split(','):
    if not candidate.strip():continue
    src=candidate.strip().split()[0]
    require(src.startswith(PREFIX) and (ROOT/unquote(urlsplit(src).path[len(PREFIX):])).is_file(),f'{path}: missing responsive image {src}')
  if 'data-save-video' in a:
   v=videos.get(a['data-save-video'])
   require(v is not None and a.get('data-save-title')==v['title'],f'{path}: saved-video identity mismatch')
   require('hidden' in a and a.get('aria-pressed')=='false',f'{path}: save control must be progressively enhanced')
  if 'data-copy-link' in a:require(a['data-copy-link']==expected and 'hidden' in a,f'{path}: incorrect copy link or no-JS control')
  if 'data-consent-manage' in a or 'menu-toggle' in a.get('class','').split():require('hidden' in a,f'{path}: inert no-JS control')
  if tag=='a' and 'data-video-id' in a:
   card_count+=1;id=a['data-video-id'];v=videos.get(id)
   require(v is not None,f'{path}: unknown video ID {id}')
   if v:require(a.get('data-video-title')==v['title'] and a.get('href')==PREFIX+'watch/'+id+'.html',f'{path}: inconsistent play title or destination {id}')
  for attribute in ['href','src']:
   value=a.get(attribute,'')
   if not value or value.startswith(('data:','mailto:','tel:','https://www.youtube','https://github.com')):continue
   u=urlsplit(value)
   if u.scheme and u.netloc!='darkechoproject.github.io':continue
   targetpath=unquote(u.path)
   if targetpath.startswith(PREFIX):targetpath=targetpath[len(PREFIX):] or 'index.html'
   elif targetpath=='':targetpath=path
   else:continue
   link_count+=1
   require((ROOT/targetpath).is_file(),f'{path}: missing target {value}')
   if u.query and tag in ['link','script'] and (ROOT/targetpath).is_file():
    digest=hashlib.sha256((ROOT/targetpath).read_bytes()).hexdigest()[:12]
    require(u.query=='v='+digest,f'{path}: stale asset version {value}')
   if u.fragment and targetpath in docs:require(u.fragment in docs[targetpath].ids,f'{path}: missing fragment {value}')

try:validate_catalog(catalog)
except (ValueError,KeyError,TypeError) as error:errors.append('Catalog: '+str(error))
require(len(videos)==len(catalog['videos']),'Duplicate catalog video IDs')
require(len(docs)==len(manifest),'Duplicate generated page paths')
for id,v in videos.items():
 require(re.fullmatch('[A-Za-z0-9_-]{11}',id) is not None,'Invalid video ID')
 require(v['format']==('clip' if v['seconds']<=180 else 'video'),f'Wrong length category {id}')
 for width in [320,640]:require((ROOT/f'assets/thumbs/{id}-{width}.webp').is_file(),f'Missing optimized thumbnail {id} {width}')
 require(('watch/'+id+'.html') in docs,f'Missing watch page {id}')
 expectedindex=v['channel']!='nasser'
 require(next(x for x in manifest if x['path']=='watch/'+id+'.html')['index']==expectedindex,f'Legacy watch page index policy {id}')

sitemap=ET.parse(ROOT/'sitemap.xml');urls=sitemap.findall('{*}url/{*}loc');url_values=[u.text for u in urls]
expected_urls={BASE+('' if item['path']=='index.html' else item['path']) for item in manifest if item['index']}
require(set(url_values)==expected_urls and len(url_values)==len(expected_urls),'Sitemap misses pages, has duplicates, or indexes excluded archive pages')
require('404.html' not in ' '.join(url_values) and not any('earn-with-nasser' in x for x in url_values),'Nonindexable pages leaked into sitemap')
for article in json.loads((ROOT/'data/articles.json').read_text()):
 doc=docs[article['file']];schema=json.loads(doc.schemas[0]);require(schema.get('genre')=='Horror fiction',f'{article["file"]}: fiction label missing')
 require(schema.get('dateModified')==article['updated'],f'{article["file"]}: incorrect modification date')

# Research files retain their external publisher identity and cited evidence.
for case in json.loads((ROOT/'data/mysteries.json').read_text()):
 path='mysteries/'+case['slug']+'.html'
 require(path in docs,'Missing mystery file '+path)
 if path not in docs:continue
 doc=docs[path];schema=json.loads(doc.schemas[0])
 require(schema.get('@type')=='Article' and schema.get('articleSection')=='Internet mystery analysis',path+': research file mislabelled')
 require(schema.get('genre')!='Horror fiction',path+': source check labelled as invented fiction')
 require(schema.get('dateModified')==case['updated'],path+': incorrect source-check date')
 source_urls=[source['url'] for source in case['sources']]
 require(schema.get('citation')==source_urls,path+': structured citations differ from source record')
 hrefs={a.get('href') for tag,a in doc.nodes if tag=='a'}
 require(set(source_urls)<=hrefs,path+': a source link is missing')
 require({'source-'+source['id'] for source in case['sources']}<=set(doc.ids),path+': missing cited source anchors')
 frames=[a.get('src') for tag,a in doc.nodes if tag=='iframe']
 require(frames==['https://www.youtube-nocookie.com/embed/'+case['video']['id']+'?rel=0'],path+': incorrect publisher video or unexpected player')
 require(schema.get('about',{}).get('publisher',{}).get('name')==case['video']['creator'],path+': publisher attribution mismatch')

for series in json.loads((ROOT/'data/series.json').read_text()):
 path='series/'+series['slug']+'.html';require(path in docs,'Missing series page '+path)
 if path not in docs:continue
 schema=json.loads(docs[path].schemas[0]);items=schema.get('mainEntity',{}).get('itemListElement',[])
 require([x.get('url') for x in items]==[BASE+'watch/'+id+'.html' for id in series['parts']],path+': chapter order mismatch')
 require([x.get('position') for x in items]==list(range(1,len(series['parts'])+1)),path+': incorrect chapter positions')
 for id in series['parts']+[series['complete']]:
  require(id in videos,'Series references missing video '+id)
  current=[a.get('href') for tag,a in docs['watch/'+id+'.html'].nodes if a.get('aria-current')=='page' and a.get('href','').startswith(PREFIX+'watch/')]
  require(current==[PREFIX+'watch/'+id+'.html'],'Series navigation has an incorrect current chapter '+id)
saved=docs.get('watch-later.html')
require(saved is not None,'Missing saved-video page')
if saved:require({a['data-saved-template'] for t,a in saved.nodes if 'data-saved-template' in a}==set(videos),'Watch-later templates differ from catalog')

for css in (ROOT/'assets').glob('*.css'):
 for target in re.findall(r'url\([\'\"]?([^\)\'\"]+)',css.read_text()):
  if target.startswith('data:'):continue
  require((css.parent/target).is_file(),f'{css.name}: missing CSS resource {target}')

# Validate the two curated home sections against the canonical metadata order.
home=(ROOT/'index.html').read_text()
for section,key in [('latest','uploadDate'),('most-watched','views')]:
 fragment=home.split('id="'+section+'"',1)[1].split('</section>',1)[0]
 actual=re.findall(r'data-video-id="([A-Za-z0-9_-]{11})"',fragment)
 expected=[v['id'] for v in sorted((v for v in videos.values() if v['channel']=='darkecho'),key=lambda v:v[key],reverse=True)[:6]]
 require(actual==expected,f'Home {section} section violates its sorting rule')

if errors:
 for error in errors:print('FAIL:',error)
 raise SystemExit(f'{len(errors)} validation failures')
print(f'PASS: {len(docs)} pages, {len(videos)} video identities, {link_count} local links/resources, {card_count} play links, {len(urls)} sitemap URLs; metadata, CSP hashes, sorting and archive boundaries validated.')
