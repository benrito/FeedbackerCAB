try:
	import simplejson
except:
	import json as simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from cab import settings
from tornado.web import RequestHandler
import httplib
import traceback
import sys
from cab.core.util import *
from uuid import uuid4

class Controller(RequestHandler):
	WEB_HTML = "web/html"	
	vars = {}
	
	def __init__(self, application, request, **kwargs):
		super(Controller, self).__init__(application, request, **kwargs)
		self.vars = dict()
		for x in request.arguments:
			self.vars[x] = request.arguments[x][0]

	def getvar(self, var):
		return self.vars.get(var, "")

	def client_id(self):
		if "client_id" in self.cookies:
			client_id = self.cookies["client_id"].value
		else:
			client_id = str(uuid4())
			self.set_cookie("client_id", client_id)
		return client_id

	def get_error_html(self, status_code, **kwargs):
		vars = dict(kwargs)
		vars['code'] = status_code
		vars['message'] = httplib.responses[status_code]
		self._process_vars(vars)
		if settings.DEBUG:

			body = "ERROR:\n"
			body += "------\n"
			body += self.request.method + " " + self.request.uri + "\n\n"
			body += "Variables:\n"
			body += "--------------\n"
			for v in self.vars:
				val = self.vars[v]
				if v == "pwd" or v == "password":
					val = "********"
				body += v + "=" + str(val) + "\n"
			body += "\n"
			body += "COOKIES variables:\n"
			body += "------------------\n"
			for v in self.cookies:
				body += v + "=" + str(self.cookies[v]) + "\n"
			body += "\n"
			exc_info = sys.exc_info()
			body += "######################## Exception #############################"
			body += '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
			body += "################################################################"
			vars['body'] = body

			return loader.render_to_string("error_debug.html", vars)
		else:
			return loader.render_to_string("error.html", vars)

	def set_nocache(self):
		self.set_header("Pragma", "No-Cache")
		self.set_header("Cache-Control", "No-Cache, No-Store, Must-Revalidate")

	def _process_vars(self, vars):
		for x in settings.TEMPLATE_CONSTANTS:
			vars[x] = settings.TEMPLATE_CONSTANTS[x]
		vars["xsrf"] = self.xsrf_form_html()

	def render(self, content='', mimetype=None):
		if mimetype:
			self.set_header("Content-Type", mimetype)
		self.finish(content)
	
	def render_template(self, template, vars):
		self.render(self.render_template_to_string(template, vars))
	
	def render_template_to_string(self, template, vars):
		vars["request"] = self.request
		self._process_vars(vars)
		return loader.render_to_string(template, vars)
	
	def render_json(self, dict):
		out = simplejson.dumps(dict)
		self.render(out, mimetype="application/javascript")

	def render_json_success(self):
		self.render_json({'success': True})

	def render_json_failed(self):
		self.render_json({'success': False})
				
	def render_json_error(self, message):
		self.render_json({'success': False, 'error': message})

	def render_json_logged_out(self):
		self.render_json({'logged_in': False})

	def render_overlay(self, overlay_contents):
		dict = {'overlay':overlay_contents}
		self.render_json(dict)
