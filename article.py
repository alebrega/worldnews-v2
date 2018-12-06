import newspaper
from newspaper import Article, fulltext
import json
from wordpress import Wordpress
from datetime import datetime, timezone
import pytz
from keywords import is_similar_context, get_keywords_from_text, get_keywords_nltk
import spacy
from urllib.request import urlopen
from unplash import get_pics
from models import get_engine, articles
from sqlalchemy.sql import insert
from translate import translate_from_google


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def save_article(url, lang, keywords_matching, old_days):
    errors = []
    try:
        a = Article(url)
        a.download()
        a.parse()
        if a.publish_date is None:
            print("No publish date")
            try:
                with urlopen(url) as f:
                    conn = urlopen(url, timeout=30)
                    publish_date = conn.headers['last-modified']
                    if publish_date is None:
                        errors = {
                            'error': 'No publish date in headers', 'success': False}
                        return errors
                    print("Publish date from headers "+str(publish_date))
            except Exception as e:
                errors = {
                    'error': 'Cant get last modified date from headers' + str(e), 'success': False}
                return errors

        else:
            publish_date = utc_to_local(a.publish_date)
        now = datetime.now(timezone.utc)
        time_between_insertion = now - publish_date
        if time_between_insertion.days > int(old_days):
            errors = {'error': "The insertion date is older than " +
                      str(old_days)+" days", 'success': False}
            return errors
        text = translate_from_google(a.text, lang, 'text')
        if (len(text) < 500):
            errors = {'error': "Text is less than 400 chars", 'success': False}
            return errors
        try:
            matches = is_similar_context(text)
            # print(matches)
        except Exception as e:
            print('Problems with similar context' + str(e))

        if (len(matches) < int(keywords_matching)):
            errors = {'error': "The keywords matching are less " +
                      str(keywords_matching), 'success': False}
            return errors

        data = {}
        data['article'] = []
        title = translate_from_google(a.title, lang)
        a.nlp()
        keywords = [keyword for keyword in a.keywords if len(keyword) > 3]
        keywords = [translate_from_google(keyword, lang)
                    for keyword in keywords]
        keywords.extend(get_keywords_from_text(text))
        k = set(keywords)
        unique_keywords = list(k)

        summary = translate_from_google(a.summary, lang)
    except Exception as e:
        errors = {'error': 'Some errors trying to parse Article: ' +
                  str(e), 'success': False}
        return errors

    '''
    data['article'].append({
        'original_title': a.title,
        'title': title,
        'author':  a.authors,
        'original_text': a.text,
        'text':  text,
        'top_image': a.top_img,
        'keywords': unique_keywords,
        'summary': summary,
        'url': url,
        'date': publish_date.strftime("%B %d, %Y")
    })
    with open("articles.json", "a", encoding='utf8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)

    '''
    wp = Wordpress()
    query_for_images = (" ".join(get_keywords_nltk(text, 3)))
    images_src = get_pics(query_for_images, 1)
    if images_src is None:
        image_src = a.top_image
    else:
        image_src = images_src[0]

    if (wp.publish(title, text, image_src, unique_keywords)):
        engine = get_engine()
        conn = engine.connect()
        ins = insert(articles).values(
            original_title=a.title.encode('utf-8'),
            title=title,
            author=' '.join(a.authors),
            original_text=a.text.encode('utf-8'),
            text=text,
            top_image=a.top_img,
            keywords=', '.join(unique_keywords),
            summary=summary,
            url=url,
            date=publish_date)

        r = conn.execute(ins)
        response = {'message': "Publish OK", 'success': True}
        return response
    else:
        errors = {'error': "Error in publishing", 'success': False}
        return errors
    response = {'error': "Parse OK", 'success': False}
    return response
