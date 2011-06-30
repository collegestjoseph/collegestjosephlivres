# This Python file uses the following encoding: utf-8
import os
from google.appengine.ext.webapp import template
import cgi
import uuid
import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import mail

gDebug = False
gDefaultMessage = """
Bonjour,

J'aimerais acheter les livres mentionnés ci-dessous. Veuillez me contacter pour plus de détails.

Bien à vous,
%s

---

%s

---

Envoyé par http://livres-stjoseph.appspot.com/

"""

class BookSet(db.Model):
    owner = db.UserProperty()
    buyer = db.StringProperty()
    description = db.TextProperty()
    can_separate = db.BooleanProperty()
    grade = db.IntegerProperty()
    price = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    uuid = db.StringProperty()

class SearchPage(webapp.RequestHandler):
    def get(self):
        books_query = BookSet.all().order('-date')
        books = books_query.filter('buyer =', None)
        sec = 0
        if self.request.get('sec'):
            try:
                sec = int(self.request.get('sec'))
            except:
                sec = 0
            if sec > 5:
                sec = 5
            if sec < 1:
                sec = 0
            logging.info("sec requested: " + str(sec))
            if (sec > 0):
                books = books_query.filter('buyer =', None).filter('grade =', sec)

        path = os.path.join(os.path.dirname(__file__), 'search.phtml')

        if users.get_current_user():
            try:
              books[0]
            except:
              books = None
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'D&eacute;connexion'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Connexion'
            path = os.path.join(os.path.dirname(__file__), 'login.phtml')

        template_values = {
            'books': books,
            'sec': str(sec),
            'user': users.get_current_user(),
            'url': url,
            'url_linktext': url_linktext,
            'page_header': template.render('header.html', {
            				'user': users.get_current_user(),
                    'admin': users.is_current_user_admin(),
            				'url': url,
				            'url_linktext': url_linktext,
            		}),
            'page_footer': template.render('footer.html', {}),
            'debug': gDebug,
            }

        self.response.out.write(template.render(path, template_values))

class MyBooksPage(webapp.RequestHandler):
    def get(self):
        books_query = BookSet.all().order('-date')
        books = None
        user = None

        path = os.path.join(os.path.dirname(__file__), 'sell.phtml')

        if users.get_current_user():
            user = users.get_current_user()
            books = books_query.filter('owner =', user)
            try:
              books[0]
            except:
              books = None
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'D&eacute;connexion'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Connexion'
            path = os.path.join(os.path.dirname(__file__), 'login.phtml')

        template_values = {
            'books': books,
            'user': user,
            'admin': users.is_current_user_admin(),
            'url': url,
            'url_linktext': url_linktext,
            'user': user,
            'page_header': template.render('header.html', {
            				'user': users.get_current_user(),
                    'admin': users.is_current_user_admin(),
            				'url': url,
				            'url_linktext': url_linktext,
            		}),
            'page_footer': template.render('footer.html', {}),
            }

        self.response.out.write(template.render(path, template_values))

class ListsPage(webapp.RequestHandler):
    def get(self):

        path = os.path.join(os.path.dirname(__file__), 'lists.phtml')

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'D&eacute;connexion'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Connexion'
            path = os.path.join(os.path.dirname(__file__), 'login.phtml')

        template_values = {
            'user': users.get_current_user(),
            'admin': users.is_current_user_admin(),
            'url': url,
            'url_linktext': url_linktext,
            'page_header': template.render('header.html', {
                    'user': users.get_current_user(),
                    'admin': users.is_current_user_admin(),
                    'url': url,
                    'url_linktext': url_linktext,
                }),
            'page_footer': template.render('footer.html', {}),
            }

        self.response.out.write(template.render(path, template_values))

class MainPage(webapp.RequestHandler):
    def get(self):

        path = os.path.join(os.path.dirname(__file__), 'index.phtml')

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'D&eacute;connexion'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Connexion'
            path = os.path.join(os.path.dirname(__file__), 'login.phtml')

        template_values = {
            'user': users.get_current_user(),
            'admin': users.is_current_user_admin(),
            'url': url,
            'url_linktext': url_linktext,
            'page_header': template.render('header.html', {
            				'user': users.get_current_user(),
                    'admin': users.is_current_user_admin(),
            				'url': url,
				            'url_linktext': url_linktext,
            		}),
            'page_footer': template.render('footer.html', {}),
            }

        self.response.out.write(template.render(path, template_values))

class EraseBook(webapp.RequestHandler):
    def post(self):
        if users.get_current_user():
            books = BookSet().all().filter('uuid =', self.request.get('uuid'))
            results = books.fetch(1)
            for result in results:
              result.delete()

            self.redirect('/vendre')

class DeleteBuyer(webapp.RequestHandler):
    def post(self):
        if users.get_current_user():
            books = BookSet().all().filter('uuid =', self.request.get('uuid'))
            results = books.fetch(1)
            for book in results:
              book.buyer = None
              book.put()

            self.redirect('/vendre')

class BuyBooks(webapp.RequestHandler):
    def post(self):
        if users.get_current_user():
            books = BookSet().all().filter('uuid =', self.request.get('uuid'))
            results = books.fetch(1)
            book = results[0]
            logging.info("Setting buyer to: " + users.get_current_user().email())
            book.buyer = users.get_current_user().email()
            book.put()

            message = mail.EmailMessage(sender="Livres St-Joseph <livresstjoseph@gmail.com>")
            message.subject = "Vente de livres St-Joseph, Secondaire %d" % book.grade
            message.to = book.owner.email()
            message.reply_to = book.buyer
            logging.info("message body: " + self.request.get('message_body'))
            message.body = self.request.get('message_body')
            message.cc = book.buyer
            message.send()

        self.redirect('/')

class ContactOwner(webapp.RequestHandler):
    def post(self):
        uuid = self.request.get('uuid')
        default_message = gDefaultMessage
        description = ''
        if users.get_current_user():
            books = BookSet().all().filter('uuid =', uuid)
            book = books.fetch(1)
            description = book[0].description.encode('utf-8')

            path = os.path.join(os.path.dirname(__file__), 'contact.phtml')

            url = users.create_logout_url(self.request.uri)
            url_linktext = 'D&eacute;connexion'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Connexion'
            path = os.path.join(os.path.dirname(__file__), 'login.phtml')

        template_values = {
            'uuid': book[0].uuid,
            'default_message': gDefaultMessage % (users.get_current_user().nickname(), description),
            'user': users.get_current_user(),
            'admin': users.is_current_user_admin(),
            'url': url,
            'url_linktext': url_linktext,
            'page_header': template.render('header.html', {
            				'user': users.get_current_user(),
                    'admin': users.is_current_user_admin(),
            				'url': url,
				            'url_linktext': url_linktext,
            		}),
            'page_footer': template.render('footer.html', {}),
            'debug': gDebug,
            }

        self.response.out.write(template.render(path, template_values))

class NewBook(webapp.RequestHandler):
    def post(self):
        if users.get_current_user():
            books = BookSet()

            books.owner = users.get_current_user()
            books.buyer = None
            books.description = self.request.get('description')
            books.can_separate = False
            if self.request.get('can_separate'):
                books.can_separate = True
            try:
                price_str = self.request.get('price').replace(",", ".")
                books.price = int(round(float(price_str)))
            except:
                books.price = 100
            try:
              books.grade = int(self.request.get('grade'))
            except:
              books.grade = 0
            books.uuid = str(uuid.uuid1())

            books.put()
            self.redirect('/vendre')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/recherche', SearchPage),
                                      ('/listes', ListsPage),
                                      ('/vendre', MyBooksPage),
                                      ('/erasebook', EraseBook),
                                      ('/deletebuyer', DeleteBuyer),
                                      ('/buybooks', BuyBooks),
                                      ('/contactowner', ContactOwner),
                                      ('/newbook', NewBook)],
                                     debug=gDebug)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
