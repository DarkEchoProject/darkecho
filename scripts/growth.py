"""Source-led guides, localized case files and the evidence quiz."""
import copy
import json
import re
from math import ceil
from urllib.parse import urlsplit

WORDS = {
    'en': {
        'home': 'Home', 'files': 'Mystery files', 'by': 'By Dark Echo Editorial',
        'published': 'Published', 'updated': 'Updated', 'checked': 'Sources checked',
        'inside': 'Inside this file', 'video': 'The publisher’s video', 'evidence': 'Evidence at a glance',
        'timeline': 'The documented timeline', 'sources': 'Sources and dates', 'verdict': 'What the sources support',
        'editorial': 'Source-based editorial analysis. Interpretations are labelled separately from documented facts.',
        'watch': 'Watch the publisher’s upload', 'before': 'Before you play:', 'publisher': 'Published by',
        'upload': 'This upload', 'sourcevideo': 'Open the source video on YouTube',
        'playernote': 'The publisher retains the video. Playback is provided by YouTube and can vary by region or availability.',
        'claim': 'Claim', 'status': 'Status', 'record': 'What the record supports',
        'sourcecaption': 'Claims and the records supporting them', 'accessed': 'Accessed',
        'sourcenote': 'Source dates identify their publication where established; otherwise the access date is shown.',
        'analysis': 'Editorial interpretation · not a creator-confirmed solution',
        'next': 'Keep investigating', 'guides': 'Read the field guides', 'quiz': 'Try Fact or Fiction?',
        'readfile': 'Open case file', 'label': 'Internet mystery · source check', 'case': 'Case file',
        'videoLength': 'Video', 'translated': 'Read this file in Arabic',
    },
    'ar': {
        'home': 'الرئيسية', 'files': 'ملفات الغموض', 'by': 'إعداد وتحرير دارك إيكو',
        'published': 'نُشر', 'updated': 'حُدّث', 'checked': 'مراجعة المصادر',
        'inside': 'محتويات الملف', 'video': 'فيديو الناشر الأصلي', 'evidence': 'الادعاءات والأدلة',
        'timeline': 'التسلسل الزمني الموثّق', 'sources': 'المصادر وتواريخها', 'verdict': 'ما الذي تثبته المصادر؟',
        'editorial': 'تحليل مبني على مصادر منشورة، مع فصل التفسير التحريري عن الوقائع الموثّقة.',
        'watch': 'شاهد نسخة الناشر الأصلي', 'before': 'قبل المشاهدة:', 'publisher': 'الناشر',
        'upload': 'تاريخ هذه النسخة', 'sourcevideo': 'افتح الفيديو الأصلي على يوتيوب',
        'playernote': 'يبقى الفيديو لدى ناشره. يقدّم يوتيوب التشغيل، وقد يختلف توفره حسب المنطقة أو حالة الفيديو.',
        'claim': 'الادعاء', 'status': 'التقييم', 'record': 'ما تدعمه المعلومات المنشورة',
        'sourcecaption': 'الادعاءات والمعلومات التي تدعم تقييمها', 'accessed': 'تاريخ الاطلاع',
        'sourcenote': 'نعرض تاريخ نشر المصدر عندما يكون معروفًا، وإلا نذكر تاريخ الاطلاع عليه بوضوح.',
        'analysis': 'قراءة تحريرية؛ ليست حلًا أكّده صانع العمل',
        'next': 'تابع الاستكشاف', 'guides': 'أدلة للمبتدئين بالإنجليزية', 'quiz': 'جرّب اختبار «حقيقة أم تمثيل؟»',
        'readfile': 'اقرأ الملف', 'label': 'غموض الإنترنت · فحص المصادر', 'case': 'ملف',
        'videoLength': 'مدة الفيديو', 'translated': 'Read this file in English',
    },
}


class Growth:
    def __init__(self, builder):
        self.b = builder
        self.root = builder.ROOT
        self.guides = json.loads((self.root / 'data/guides.json').read_text(encoding='utf-8'))
        self.arabic = json.loads((self.root / 'data/mysteries-ar.json').read_text(encoding='utf-8'))
        self.quiz = json.loads((self.root / 'data/quiz.json').read_text(encoding='utf-8'))

    def day(self, value, lang='en'):
        if lang != 'ar':
            return self.b.date(value)
        y, m, d = map(int, value[:10].split('-'))
        months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        return f'{d} {months[m-1]} {y}'

    def time(self, value, lang='en'):
        return f'<time datetime="{self.b.e(value)}">{self.day(value, lang)}</time>'

    @staticmethod
    def path(case, lang='en'):
        return ('ar/' if lang == 'ar' else '') + 'mysteries/' + case['slug'] + '.html'

    def localized(self, original, lang):
        if lang == 'en':
            return original
        result = copy.deepcopy(original)
        translation = self.arabic[original['slug']]
        result.pop('shareTitle', None)
        if translation.get('shareTitle'):
            result['shareTitle'] = translation['shareTitle']
        for key in ('title', 'deck', 'verdict', 'sections', 'evidence', 'timeline', 'sources', 'published', 'updated', 'checked'):
            result[key] = translation[key]
        result['video']['contentNote'] = translation['videoNote']
        return result

    def card_items(self):
        items = []
        for original in self.b.MYSTERIES:
            for lang in ['en', 'ar'] if original['slug'] in self.arabic else ['en']:
                case = self.localized(original, lang)
                theme = 'maze' if 'backrooms' in case['slug'] else 'house' if 'house' in case['slug'] else 'signal'
                items.append({'page': self.path(case, lang), 'key': 'mystery-' + case['slug'] + '-' + lang, 'lang': lang,
                              'title': case.get('shareTitle', case['title']), 'label': ('ملفات الغموض' if lang == 'ar' else 'INTERNET MYSTERY FILES'), 'theme': theme})
        for guide in self.guides:
            items.append({'page': 'guides/' + guide['slug'] + '.html', 'key': 'guide-' + guide['slug'], 'title': guide['title'], 'label': 'THE DARK ECHO FIELD GUIDES', 'theme': 'guide'})
        for lang in ['en', 'ar']:
            items.append({'page': ('ar/' if lang == 'ar' else '') + 'quiz.html', 'key': 'quiz-' + lang, 'lang': lang,
                          'title': 'حقيقة أم تمثيل؟' if lang == 'ar' else 'Fact or Fiction?', 'label': 'خمسة ادعاءات. افحص الدليل.' if lang == 'ar' else 'FIVE CLAIMS. FOLLOW THE EVIDENCE.', 'theme': 'quiz'})
        items += [
            {'page': 'guides.html', 'key': 'guides', 'title': 'A field guide to internet horror', 'label': 'THE DARK ECHO FIELD GUIDES', 'theme': 'guide'},
            {'page': 'ar/index.html', 'key': 'arabic', 'lang': 'ar', 'title': 'الغموض يستحق نظرة أقرب', 'label': 'دارك إيكو بالعربية', 'theme': 'signal'},
        ]
        return items

    def validate(self):
        b = self.b
        cases = {case['slug']: case for case in b.MYSTERIES}
        for slug, tr in self.arabic.items():
            if slug not in cases:
                raise ValueError('Translation without original: ' + slug)
            original = cases[slug]
            if {s['id'] for s in tr['sources']} != {s['id'] for s in original['sources']}:
                raise ValueError('Translation source IDs differ: ' + slug)
            urls = {s['id']: s['url'] for s in original['sources']}
            if any(s['url'] != urls[s['id']] for s in tr['sources']):
                raise ValueError('Translated file must preserve source URLs: ' + slug)
            if [s['id'] for s in tr['sections']] != [s['id'] for s in original['sections']]:
                raise ValueError('Translation sections differ: ' + slug)
            for group in ['sections', 'evidence', 'timeline']:
                for row in tr[group]:
                    if not set(row['sources']) <= urls.keys():
                        raise ValueError('Unknown translated citation: ' + slug)
            for key in ['published', 'updated', 'checked']:
                b.date(tr[key])
        slugs = set()
        for guide in self.guides:
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',guide['slug']) or guide['slug'] in slugs:
                raise ValueError('Invalid or repeated guide slug')
            slugs.add(guide['slug'])
            for key in ['published','updated']:
                b.date(guide[key])
            if not set(guide['related']) <= cases.keys():
                raise ValueError('Unknown related case in guide')
            ids = {s['id'] for s in guide['sources']}
            if len(ids) != len(guide['sources']):
                raise ValueError('Repeated guide source')
            if len({s['id'] for s in guide['sections']}) != len(guide['sections']):
                raise ValueError('Repeated guide section')
            for source in guide['sources']:
                if urlsplit(source['url']).scheme != 'https':
                    raise ValueError('Guide sources require HTTPS')
                b.date(source.get('date') or source['checked'])
            for section in guide['sections']:
                if not set(section.get('sources', [])) <= ids:
                    raise ValueError('Unknown guide citation')
        questions = self.quiz['questions']
        if len(questions) != 5 or len({q['id'] for q in questions}) != 5:
            raise ValueError('Quiz must have five distinct questions')
        for question in questions:
            if type(question['answer']) is not bool or question['case'] not in cases or question['case'] not in self.arabic:
                raise ValueError('Invalid quiz answer or case')
            case = cases[question['case']]
            valid = {'evidence', 'timeline', 'sources'} | {s['id'] for s in case['sections']}
            if question['section'] not in valid:
                raise ValueError('Quiz source anchor missing')
            for lang in ['en', 'ar']:
                if not question[lang]['claim'] or not question[lang]['explanation']:
                    raise ValueError('Missing quiz translation')

    def citations(self, item, ids, lang='en'):
        b = self.b
        sources = {s['id']: (i, s) for i, s in enumerate(item['sources'], 1)}
        word = 'المصدر' if lang == 'ar' else 'Source'
        return ' '.join(f'<a class="source-ref" href="#source-{b.e(id)}" aria-label="{word} {sources[id][0]}: {b.e(sources[id][1]["label"])}">[{sources[id][0]}]</a>' for id in ids)

    def source_list(self, item, lang='en'):
        b = self.b; w = WORDS[lang]
        rows = []
        for source in item['sources']:
            stamp = self.time(source.get('date') or source['checked'], lang)
            if not source.get('date'):
                stamp = w['accessed'] + ' ' + stamp
            rows.append(f'<li id="source-{b.e(source["id"])}"><a href="{b.e(source["url"])}" target="_blank" rel="noopener noreferrer">{b.e(source["label"])}</a><p class="fine-print">{b.e(source["kind"])} · {stamp}</p><p>{b.e(source["note"])}</p></li>')
        return f'<section class="case-sources" id="sources" aria-labelledby="sources-title"><h2 id="sources-title">{w["sources"]}</h2><p class="fine-print">{w["sourcenote"]}</p><ol>{"".join(rows)}</ol></section>'

    def case_card(self, original, lang='en', heading='h2'):
        b = self.b; w = WORDS[lang]; case = self.localized(original, lang); path = self.path(case, lang)
        image = b.SOCIAL[path]
        minutes = max(1, ceil(b.case_words(case) / (180 if lang == 'ar' else 200)))
        reading = f'نحو {minutes} دقائق قراءة' if lang == 'ar' else f'About {minutes} min read'
        return f'<article class="case-file-card"><div class="case-art-visual"><img src="{b.link(image)}" width="1200" height="630" alt="" loading="lazy" decoding="async"></div><div class="case-card-body"><p class="label">{w["label"]}</p><{heading}><a href="{b.link(path)}">{b.e(case["title"])}</a></{heading}><p>{b.e(case["deck"])}</p><p class="fine-print">{reading} · {w["videoLength"]} <bdi>{b.duration(case["video"]["seconds"])}</bdi></p><p class="case-card-verdict">{b.e(case["verdict"])}</p><a class="button" href="{b.link(path)}" data-track="casefile_open">{w["readfile"]}<span class="sr-only">: {b.e(case["title"])}</span></a></div></article>'

    def mystery_pages(self):
        b = self.b
        body = '<div class="container"><header class="page-intro"><p class="eyebrow">Internet mystery files</p><h1>Strange videos. A traceable story.</h1><p>Original publishers, dated records, and a closer look at the stories behind unsettling internet videos. Read the evidence, then explore clearly labelled interpretations.</p><div class="actions"><a class="button" href="' + b.link('guides.html') + '">Start with the field guides</a><a class="button" href="' + b.link('quiz.html') + '">Try Fact or Fiction?</a><a class="button" href="' + b.link('ar/index.html') + '" lang="ar" dir="rtl">اقرأ بالعربية</a></div></header><div class="case-list">'
        body += ''.join(self.case_card(case) for case in b.MYSTERIES)
        body += '</div><section class="section prose"><h2>What a case file includes</h2><p>Each file identifies the publisher, dates the reviewed records, and distinguishes documented facts from interpretations. A frightening style alone does not establish a video’s origin. The videos remain in their publishers’ players; the source checks and commentary are by Dark Echo.</p></section></div>'
        b.write_page('mysteries.html', 'Internet Mystery Files | Dark Echo', 'Explore unsettling videos through original publishers, evidence, dated timelines and clearly labelled interpretations.', body, active='mysteries', schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Dark Echo internet mystery files','url':b.canonical('mysteries.html'),'inLanguage':'en','mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'name':c['title'],'url':b.canonical(self.path(c))} for i,c in enumerate(b.MYSTERIES,1)]}}, alternates={'en':'mysteries.html','ar':'ar/index.html'})
        for case in b.MYSTERIES:
            self.render_case(case, 'en')
            if case['slug'] in self.arabic:
                self.render_case(case, 'ar')

    def render_case(self, original, lang):
        b = self.b; w = WORDS[lang]; case = self.localized(original, lang); path = self.path(case, lang); v = case['video']
        index = 'ar/index.html' if lang == 'ar' else 'mysteries.html'
        other_lang = 'en' if lang == 'ar' else 'ar'
        has_other = original['slug'] in self.arabic
        alternates = {key:self.path(original,key) for key in ['en','ar']} if has_other else None
        minutes = max(1, ceil(b.case_words(case) / (180 if lang == 'ar' else 200)))
        reading = f'نحو {minutes} دقائق قراءة' if lang == 'ar' else f'About {minutes} min read'
        language_link = f'<p class="language-switch"><a href="{b.link(self.path(case,other_lang))}" lang="{other_lang}" hreflang="{other_lang}">{w["translated"]}</a></p>' if has_other else ''
        body = f'<article class="reading-layout"><nav class="breadcrumbs" aria-label="{"مسار الصفحة" if lang=="ar" else "Breadcrumb"}"><a href="{b.link("ar/index.html" if lang=="ar" else "")}">{w["home"]}</a><span aria-hidden="true">/</span><a href="{b.link(index)}">{w["files"]}</a></nav><header><p class="eyebrow">{w["case"]} <bdi>{b.e(case["number"])}</bdi> · {w["label"]}</p><h1 class="article-title">{b.e(case["title"])}</h1><p class="article-deck">{b.e(case["deck"])}</p><p class="article-meta"><span>{w["by"]}</span><span>{w["published"]} {self.time(case["published"],lang)}</span><span>{w["updated"]} {self.time(case["updated"],lang)}</span><span>{w["checked"]} {self.time(case["checked"],lang)}</span><span>{reading}</span></p>{language_link}{b.share_tools(path,case["title"],lang)}</header>'
        body += f'<aside class="case-verdict" aria-labelledby="source-check-title"><h2 id="source-check-title">{w["verdict"]}</h2><p>{b.e(case["verdict"])}</p><p class="fine-print">{w["editorial"]}</p></aside><nav class="story-contents" aria-label="{w["inside"]}"><h2>{w["inside"]}</h2><ol>'
        body += ''.join(f'<li><a href="#{id}">{label}</a></li>' for id,label in [('publisher-video',w['video']),('evidence',w['evidence']),('timeline',w['timeline'])])
        body += ''.join(f'<li><a href="#{b.e(s["id"])}">{b.e(s["title"])}</a></li>' for s in case['sections']) + f'<li><a href="#sources">{w["sources"]}</a></li></ol></nav>'
        embed = 'https://www.youtube-nocookie.com/embed/' + v['id'] + '?rel=0'
        body += f'<section class="case-player" id="publisher-video" aria-labelledby="publisher-video-title"><h2 id="publisher-video-title">{w["watch"]}</h2><aside class="notice"><p><strong>{w["before"]}</strong> {b.e(v["contentNote"])}</p></aside><div class="watch-video"><iframe src="{embed}" title="{b.e(v["title"])} — {w["publisher"]} {b.e(v["creator"])}" width="1280" height="720" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div><p class="fine-print">{w["publisher"]} <a href="{b.e(v["creatorUrl"])}" target="_blank" rel="noopener noreferrer"><bdi>{b.e(v["creator"])}</bdi></a> · {w["upload"]}: {self.time(v["uploadDate"],lang)} · <bdi>{b.duration(v["seconds"])}</bdi></p><p><a href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener noreferrer" data-track="casefile_source_video">{w["sourcevideo"]}</a></p><p class="fine-print">{w["playernote"]}</p></section>'
        body += f'<section class="case-evidence" id="evidence" aria-labelledby="evidence-title"><h2 id="evidence-title">{w["evidence"]}</h2><table><caption class="sr-only">{w["sourcecaption"]}</caption><thead><tr><th scope="col">{w["claim"]}</th><th scope="col">{w["status"]}</th><th scope="col">{w["record"]}</th></tr></thead><tbody>'
        body += ''.join(f'<tr><th scope="row">{b.e(row["claim"])}</th><td data-label="{w["status"]}">{b.e(row["status"])}</td><td data-label="{w["record"]}">{b.e(row["detail"])} {self.citations(case,row["sources"],lang)}</td></tr>' for row in case['evidence']) + '</tbody></table></section>'
        body += f'<section class="case-timeline" id="timeline" aria-labelledby="timeline-title"><h2 id="timeline-title">{w["timeline"]}</h2><ol>'
        body += ''.join(f'<li>{self.time(t["date"],lang)}<h3>{b.e(t["label"])}</h3><p>{b.e(t["text"])} {self.citations(case,t["sources"],lang)}</p></li>' for t in case['timeline']) + '</ol></section><div class="prose">'
        for section in case['sections']:
            body += f'<section id="{b.e(section["id"])}"' + (' class="interpretation-note"' if section.get('interpretation') else '') + f'><h2>{b.e(section["title"])}</h2>'
            if section.get('interpretation'):
                body += f'<p class="label">{w["analysis"]}</p>'
            body += ''.join('<p>' + b.e(p) + '</p>' for p in section['paragraphs'])
            if section['sources']:
                body += f'<p class="case-citations">{w["sources"]}: {self.citations(case,section["sources"],lang)}</p>'
            body += '</section>'
        body += '</div>' + self.source_list(case,lang)
        body += f'<section class="related-box"><h2>{w["next"]}</h2><ul>'
        others = [c for c in b.MYSTERIES if c['slug'] != original['slug'] and (lang == 'en' or c['slug'] in self.arabic)][:2]
        body += ''.join(f'<li><a href="{b.link(self.path(c,lang))}">{b.e(self.localized(c,lang)["title"])}</a></li>' for c in others)
        body += f'<li><a href="{b.link(("ar/" if lang=="ar" else "")+"quiz.html")}">{w["quiz"]}</a></li><li><a href="{b.link("guides.html")}"' + (' lang="en" hreflang="en"' if lang == 'ar' else '') + f'>{w["guides"]}</a></li></ul></section></article>'
        schema = {'@context':'https://schema.org','@type':'Article','headline':case['title'],'description':case['deck'],'url':b.canonical(path),'mainEntityOfPage':{'@type':'WebPage','@id':b.canonical(path)},'articleSection':'Internet mystery analysis','inLanguage':lang,'datePublished':case['published'],'dateModified':case['updated'],'wordCount':b.case_words(case),'image':b.BASE+b.SOCIAL[path],'citation':[s['url'] for s in case['sources']], 'about':{'@type':'CreativeWork','name':v['title'],'url':'https://www.youtube.com/watch?v='+v['id'],'publisher':{'@type':v.get('publisherType','Person'),'name':v['creator'],'url':v['creatorUrl']}},'author':{'@type':'Organization','name':'Dark Echo Editorial','url':b.canonical('about.html')},'publisher':{'@type':'Organization','name':'Dark Echo','url':b.BASE}}
        if has_other:
            schema['translationOfWork' if lang == 'ar' else 'workTranslation'] = {'@type':'Article','url':b.canonical(self.path(original,other_lang)),'inLanguage':other_lang}
        b.write_page(path,case['title']+' | Dark Echo',case['deck'],body,active='mysteries',schema=schema,article=True,modified=case['updated'],lang=lang,alternates=alternates)

    def guide_cards(self):
        b = self.b
        return '<div class="guide-grid">' + ''.join(f'<article class="guide-card"><a href="{b.link("guides/"+g["slug"]+".html")}" aria-label="Read {b.e(g["title"])}"><img src="{b.link(b.SOCIAL["guides/"+g["slug"]+".html"])}" width="1200" height="630" loading="lazy" decoding="async" alt=""></a><div class="card-body"><p class="label">{b.e(g["category"])}</p><h2><a href="{b.link("guides/"+g["slug"]+".html")}">{b.e(g["title"])}</a></h2><p>{b.e(g["deck"])}</p><a href="{b.link("guides/"+g["slug"]+".html")}">Read the guide<span class="sr-only">: {b.e(g["title"])}</span></a></div></article>' for g in self.guides) + '</div>'

    def render_guides(self):
        b = self.b
        body = '<div class="container"><header class="page-intro"><p class="eyebrow">The field guides</p><h1>Get closer to the mystery.</h1><p>Understand the formats, follow a fictional clue trail, and check what a viral video actually establishes. Start with a question; leave with a method you can use.</p></header>' + self.guide_cards() + '<section class="section prose"><h2>Try the method</h2><p>Our <a href="' + b.link('mysteries.html') + '">mystery files</a> put these questions into practice. For a short challenge with an explanation after every answer, try <a href="' + b.link('quiz.html') + '">Fact or Fiction?</a>.</p></section></div>'
        b.write_page('guides.html','Internet Horror Field Guides | Analog Horror, ARGs & Video Sources','Learn how analog horror and ARGs work, and use a practical method for checking the source of a viral video.',body,active='guides')
        for guide in self.guides:
            path = 'guides/' + guide['slug'] + '.html'
            words = sum(len(p.split()) for s in guide['sections'] for p in s['paragraphs'])
            body = f'<article class="reading-layout"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{b.link()}">Home</a><span aria-hidden="true">/</span><a href="{b.link("guides.html")}">Field guides</a></nav><header><p class="eyebrow">{b.e(guide["category"])}</p><h1 class="article-title">{b.e(guide["title"])}</h1><p class="article-deck">{b.e(guide["deck"])}</p><p class="article-meta"><span>By Dark Echo Editorial</span><span>Published {self.time(guide["published"])}</span><span>About {max(1,ceil(words/200))} min read</span></p>{b.share_tools(path,guide["title"])}</header><aside class="case-verdict"><h2>The short answer</h2><p>{b.e(guide["answer"])}</p></aside><nav class="story-contents" aria-label="Guide contents"><h2>In this guide</h2><ol>'
            body += ''.join(f'<li><a href="#{b.e(s["id"])}">{b.e(s["title"])}</a></li>' for s in guide['sections']) + '</ol></nav><div class="prose">'
            for section in guide['sections']:
                body += f'<section id="{b.e(section["id"])}"><h2>{b.e(section["title"])}</h2>' + ''.join('<p>'+b.e(p)+'</p>' for p in section['paragraphs'])
                if section.get('sources'):
                    body += '<p class="case-citations">Sources: ' + self.citations(guide,section['sources']) + '</p>'
                body += '</section>'
            body += f'</div><aside class="practice-box"><h2>Try this on your next video</h2><p>{b.e(guide["practice"])}</p></aside>' + self.source_list(guide)
            body += '<section class="related-box"><h2>Put it into practice</h2><ul>' + ''.join(f'<li><a href="{b.link(self.path(case))}">{b.e(case["title"])}</a></li>' for case in b.MYSTERIES if case['slug'] in guide['related']) + f'<li><a href="{b.link("quiz.html")}">Take the five-question evidence quiz</a></li></ul></section></article>'
            schema = {'@context':'https://schema.org','@type':'Article','headline':guide['title'],'description':guide['deck'],'url':b.canonical(path),'mainEntityOfPage':b.canonical(path),'articleSection':'Internet horror field guide','inLanguage':'en','datePublished':guide['published'],'dateModified':guide['updated'],'wordCount':words,'image':b.BASE+b.SOCIAL[path],'citation':[s['url'] for s in guide['sources']],'author':{'@type':'Organization','name':'Dark Echo Editorial','url':b.canonical('about.html')},'publisher':{'@type':'Organization','name':'Dark Echo','url':b.BASE}}
            b.write_page(path,guide['title']+' | Dark Echo',guide['deck'],body,active='guides',schema=schema,article=True,modified=guide['updated'])

    def render_ar_home(self):
        b = self.b
        body = '<div class="container"><header class="page-intro"><p class="eyebrow">دارك إيكو بالعربية</p><h1>الغموض يستحق نظرة أقرب.</h1><p>فيديوهات غريبة، ومصادر منشورة، وأسئلة تستحق التحقق. اقرأ ثلاث قضايا من غموض الإنترنت بالعربية، مع فصل القصة الخيالية عن الوقائع والتفسير.</p><div class="actions"><a class="button button-primary" href="#files">اختر ملفًا</a><a class="button" href="'+b.link('ar/quiz.html')+'">اختبر نفسك: حقيقة أم تمثيل؟</a><a class="button" href="'+b.link('mysteries.html')+'" lang="en" hreflang="en">English files</a></div></header><section id="files" aria-labelledby="ar-files"><h2 id="ar-files">ملفات الغموض</h2><div class="case-list">'
        body += ''.join(self.case_card(case,'ar') for case in b.MYSTERIES if case['slug'] in self.arabic)
        body += '</div></section><section class="section prose"><h2>كيف نقرأ الفيديو الغامض؟</h2><p>نبدأ بالناشر والتاريخ والمصدر، ثم نفصل ما يثبته السجل عما نقرأه في الرموز. لا تكفي جودة التصوير المنخفضة أو عبارة «من الدارك ويب» لإثبات أصل فيديو. تتضمن الملفات روابط النسخ الأصلية ومصادر التحليل.</p><p>الأدلة التعليمية الإضافية متاحة الآن <a href="'+b.link('guides.html')+'" lang="en" hreflang="en">بالإنجليزية</a>. يمكنك أيضًا تجربة <a href="'+b.link('ar/quiz.html')+'">الاختبار العربي</a> وقراءة تفسير كل إجابة.</p></section></div>'
        b.write_page('ar/index.html','دارك إيكو | ملفات غموض الإنترنت بالعربية','اقرأ ملفات Backrooms و11B-X-1371 وThis House Has People in It بالعربية، مع مصادر موثقة وتحليل واختبار تفاعلي.',body,active='mysteries',lang='ar',alternates={'en':'mysteries.html','ar':'ar/index.html'},schema={'@context':'https://schema.org','@type':'CollectionPage','name':'دارك إيكو بالعربية','url':b.canonical('ar/index.html'),'inLanguage':'ar','mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'name':self.localized(c,'ar')['title'],'url':b.canonical(self.path(c,'ar'))} for i,c in enumerate([c for c in b.MYSTERIES if c['slug'] in self.arabic],1)]}})

    def render_quiz(self, lang):
        b = self.b; ar = lang == 'ar'; page = ('ar/' if ar else '') + 'quiz.html'
        title = 'حقيقة أم تمثيل؟' if ar else 'Fact or Fiction?'
        deck = 'خمسة ادعاءات عن فيديوهات غامضة. هل تدعمها المصادر؟ اختر إجابتك، ثم اقرأ التفسير والدليل.' if ar else 'Five claims about unsettling videos. Decide what the sources support, then check the explanation and evidence.'
        labels = ['تدعمه المصادر','لا تدعمه المصادر'] if ar else ['Supported by the sources','Not supported by the sources']
        body = f'<article class="reading-layout quiz-layout"><header><p class="eyebrow">{"اختبار الأدلة" if ar else "The evidence challenge"}</p><h1 class="article-title">{title}</h1><p class="article-deck">{deck}</p><p>{"يختبر هذا التحدي قراءة الادعاءات والمصادر، ولا يكشف حقيقة فيديو تلقائيًا. الإجابات تبقى في هذه الصفحة وتُمسح عند إعادة تحميلها." if ar else "This tests how you read claims and sources; it is not an automatic video-authenticity detector. Answers stay on this page and reset when you reload."}</p>{b.share_tools(page,title,lang)}</header><section data-quiz data-lang="{lang}" aria-label="{title}"><div class="quiz-progress" data-quiz-controls hidden><p data-quiz-progress role="status" aria-live="polite"></p><progress max="5" value="0" aria-label="{"عدد الأسئلة المجاب عنها" if ar else "Questions answered"}"></progress></div><div data-quiz-questions>'
        for i, question in enumerate(self.quiz['questions']):
            q = question[lang]; source = next(c for c in b.MYSTERIES if c['slug'] == question['case'])
            href = b.link(self.path(source,lang)) + '#' + question['section']
            supported = labels[0] if question['answer'] else labels[1]
            source_label = 'اقرأ الملف والمصادر' if ar else 'Read the case and sources'
            body += f'<fieldset class="quiz-question" data-quiz-question data-answer="{str(question["answer"]).lower()}" data-question-id="{b.e(question["id"])}"><legend><span class="quiz-question-number">{"السؤال" if ar else "Question"} {i+1}</span>{b.e(q["claim"])}</legend><div class="quiz-options">'
            for value,label in [('true',labels[0]),('false',labels[1])]:
                body += f'<label><input type="radio" name="question-{i}" value="{value}"><span>{label}</span></label>'
            body += f'</div><div class="quiz-feedback" data-quiz-feedback hidden role="status" aria-live="polite"><p data-quiz-answer-status></p><p data-quiz-explanation>{b.e(q["explanation"])}</p><a href="{href}" data-quiz-source>{source_label}</a></div><details class="quiz-answer-fallback" data-quiz-nojs><summary>{"اقرأ الإجابة وتفسيرها" if ar else "Read the answer and explanation"}</summary><p><strong>{supported}.</strong> {b.e(q["explanation"])}</p><a href="{href}">{source_label}</a></details></fieldset>'
        body += '</div><div class="quiz-actions" data-quiz-controls hidden><button type="button" class="button button-primary" data-quiz-check>'+('تحقق من الإجابة' if ar else 'Check answer')+'</button><button type="button" class="button" data-quiz-next hidden>'+('السؤال التالي' if ar else 'Next question')+'</button></div><section class="quiz-result" data-quiz-result hidden aria-labelledby="quiz-result-title"><p class="eyebrow">'+('انتهى الاختبار' if ar else 'Your result')+'</p><h2 id="quiz-result-title" tabindex="-1">'+('ما الذي أثبتته الأدلة؟' if ar else 'What did the evidence support?')+'</h2><p class="quiz-score" data-quiz-score dir="ltr"></p><p data-quiz-result-text></p><ol class="quiz-review" data-quiz-review></ol><div class="actions"><button class="button button-primary" type="button" data-quiz-share>'+('شارك نتيجتك' if ar else 'Share your result')+'</button><button class="button" type="button" data-quiz-restart>'+('ابدأ من جديد' if ar else 'Try again')+'</button></div><div class="copy-fallback" data-quiz-share-fallback hidden><label>'+('نص المشاركة' if ar else 'Result to share')+'<textarea readonly rows="3" data-quiz-share-text></textarea></label></div></section><noscript><p class="notice">'+('يمكنك قراءة الأسئلة وفتح تفسير كل إجابة دون JavaScript. النتيجة التفاعلية تتطلب تشغيل JavaScript.' if ar else 'You can read every question and open its answer without JavaScript. Enable JavaScript for the interactive score.')+'</p></noscript></section><section class="related-box"><h2>'+('تابع الاستكشاف' if ar else 'Keep investigating')+'</h2><p><a href="'+b.link('ar/index.html' if ar else 'mysteries.html')+'">'+('ملفات الغموض بالعربية' if ar else 'Explore the mystery files')+'</a></p><p><a href="'+b.link('quiz.html' if ar else 'ar/quiz.html')+'" lang="'+('en' if ar else 'ar')+'" hreflang="'+('en' if ar else 'ar')+'">'+('Take the quiz in English' if ar else 'جرّب الاختبار بالعربية')+'</a></p></section></article>'
        b.write_page(page,title+' | Dark Echo',deck,body,active='quiz',lang=lang,alternates={'en':'quiz.html','ar':'ar/quiz.html'},scripts=['assets/quiz-tools.js','assets/quiz.js'],schema={'@context':'https://schema.org','@type':'WebPage','name':title,'description':deck,'url':b.canonical(page),'inLanguage':lang,'dateModified':self.quiz['updated']},modified=self.quiz['updated'])

    def teaser(self):
        b = self.b
        return '<section class="section growth-teaser"><div class="container"><div class="section-heading"><div><h2>Go beyond the first impression.</h2><p>Learn the format, question the claim, or follow the story in Arabic.</p></div></div><div class="discovery-grid"><article><p class="label">The field guides</p><h3>Understand the signal.</h3><p>Analog horror, fictional clue trails, and a practical way to check a viral video.</p><a class="button" href="'+b.link('guides.html')+'">Explore the guides</a></article><article><p class="label">Five-question challenge</p><h3>Fact or Fiction?</h3><p>Decide what the records support. Every answer comes with an explanation and a source.</p><a class="button" href="'+b.link('quiz.html')+'">Take the challenge</a></article><article lang="ar" dir="rtl"><p class="label">دارك إيكو بالعربية</p><h3>الغموض، بلغتك.</h3><p>اقرأ ملفات الفيديوهات الغامضة بالعربية، مع الأدلة والمصادر والتفسير.</p><a class="button" href="'+b.link('ar/index.html')+'">اقرأ الملفات العربية</a></article></div></div></section>'

    def render(self):
        self.render_guides()
        self.render_ar_home()
        self.render_quiz('en')
        self.render_quiz('ar')
