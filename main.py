#!/usr/bin/env python

import webapp2
from google.appengine.ext import db

import jinja2

import os

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(templates_dir), autoescape = True)

class Art(db.Model):
    title = db.StringProperty(Required=True)
    art = db.TextProperty(Required=True)

class BaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))
   

class AsciiChanHandler(BaseHandler):
    def get(self):
        self.render("main-page.html")
    
    def post(self):
        self.title = self.request.get('title')
        self.art_text = self.request.get('art')
        
        if title and art:
            art = Art(title = self.title, art = self.art_text)
            art.put()
            self.redirect('/')
        else:
            self.error = "we need both a title and some art work"
            self.render("main-page.html", title = self.title, art=self.art_text, error = self.error)

app = webapp2.WSGIApplication([
    ('/', AsciiChanHandler)
], debug=True)
