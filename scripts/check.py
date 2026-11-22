#!/usr/bin/env python3
"""Validate generated links, media identity, structured data and index boundaries."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import base64,hashlib,json,re,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BASE='https://darkechoproject.github.io/darkecho/'
PREFIX='/darkecho/'
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
  require(not any(key.startswith('on') for key in a),f'{path}: inline event handler disallowed by CSP')
  require('style' not in a,f'{path}: inline style disallowed by CSP')
  if tag=='a' and a.get('target')=='_blank':require({'noopener','noreferrer'}<=set(a.get('rel','').split()),f'{path}: unsafe external window link')
  if tag=='img':
   require('alt' in a and bool(a.get('width')) and bool(a.get('height')),f'{path}: missing image dimensions or alternative text')
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
   if u.fragment and targetpath in docs:require(u.fragment in docs[targetpath].ids,f'{path}: missing fragment {value}')

require(len(videos)==89,'Unexpected loss or duplication of catalog videos')
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
