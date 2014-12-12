from os import path

from tornado.web import RequestHandler


class IndexController(RequestHandler):
    def get(self):
        tmpl_path = ''.join((path.dirname(path.abspath(__file__)), '/../templates/index.html'))
        self.render(tmpl_path)