from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from database import Base


class ShortUrl(Base):
    __tablename__ = 'short_url'
    id = Column(Integer, primary_key=True)
    short_url = Column(String(100))
    user_agent = Column(String(1000))
    long_url = Column(String(1000))
    create_time = Column(DateTime)
    priority = Column(Integer)

    def __init__(self, short_url=None, user_agent=None, long_url=None, create_time=datetime.now(), priority=0):
        self.short_url = short_url
        self.user_agent = user_agent
        self.long_url = long_url
        self.create_time = create_time
        self.priority = priority

    def __repr__(self):
        return '<short_url: %s - > %s for UA %s >' % (self.short_url, self.long_url, self.user_agent)


class RedirectEvent(Base):
    __tablename__ = 'redirects'
    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('short_url.id'), nullable=False)
    redirect_time = Column(DateTime)
    client_ip = Column(String(100))
    client_ua = Column(String(1000))
    client_requested_url = Column(String(1000))
    client_redirected_url = Column(String(100))

    def __init__(self, url_id=None, redirect_time=datetime.now(), client_ip=None, client_ua=None,
                 client_requested_url=None, client_redirected_url=None):
        self.url_id = url_id
        self.redirect_time = redirect_time
        self.client_ip = client_ip
        self.client_ua = client_ua
        self.client_redirected_url = client_redirected_url
        self.client_requested_url = client_requested_url

    def __repr__(self):
        return '<redirect event: %s -> %s for %s at %s> ' % (
            self.client_requested_url, self.client_redirected_url, self.client_ua, self.client_ip)
