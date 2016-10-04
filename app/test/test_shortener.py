import json
from test import AppTestCase


class TestShortener(AppTestCase):
    def test_shorten_single(self):
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], "SUCCESS")

    def test_shorten_multiple(self):
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com/',
                                                                 ua='mobile')))),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['status'], "SUCCESS")
        pass

    def test_shorten_vanity_single(self):
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com', vanity="big-g")),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.data)
        self.assertEqual(resp['status'], "SUCCESS")
        self.assertEqual(resp['url'], 'big-g')
        pass

    def test_shorten_vanity_multiple(self):
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com/',
                                                                 ua='mobile')),
                                                      vanity="big-g")),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.data)
        self.assertEqual(resp['status'], "SUCCESS")
        self.assertEqual(resp['url'], 'big-g')

        pass

    def test_shorten_vanity_fail(self):
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com', vanity="big-g")),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com', vanity="big-g")),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.data)
        self.assertEqual(resp['status'], "FAILED")
        self.assertEqual(resp['message'], "Vanity URL already exists")
        pass


class TestAnalyzer(AppTestCase):
    def test_analyze_summary(self):
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']
        self.app.get('/s/' + url1)
        self.app.get('/s/' + url1)
        self.app.get('/s/' + url1)
        self.app.get('/s/' + url1)
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url2 = resp['url']
        self.app.get('/s/' + url2)
        self.app.get('/s/' + url2)
        self.app.get('/s/' + url2)
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url3 = resp['url']
        self.app.get('/s/' + url3)
        self.app.get('/s/' + url3)
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url4 = resp['url']
        self.app.get('/s/' + url4)

        response = self.app.post('/analyze', data=json.dumps(dict(detail='summary')), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.data)
        mapped = dict(zip((x['short_url'] for x in resp['urls']), (x['redirects'] for x in resp['urls'])))
        self.assertEqual(mapped[url1], 4)
        self.assertEqual(mapped[url2], 3)
        self.assertEqual(mapped[url3], 2)
        self.assertEqual(mapped[url4], 1)

    def test_analyze_ua(self):
        mobile_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/43.0.2357.65 Mobile Safari/537.36'}
        tablet_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0'}
        desktop_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']
        self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.app.get('/s/' + url1, environ_base=tablet_ua)
        self.app.get('/s/' + url1, environ_base=desktop_ua)
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com/',
                                                                 ua='mobile')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url2 = resp['url']
        self.app.get('/s/' + url2, environ_base=mobile_ua)
        self.app.get('/s/' + url2, environ_base=tablet_ua)
        self.app.get('/s/' + url2)
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com/',
                                                                 ua='mobile')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url3 = resp['url']
        self.app.get('/s/' + url3, environ_base=mobile_ua)
        self.app.get('/s/' + url3, environ_base=tablet_ua)
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com/',
                                                                 ua='mobile')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url4 = resp['url']
        self.app.get('/s/' + url4, environ_base=mobile_ua)

        response = self.app.post('/analyze', data=json.dumps(dict(detail='ua')), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.data)
        mapped = dict(zip((x['short_url'] for x in resp['urls']), (x['redirects'] for x in resp['urls'])))

        self.assertEqual(mapped[url1], [{u'redirects': 4, u'ua_pattern': u'.'}])
        self.assertEqual(mapped[url2],
                         [{u'redirects': 2, u'ua_pattern': u'desktop'}, {u'redirects': 1, u'ua_pattern': u'mobile'}])
        self.assertEqual(mapped[url3],
                         [{u'redirects': 1, u'ua_pattern': u'desktop'}, {u'redirects': 1, u'ua_pattern': u'mobile'}])
        self.assertEqual(mapped[url4], [{u'redirects': 1, u'ua_pattern': u'mobile'}])

    def test_analyze_full(self):
        mobile_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/43.0.2357.65 Mobile Safari/537.36'}
        tablet_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0'}
        desktop_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']
        self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.app.get('/s/' + url1, environ_base=tablet_ua)
        self.app.get('/s/' + url1, environ_base=desktop_ua)
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com/',
                                                                 ua='mobile')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url2 = resp['url']
        self.app.get('/s/' + url2, environ_base=mobile_ua)
        self.app.get('/s/' + url2, environ_base=tablet_ua)
        self.app.get('/s/' + url2)
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com/',
                                                                 ua='mobile')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url3 = resp['url']
        self.app.get('/s/' + url3, environ_base=mobile_ua)
        self.app.get('/s/' + url3, environ_base=tablet_ua)
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com/',
                                                                 ua='mobile')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url4 = resp['url']
        self.app.get('/s/' + url4, environ_base=mobile_ua)

        response = self.app.post('/analyze', data=json.dumps(dict(detail='full')), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.data)

        mapped = dict(zip((x['short_url'] for x in resp['urls']), (len(x['redirects']) for x in resp['urls'])))
        self.assertEqual(mapped[url1], 4)
        self.assertEqual(mapped[url2], 3)
        self.assertEqual(mapped[url3], 2)
        self.assertEqual(mapped[url4], 1)


class TestRedirect(AppTestCase):
    def test_redirect_default(self):
        mobile_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/43.0.2357.65 Mobile Safari/537.36'}
        tablet_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0'}
        desktop_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']

        response = self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        response = self.app.get('/s/' + url1, environ_base=tablet_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        response = self.app.get('/s/' + url1, environ_base=desktop_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        pass

    def test_redirect_ua_match(self):
        mobile_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/43.0.2357.65 Mobile Safari/537.36'}
        tablet_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0'}
        desktop_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://windows.google.com', ua='Windows'),
                                                            dict(url='https://linux.google.com',
                                                                 ua='Linux')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']

        response = self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://linux.google.com')

        response = self.app.get('/s/' + url1, environ_base=tablet_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://windows.google.com')

        response = self.app.get('/s/' + url1, environ_base=desktop_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://windows.google.com')

    def test_redirect_ua_no_match(self):
        mobile_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/43.0.2357.65 Mobile Safari/537.36'}
        tablet_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0'}
        desktop_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='Android'),
                                                            dict(url='https://other.google.com',
                                                                 ua='Mac')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']

        response = self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        response = self.app.get('/s/' + url1, environ_base=tablet_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        response = self.app.get('/s/' + url1, environ_base=desktop_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

    def test_redirect_mobile(self):
        mobile_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/43.0.2357.65 Mobile Safari/537.36'}
        tablet_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0'}
        desktop_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        response = self.app.post('/shorten', data=json.dumps(dict(url='https://www.google.com')),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']

        response = self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        response = self.app.get('/s/' + url1, environ_base=tablet_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        response = self.app.get('/s/' + url1, environ_base=desktop_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

    def test_redirect_tablet(self):
        mobile_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/43.0.2357.65 Mobile Safari/537.36'}
        tablet_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0'}
        desktop_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com',
                                                                 ua='mobile')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']

        response = self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://m.google.com')

        response = self.app.get('/s/' + url1, environ_base=tablet_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        response = self.app.get('/s/' + url1, environ_base=desktop_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

    def test_redirect_desktop(self):
        mobile_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/43.0.2357.65 Mobile Safari/537.36'}
        tablet_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0'}
        desktop_ua = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        response = self.app.post('/shorten',
                                 data=json.dumps(dict(urls=(dict(url='https://www.google.com', ua='desktop'),
                                                            dict(url='https://m.google.com',
                                                                 ua='tablet')))),
                                 content_type='application/json')
        resp = json.loads(response.data)
        url1 = resp['url']

        response = self.app.get('/s/' + url1, environ_base=mobile_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

        response = self.app.get('/s/' + url1, environ_base=tablet_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://m.google.com')

        response = self.app.get('/s/' + url1, environ_base=desktop_ua)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')
