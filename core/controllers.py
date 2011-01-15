#!/usr/bin/env python
from cab.core.base import Controller
import tornado
import tornado.httpclient
from tornado.ioloop import IOLoop
from tornado.web import asynchronous
from datetime import datetime, timedelta
from time import time
from Queue import deque
from random import randint
from uuid import uuid4

# Define the class that will respond to the URL
class IndexController(Controller):
	def get(self):
		total_score = SubscribeController.total_score
		total_members = SubscribeController.active_count
		self.render_template("index.html", {"total_score": total_score, "total_members": total_members})

class RemoteController(Controller):
	def get(self):
		pass

class GraphController(Controller):
	def get(self):
		pass

class NotifyController(Controller):
	def post(self):
		score = int(self.vars['score'])
		if score == -1 or score == 0 or score == 1:
			client = SubscribeController.clients[self.client_id()]
			if score != client.score:
				SubscribeController.total_score -= client.score
				client.score = score
				SubscribeController.total_score += client.score
				SubscribeController.broadcast_state()
		self.render_json_success()

class SubscribeController(Controller):
	# static variables
	clients = dict()
	active_count = 0
	total_score = 0

	# instance variables
	time  = None
	TIMEOUT = 60
	INACTIVE_TIMEOUT = 10
	messages = None
	active = None
	destroyed = None
	score = 0
	id = None

	# called during the GET request
	@asynchronous
	def get(self):
		print "GET " + self.client_id()
		
		SubscribeController._prune()

		self.id = self.client_id()
		self.time = datetime.now()
		self.active = True
		self.destroyed = False
		self.messages = []
		
		# replace old controller with this one
		exists = self.id in SubscribeController.clients
		if exists:
			old = SubscribeController.clients[self.id]
			self.messages = old.messages
			self.score = old.score
			old.destroy()

		# update aggregate state
		SubscribeController.clients[self.id] = self
		SubscribeController.active_count += 1
		SubscribeController.total_score += self.score
		
		print "MEMBERS: " + str(SubscribeController.active_count)
		
		# broadcast if new
		if not exists:
			SubscribeController.broadcast_state()
	
	def on_connection_close(self):
		self.active = False
		IOLoop.instance().add_timeout(time() + SubscribeController.INACTIVE_TIMEOUT, self._check_stale)
		
	def _check_stale(self):
		if not self.destroyed:
			self.destroy()
			SubscribeController.broadcast_state()
	
	@classmethod
	def _prune(cls):
		for id in dict(SubscribeController.clients):
			client = SubscribeController.clients[id]
			if client.is_expired():
				client.notify({"timeout": 1})
	
	def is_expired(self):
		return self.active and ((datetime.now() - self.time) > timedelta(seconds=SubscribeController.TIMEOUT))

	@classmethod	
	def broadcast_state(cls):
		SubscribeController.broadcast({"members": SubscribeController.active_count, "score": SubscribeController.total_score})
		
	# broadcasts a message to all clients
	@classmethod
	def broadcast(cls, message):
		#print "broadcast " + str(message)
		for id in SubscribeController.clients:
			client = SubscribeController.clients[id]
			client.notify(message)

	# sends a message to this client
	def notify(self, message):
		#print self.client_id() + " -> " + str(message)
		self.messages.append(message)
		if self.active:
			self.active = False
			self.inactive_time = datetime.now()
			try:
				self.render_json({"messages": self.messages})
				self.messages = []
			except:
				# connection closed
				pass
	
	def destroy(self):
		if self.id in SubscribeController.clients:
			SubscribeController.total_score -= self.score
			SubscribeController.active_count -= 1
			del SubscribeController.clients[self.id]
			self.destroyed = True
