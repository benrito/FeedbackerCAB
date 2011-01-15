from cab.core.controllers import *

urls = [
	(r"/", IndexController),
	(r"/remote", RemoteController),
	(r"/graph", GraphController),
	(r"/subscribe", SubscribeController),
	(r"/notify", NotifyController),	
]
