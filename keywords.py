import spacy
from spacy import displacy
from wordpress import Wordpress
import nltk

import re


def is_similar_context(text):
    keywords = []
    keywords = get_keywords_from_text(text)
    is_str_keywords = not any(not isinstance(y, (str)) for y in keywords)
    if not is_str_keywords:
        print("is NOT string is_str_keywords")

    wp = Wordpress()
    keywords_from_our_site = wp.get_tags()
    is_str_keywords_from_our_site = not any(
        not isinstance(y, (str)) for y in keywords_from_our_site)
    if not is_str_keywords_from_our_site:
        print("is NOT string keywords_from_our_site")

    return list(set(keywords) & set(keywords_from_our_site))


def get_keywords_from_text(text):
    keywords = []
    keywords2 = []
    keywords = get_keywords_by_entities_from_text(text)
    keywords2 = get_keywords_by_tagging_from_text(text)
    keywords.extend(keywords2)
    return keywords


def get_keywords_by_entities_from_text(text):
    keywords = []
    try:
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(text)
        for ent in doc.ents:
            if (len(ent.text) > 3):
                if ((ent.label_ == 'GPE') or (ent.label_ == 'PERSON')
                    or (ent.label_ == 'NORP') or (ent.label_ == 'ORG') or (ent.label_ == 'PRODUCT')
                        or (ent.label_ == 'LOC') or (ent.label_ == 'FAC')):
                    keywords.append(ent.text)
        k = set(keywords)
        unique_keywords = list(k)
        return unique_keywords
    except Exception as e:
        print('Errors trying to get more keywords: ' + str(e))
        return keywords


def get_keywords_by_tagging_from_text(text):
    keywords = []
    try:
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(text)
        for token in doc:
            if ((token.pos_ == "PROPN") and (len(token.text) > 3)):
                try:
                    keywords.append(token.text)
                except Exception as e:
                    print('Errors getting keywords by tagging (' +
                          token.text+') with shapes: ' + str(e))
        k = set(keywords)
        unique_keywords = list(k)
        return unique_keywords
    except Exception as e:
        print('Errors trying to get more keywords by tagging: ' + str(e))
        return keywords


def get_keywords_nltk(text, num_keywords):
    keywords = []
    try:
        # Remove anything that isn't a 'word'
        only_words = re.sub("[^a-zA-Z]", " ", text)
        # Remove any words consisting of a single character
        no_single = re.sub(r'(?:^| )\w(?:$| )', ' ', only_words).strip()

        allWords = nltk.tokenize.word_tokenize(no_single)
        allWordDist = nltk.FreqDist(w.lower() for w in allWords)

        stopwords = nltk.corpus.stopwords.words('english')

        allWordExceptStopDist = nltk.FreqDist(
            w.lower() for w in allWords if w.lower() not in stopwords and len(w) > 3)
        keywords_tuple = allWordExceptStopDist.most_common(num_keywords)
        for keyword in keywords_tuple:
            keywords.append(keyword[0])
        return keywords
    except Exception as e:
        print('Errors trying to get more keywords by nltk: ' + str(e))
        return keywords
