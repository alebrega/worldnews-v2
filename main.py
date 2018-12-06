from flask import Flask
from flask import flash, request, jsonify, abort, render_template, session, redirect, url_for
from urllib.request import urlopen, URLError, urlparse
from article import save_article
from models import get_engine, articles
from sqlalchemy.sql import table, column, select
import os

contento = Flask(__name__)

engine = get_engine()
conn = engine.connect()


def valid_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme)


@contento.route('/api/article', methods=['POST'])
def create_article():
    content = request.json
    url = content['url']
    languange_to_translate = content['lang']
    keywords_matching = content['keywords_matching']
    old_days = content['old_days']
    t = table('articles', column('url'))
    s = select([t]).where(t.c.url == url)
    r = conn.execute(s)
    results = r.fetchall()
    if (len(results) > 0):
        return jsonify({'url': url, 'success': False, 'error': 'URL was used before'})

    if valid_url(url):
        response = save_article(
            url, languange_to_translate, keywords_matching, old_days)
        if response['success']:
            return jsonify({'url': url, 'success': response['success'], 'message': response['message']})
        else:
            return jsonify({'url': url, 'success': response['success'], 'message': response['error']})
    else:
        return jsonify({'url': url, 'success': False, 'error': 'URL is no valid'})

    abort(404)


@contento.route('/', methods=['GET', 'POST'])
def index_admin():
    if request.method == 'POST':
        url = request.form['url']
        old_days = request.form['old_days']
        languange_to_translate = request.form['language']
        keywords_matching = 0
        t = table('articles', column('url'))
        s = select([t]).where(t.c.url == url)
        r = conn.execute(s)
        results = r.fetchall()
        if (len(results) > 0):
            flash('URL was used before')
            return render_template("admin/index.html")

        if valid_url(url):
            response = save_article(
                url, languange_to_translate, keywords_matching, old_days)
            if response['success']:
                flash(response['message'])
                return render_template("admin/index.html")
            else:
                flash(response['error'])
                return render_template("admin/index.html")
        else:
            flash('URL is no valid')
            return render_template("admin/index.html")
        abort(404)
    return render_template("admin/index.html")


if __name__ == '__main__':
    contento.config.from_mapping(
        SECRET_KEY=os.environ['SECRET']
    )
    contento.run(host='0.0.0.0', debug=os.environ['DEBUG'])
