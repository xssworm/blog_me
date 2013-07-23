#!/usr/bin/env python
#-*-encoding:utf8-*-

import os
import re
import tornado.httpserver
import torndb
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata

from tornado.options import define,options

define('port',default=9000,help='run on the given port',type=int)
define('mysql_host',default='127.0.0.1:3306',help='blog_me database host')
define('mysql_database',default='blog_me',help='Blog_me database name')
define('mysql_user',default='blog_me',help='Blog_me database username')
define('mysql_password',default='123456',help='Blog_me database password')


class Application(tornado.web.Application):
    def __init__(self):

        handlers=[
            (r'/',HomeHandler),
            (r'/home',HomeHandler),
            (r'/compose',ComposeHandler),
    ]

        settings=dict(
            blog_title=u'Blog Me',
            template_path=os.path.join(os.path.dirname(__file__),'templates'),
            static_path=os.path.join(os.path.dirname(__file__),'static'),
            cookie_secret='7c4a8d09ca3762af61e59520943dc26494f8941b',
            login_url='/auth/login',
            debug=True,
           )

        tornado.web.Application.__init__(self,handlers,**settings)
        self.db=torndb.Connection(
            host=options.mysql_host,
            database=options.mysql_database,
            user=options.mysql_user,
            password=options.mysql_password
        )

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_id=self.get_secure_cookie('blog_user')
        if not user_id:
            return None
        return self.db.get('select username from blog_user where id="%d"' % int(user_id)) 

class HomeHandler(BaseHandler):
    def get(self):
        blogs=self.db.query("select * from blogs order by update_time desc limit 5")
        #if not blogs:
        #    self.redirect('/compose')
        self.render('home.html',blogs=blogs)

class ComposeHandler(BaseHandler):
    def get(self):
        id=self.get_argument('id',None)
        blog=None
        if id:
            blog=self.db.get("select * from blogs where id=%d" % int(id))
        self.render('compose.html',blog=blog)

    def post(self):
        
    




if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server=tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
