#!/usr/bin/env python

import webapp2
from google.appengine.ext import db
import urllib2
from xml.dom import minidom
import jinja2

import os

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(templates_dir), autoescape = True)
def get_location(ip):
    ip = '4.2.2.2'
    url = 'http://api.hostip.info/?ip=%s'
    if ip:
        contnet = None
        try:
            content = urllib2.urlopen(url % ip).read()
        except urllib2.URLError:
            return        
        if contnet:
            d = minidom.parseStrin(content)
            coords =d.getElementsByTageName('gml:coordinates')
            lon, lat = coords[0].childNodes[0].nodeValue.split(',')
            return lat, lon
            
class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now=True)
    location = db.GeoPtProperty()

class BaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))
   
GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"
def gmaps_url(points):
    temp = GMAPS_URL
    for p in points:
        temp += 'markers=%s,%s&' % (p.lat, p.lon)
    return temp[:len(temp) -1]
    
class AsciiChanHandler(BaseHandler):
    def get(self):
        self.arts = db.GqlQuery('select * from Art order by created desc')
        
        self.arts = list(self.arts)
        
        points = filter(None, (a.location for a in self.arts))
        
        image_url = None
        if points:
            image_url = gmaps_url(points)
        self.render("main-page.html", arts = self.arts, image_url = image_url)
    
    def post(self):
        self.title = self.request.get('title')
        self.art_text = self.request.get('art')
        
        if self.title and self.art_text:
            art = Art(title = self.title, art = self.art_text)
            loc = get_location(self.request.remote_addr)
            
            if loc:
                art.location = db.GeoPt(loc.lat, loc.lon)
            
            art.put()
            self.redirect('/')
        else:
            self.error = "we need both a title and some art work"
            self.render("main-page.html", title = self.title, art=self.art_text, error = self.error)

app = webapp2.WSGIApplication([
    ('/', AsciiChanHandler)
], debug=True)
