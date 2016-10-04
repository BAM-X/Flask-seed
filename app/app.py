import random
import re
import time
from itertools import ifilter, groupby

from flask import Flask, jsonify, request, redirect
from flask.views import MethodView
from sqlalchemy.sql import func

from database import init_db, db_session
from models import ShortUrl, RedirectEvent

app = Flask(__name__, static_url_path='/', static_folder='static')
counter = 0
last_s = time.time() / 60


def getMatcher(ua):
    """Get a matcher method for a given user agent"""
    # see https://developer.mozilla.org/en-US/docs/Web/HTTP/Browser_detection_using_the_user_agent
    def matcher(url):
        if url.user_agent == 'mobile':
            return re.search('Mobi', ua)
        elif url.user_agent == 'tablet':
            return re.search('Tablet', ua)
        elif url.user_agent == 'desktop':
            return not re.search("Mobi", ua) and not re.search("Tablet", ua)
        else:
            return re.search(url.user_agent, ua)

    return matcher


class RedirectView(MethodView):
    def get(self, short_url):
        """Redirect from a given short url to an appropriate expansion, or return failure if no such url exists"""
        ua = request.user_agent.string
        match = None
        urls = ShortUrl.query.filter(ShortUrl.short_url == short_url).order_by(ShortUrl.priority).all()
        if len(urls) == 0:
            return jsonify({'status':'FAILED', 'message': 'No such short path'})
        try:
            match = ifilter(getMatcher(ua), urls).next()
        except StopIteration:
            pass
        if match is None:
            match = urls[0]
        r = RedirectEvent(url_id=match.id, client_ip=request.remote_addr, client_ua=ua, client_requested_url=short_url,
                          client_redirected_url=match.long_url)
        db_session.add(r)
        db_session.commit()
        return redirect(match.long_url, code=302)


class URLAnalysisView(MethodView):

    def get(self, short_url):
        """Get all redirect events for a given short url"""
        events = (x.__repr__() for x in
                  RedirectEvent.query.filter(RedirectEvent.client_requested_url == short_url).all())
        return jsonify(value=events)


class AnalysisView(MethodView):
    def post(self):
        """Get global analytics on url usage.  See README.md for more details"""
        data = request.get_json(force=True)
        if data[u"detail"] == u"summary":
            urls = db_session.query(ShortUrl.short_url, func.min(ShortUrl.create_time).label('create_time'),
                                    func.count(RedirectEvent.id).label('redirects')) \
                .join(RedirectEvent,
                      ShortUrl.short_url == RedirectEvent.client_requested_url).group_by(ShortUrl.short_url).all()
            mapped = (dict(zip(['short_url', 'create_time', 'redirects'], u)) for u in urls)
            return jsonify(urls=list(mapped))
        elif data[u'detail'] == u'ua':
            urls = db_session.query(ShortUrl.id, ShortUrl.create_time, ShortUrl.short_url, ShortUrl.user_agent,
                                    func.count(RedirectEvent.id)).join(RedirectEvent,
                                                                       ShortUrl.id == RedirectEvent.url_id).group_by(
                ShortUrl.id).all()
            mapped = (dict(zip(['id', 'create_time', 'short_url', 'ua_pattern', 'redirects'], u)) for u in urls)
            values = []

            for k, v in groupby(mapped, (lambda x: {'create_time': x['create_time'], 'short_url': x['short_url']})):
                k['redirects'] = list({'ua_pattern': x['ua_pattern'], 'redirects': x['redirects']} for x in v)
                values.append(k)

            return jsonify(urls=values)
        elif data[u'detail'] == u'full':
            values = []
            urls = db_session.query(ShortUrl.create_time, ShortUrl.short_url, ShortUrl.user_agent,
                                    RedirectEvent.client_redirected_url,
                                    RedirectEvent.redirect_time,
                                    RedirectEvent.client_ip, RedirectEvent.client_ua) \
                .join(RedirectEvent, ShortUrl.id == RedirectEvent.url_id).all()
            mapped = (dict(zip(
                ['create_time', 'short_url', 'ua_pattern', 'redirected_url', 'redirected_at', 'client_ip', 'client_ua'],
                u)) for u in urls)
            for k, v in groupby(mapped, (lambda x: {'create_time': x['create_time'], 'short_url': x['short_url']})):
                k['redirects'] = list({'redirected_url': x['redirected_url'], 'redirected_at': x['redirected_at'],
                                       'client_ip': x['client_ip'], 'client_ua': x['client_ua']} for x in v)
                values.append(k)
            return jsonify(urls=values)

        else:
            return jsonify(urls=[])


class ShortenView(MethodView):

    def getURL(self):
        """Get a probably unique URL in the database. Uses current seconds, and a counter, plus 8 bits of randomness."""
        global counter, last_s
        url = ""
        while True:
            if (last_s == time.time() / 60):
                counter += 1
            else:
                last_s = time.time() / 60
                counter = 0

            url = ("%X" % ((last_s * 100) + counter)).join(random.choice('0123456789ABCDEF') for i in range(2))
            if ShortUrl.query.filter(ShortUrl.short_url == url).count() == 0:
                break
        return url

    def post(self):
        """Create a short url from a long url. See README.md for more details"""
        resp = {'status': 'FAILED'}
        data = request.get_json(force=True)
        vanity = None
        if u'vanity' in data.keys():
            vanity = data[u'vanity']

        url = ""
        if vanity is not None:
            exists = ShortUrl.query.filter(ShortUrl.short_url == vanity).count()
            if exists == 0:
                url = vanity
            else:
                resp['message'] = 'Vanity URL already exists'
                return jsonify(resp)
        else:
            url = self.getURL()

        if u'url' in data.keys():
            su = ShortUrl(short_url=url, user_agent='*', long_url=data[u'url'])
            db_session.add(su)
            db_session.commit()
            resp['url'] = url
            resp['status'] = 'SUCCESS'
        elif u'urls' in data.keys():
            for single in data['urls']:
                priority=0
                if single[u'ua'] in ['tablet','mobile','desktop']:
                    priority= 1

                su = ShortUrl(short_url=url, user_agent=single[u'ua'], long_url=single[u'url'], priority=priority)
                db_session.add(su)
            db_session.commit()
            resp['url'] = url
            resp['status'] = 'SUCCESS'

        else:
            resp['message'] = 'Exactly one of url or urls must be in request'
            return jsonify(resp)

        return jsonify(resp)


app.add_url_rule('/s/<string:short_url>', view_func=RedirectView.as_view('redirect'), methods=['GET', ])
app.add_url_rule('/a/<string:short_url>', view_func=URLAnalysisView.as_view('analyze_url'), methods=['GET', ])
app.add_url_rule('/analyze', view_func=AnalysisView.as_view('analysis'), methods=['POST', ])
app.add_url_rule('/shorten', view_func=ShortenView.as_view('shorten'), methods=['POST', ])


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    init_db()
    sr = ShortUrl(short_url="temp", user_agent="desktop", long_url="https://google.com/")
    db_session.add(sr)
    db_session.commit()
    app.run(debug=True, host='0.0.0.0')
