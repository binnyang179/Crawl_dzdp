# import http.cookiejar
# import urllib.request
#
# cookie = http.cookiejar.CookieJar()
# handler = urllib.request.HTTPCookieProcessor(cookie)
# opener = urllib.request.build_opener(handler)
# response = opener.open('http://bing.com')
# for item in cookie:
#     print(item.name + "=" + item.value)
#
# from bs4 import BeautifulSoup
# soup = BeautifulSoup('<p>Hello</p>', 'lxml')
# print(soup.p.string)

#
# import tesserocr
# from PIL import Image
# image = Image.open('image/image.png')
# print(tesserocr.image_to_text(image))
# print(tesserocr.file_to_text('image/image.png'))

# from flask import Flask
#
# app = Flask(__name__)
#
#
# @app.route("/")
# def hello():
#     return "Hello World!"
#
#
# if __name__ == "__main__":
#     app.run()
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()