#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class blog_handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class blog_posts(db.Model):
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    perma = db.TextProperty(required=False)

class Blog_Page(blog_handler):
    def render_main_blog(self, title="", post="", perma =""):
        all_posts = db.GqlQuery("SELECT * FROM blog_posts ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, post=post, all_posts=all_posts, perma=perma)

    def get(self, id=""):
        self.render_main_blog()

        # if title and post:
        #     a = blog_posts(title = title, post = post)
        #     a.put()
        #
        #     self.redirect("/blog")
        # else:
        #     error= "This entry is not complete"

class newpost(blog_handler):
    def render_submission_form(self, title="", post="", error=""):
        self.render("newpost.html", title=title, post=post, error=error)

    def get(self):
        self.render_submission_form()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            a = blog_posts(title=title, post=post)
            a.put()
            id = a.key().id()
            perma = "/blog/" + str(id)
            a.perma = perma
            a.put()
            self.redirect(perma)

        else:
            error = "This entry is not complete"
            self.render_submission_form(title, post, error)

class MainHandler(blog_handler):
    def get(self):
        template_values = {}
        template = jinja_env.get_template('base.html')
        self.response.write(template.render(template_values))

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        mypost = blog_posts.get_by_id(int(id), parent = None)
        final_post = ""
        final_post += "<h1>"+ mypost.title + "</h1><br>" + mypost.post 
        self.response.write(final_post)
        # self.redirect(blog_posts)
        #
        # for p in mypost:
        #     self.response.write(p)
        #


app = webapp2.WSGIApplication([
    ('/', MainHandler,),
    ('/newpost', newpost),
    ('/blog', Blog_Page),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)

], debug=True)
