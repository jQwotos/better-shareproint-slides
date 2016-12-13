import webapp2, jinja2, os

# Import requests with app engine adapter
import requests, requests_toolbelt.adapters.appengine
from bs4 import BeautifulSoup

import datetime, time

from google.appengine.ext import ndb

# Patch adapter
requests_toolbelt.adapters.appengine.monkeypatch()

# os.path.dirname(__file__) is the current location of the file
# os.path.join joins the current location with templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)
baseUrl = "https://woodroffehs.ocdsb.ca/Home%20Page%20Images/"
srcLocation = 'http://woodroffehs.ocdsb.ca/Home%20Page%20Images/Forms/AllItems.aspx'

garbageImages = [
    '',
]

acceptableFormats = [
    '.png',
    '.PNG',
    '.jpg',
    '.JPG'
]

for item in range(len(garbageImages)):
    garbageImages[item] = srcLocation + garbageImages[item]

def GetImages():
    images = []
    page = BeautifulSoup(requests.get(srcLocation).content)
    for image in page.findAll('img'):
        #images.append(image)
        try:
            alt = str(image['alt']).replace(" ", '%20')
            if alt not in garbageImages and any(acceptable in alt for acceptable in acceptableFormats):
                images.append(baseUrl + alt)
        except KeyError:
            pass
    return images


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# MainPage is a child of Handler, therefore it has all the functions and variables of Handler
class MainPage(Handler):
    '''
    def get(self):
        now = datetime.datetime.now()
        latestUpdateObj = Timeout.query().fetch()[0]
        latestUpdate = latestUpdateObj.updateTime

        images = Image.query().fetch()
        self.render('slideshow.html', images=images)
        if now >= now:
            latestUpdate.updateTime = now + datetime.timedelta(hours=2)
            ndb.delete_multi(Image.query().fetch())
            for image in GetImages():
                img = Image(link = image)
                img.put()
        #self.render('slideshow.html', images=GetImages())
    '''

    def get(self):
        now = datetime.datetime.now()

class GenerateInitial(Handler):
    def get(self):
        timeout = Timeout(updateTime = datetime.datetime.now())
        timeout.put()

        for image in GetImages():
            img = Image(link = image)
            img.put()

class EscapeCache(Handler):
    def get(self):
        self.render('slideshow.html', images=GetImages())

class Image(ndb.Model):
    link = ndb.StringProperty(required = True)
    uuid = ndb.StringProperty()
    updateTime = ndb.DateTimeProperty()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/init', GenerateInitial),
    ('/escape', EscapeCache)
], debug=True)
