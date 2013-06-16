#!/usr/bin/env python
# encoding: utf-8
"""
helloworld.py

Created by John Wesonga on 2011-12-12.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import tornado.auth
from tornado import httpclient
import tornado.escape
import tornado.httputil
import tornado.ioloop
import tornado.web
import tornado.httpserver 
import uimodules

import oauth2
import urllib
import logging
import os

from tornado.options import define, options


define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
		(r"/", MainHandler),
		(r"/auth/login", AuthHandler),
		(r"/auth/logout", LogoutHandler),
		(r"/profile", ProfileHandler),
		(r"/register", RegisterHandler),
		]

		settings = {"static_path": os.path.join(os.path.dirname(__file__), "static"),
		            "cookie_secret": "32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o",
		            "login_url": "/auth/login",
		            "google_permissions": "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar",
		            "debug": True,
		            "template_path": "templates/",
		            "xsrf_cookies": True,
		            "ui_modules": uimodules,
		            }
		

		tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		user_json = self.get_secure_cookie("user")
		if not user_json: return None
		return tornado.escape.json_decode(user_json)

class MainHandler(BaseHandler):
	def get(self):
		self.render('index.html')

class ProfileHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		logging.info(self.current_user)
		email = self.current_user["email"]
		self.render('profile.html', profile=self.current_user, email=email)

class AuthHandler(BaseHandler, oauth2.GoogleOAuth2Mixin):
	@tornado.web.asynchronous
	def get(self):
		#if self.get_argument("error", None) is not None: self.redirect("/")
		if self.get_argument("code", None):
			authorization_code = self.get_argument("code", None)
			self.get_authenticated_user(authorization_code,
				                        self.async_callback(self._on_auth))
			return
		self.authorize_redirect(self.settings['google_permissions'])

	def _on_auth(self, user_info):
		logging.info(user_info)
		self.set_secure_cookie("user", tornado.escape.json_encode(user_info))
		self.redirect('/profile')

class RegisterHandler(BaseHandler):
	def get(self):
		self.render('register.html')


class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_cookie("user")
		self.redirect("/")



def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
	main()

