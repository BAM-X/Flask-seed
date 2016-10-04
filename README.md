# Shortener: User-Agent aware URL shortening

Shortener takes a URL and shortens it.  It optionally allows for different urls to be redirected to based on the User-Agent of the request.

To run:

`pip install -r requirements.txt`

`python app/app.py`

I suggest you run this in a virtualenv  - see [VirtualEnv docs](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

Run tests with
 `cd app`
 `python -m unittest discover`

##URL API
### shorten
 To request a shortened version of a URL send a json post to /shorten with the following payload:
 ```javascript
    
    {url: 'url.to/shorten'}
     
    {url:'url.to/shorten',vanity:'my-vanity-url'}
 
    {urls:[{url: 'url.to/shorten', ua:'desktop'},
    {url: 'm.url.to/shorten', ua:'mobile'}, 
    {url: 't.url.to/shorten', ua:'tablet'}
    {url:'ie.url.to/shorten', ua:"MSIE ([0-9]{1,}[.0-9]{0,})"}],     vanity: 'my-vanity-url'}
```

 The response will be of the format:
 
 ```javascript
 {status:'SUCCESS', shorturl:'shorturl'}
 ```
 Note that the short url can be used by going to `http://<hostname>/s/shorturl`
 
 More formally  - the request must consist of a json object containing either a `url` or `urls` field.  A `url` field must contain exactly one url in string format.
 A `urls` field must consist of an array containing one or more elements, each of which must contain a `url` field and optionally a `ua` field specifying the user agents that should match that url.
 User agent matching occurs in the following manner:
  - if a user agent matches one or more regular expressions provided in a `ua` field, the url that is redirected to is the first such match.
  - if a user agent matches one of the special values `tablet` `mobile` or `desktop` and the matching value has a url, it's redirected to the first such match
  - if there is a ua of `default` and the user agent does not match any other value, it is redirected to the first such value
  - Otherwise, the first url provided is used.
Note that multiple ua fields can have the same url field.

a `vanity` field can optionally be provided, in which case the shortened url will use that value unless it is already being used. 
If a `vanity` field is set, but is not available, the request will fail.

### analyze
   To get data about a particular shortened url, post to /analyze with the following payload:
```javascript
            {detail: 'summary|ua|full'} 
```
     
   The response will contain:
```javascript
        //summary
        {urls: [{url:'short.url', create_time:'2016-09-23 00:00:34', redirects: 102} ] }
     
        //UA
        {urls: [{url:'short.url', create_time:'2016-09-23 00:00:34', redirects: [{'ua_pattern':'tablet', redirects:102}, {ua_pattern:'mobile', redirects:100}]} ] }
        
        //full
        {urls: [{url:'short.url', create_time:'2016-09-23 00:00:34', redirects: [ 
        {redirected_url: 'long.url', redirected_at:'2016-10-01 00:00:00', client_ip:'192.168.2.2', client_ua:'Mozilla ....'}
        ] }
     
```
     
##internals
 
 short urls are stored as a shortened url, creation timestamp, a user-agent string, and a long url.
 each redirect event is stored as a client ip, timestamp, user-agent, requested url and redirected url
 
 
## notes on scaling
  - database is currently sqlite, and is probably the bottleneck in processing
  - improvements could include using a mongodb or other nosql store for storing the request event stream
  - ua matching on regex can also be done in the database if supported (e.g. mongodb)
  - db can be sharded on url fairly easily