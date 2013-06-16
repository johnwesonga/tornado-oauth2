import tornado.web

import hashlib

class Gravatar(tornado.web.UIModule):
	def render(self, email, size=40, image_type='jpg', show_comments=False):
		email_hash = hashlib.md5(email).hexdigest()
		#self.render_string("module-gravatar.html", show_comments=show_comments)
		return "http://gravatar.com/avatar/{0}?s={1}.{2}".format(email_hash, size, image_type)
		