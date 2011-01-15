import sys, os, traceback
from django.conf import settings as django_settings
import tornado.httpserver
import tornado.ioloop
from tornado.web import RequestHandler

# load settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django_settings._setup()

# import to path one directory up
path = os.path.abspath(__file__)
path = path[0:path.rfind("/")]
sys.path.append(path[0:path.rfind("/")])

# create the app
from cab import settings
from cab.urls import urls
app_settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "public"),
    "cookie_secret": "61oETzKXQAGaYdkA5gEmGEJjFugh7e5np2XdTP1o=/0/",
    "login_url": "/login",
    "xsrf_cookies": True,
}
application = tornado.web.Application(urls, **app_settings)

runserver = True
if len(sys.argv) > 1:
	runserver = False
	arg = sys.argv[1]
	if arg == "cron":
		try:
			exec("from cab.cron import " + sys.argv[2])
		except:
			exc_info = sys.exc_info()
			body = '######################## Exception #############################'
			body += '\\\\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
			body += '################################################################'
			print body
	elif arg == "daemon":
		runserver = True
		import daemon
		log = open('tornado.log', 'a+')
		ctx = daemon.DaemonContext(stdout=log, stderr=log,  working_directory='.')
		ctx.open()
	elif arg == "exec":
		exec(sys.argv[2])

if runserver:
	# Start the server
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(settings.SERVER_PORT)
	tornado.ioloop.IOLoop.instance().start()
