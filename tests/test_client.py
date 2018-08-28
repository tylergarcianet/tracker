import unittest
from app import create_app, db
from app.models import User, Ticket, Comment
from flask import url_for


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_lockout_redirect(self):
        """
        Verify redirect
        :return:
        """
        response = self.client.get(url_for("main.index"), follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def create_dummy_user(self, email):
        response = self.client.post(url_for("auth.register"), data={
            "email": email,
            "username": "john",
            "password": "cat",
            "password2": "cat"
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(url_for("auth.login"), data={
            "email": email,
            "password": "cat"
        }, follow_redirects=True)

        user = User.query.filter_by(email=email).first()
        user.generate_confirmation_token()
        token = user.generate_confirmation_token()
        self.client.get(url_for("auth.confirm", token=token), follow_redirects=True)
        return user

    def test_lockout_correct_message_and_page(self):
        """
        Ensures the error message is populated and redirects to correct place
        :return:
        """
        response = self.client.get(url_for("main.index"), follow_redirects=True)
        self.assertIn(b"Please log in to access this page.", response.data)

    def test_register_and_login(self):
        response = self.client.post(url_for("auth.register"), data={
            "email": "john@example.com",
            "username": "john",
            "password": "cat",
            "password2": "cat"
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(url_for("auth.login"), data={
            "email": "john@example.com",
            "password": "cat"
        }, follow_redirects=True)
        self.assertIn(b"Before you can access this site you need to confirm your account", response.data)

        user = User.query.filter_by(email="john@example.com").first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for("auth.confirm", token=token), follow_redirects=True)
        self.assertIn(b"You have confirmed your account", response.data)

        #Test user is not admin
        self.assertFalse(user.isadmin)

        #log out
        response = self.client.get(url_for("auth.logout"), follow_redirects=True)
        self.assertIn(b"You have been logged out", response.data)

    def test_post_new_ticket_and_reply(self):
        #create user and ticket
        author = self.create_dummy_user("john102@hotmail.com")
        ticket = Ticket(tickettitle="test title", ticketrequest="test body", user=author)
        response = self.client.post(url_for("main.new_ticket"), data={
            "tickettitle": "test title",
            "ticketrequest": "test ticket body"}, follow_redirects=True)
        self.assertIn(b"test ticket body", response.data)
        self.assertIn(b"john", response.data)
        #create ticket comment
        response = self.client.post(url_for("main.ticket", ticketnum=ticket.id), data={
            "commentbody": "test comment body"
        }, follow_redirects=True)
        self.assertIn(b"test comment body", response.data)

    def test_correct_admin(self):
        author = self.create_dummy_user("dummy@tylergarcia.net")
        self.assertTrue(author.isadmin)
