"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        user1 = User.signup("test1", "jenkins@gmail.com", "password", None)
        user1.id = 1001

        user2 = User.signup("test2", "hello@gmail.com", "password", None)
        user2.id = 1002

        db.session.commit()

        self.user2 = user2
        self.user2.id = user2.id

        self.user1 = user1
        self.user1.id = user1.id

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_message_delete(self):
        test_message = Message(id=1001, text='test message', user_id=self.user1.id)
        db.session.add(test_message)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = client.post('/messages/1001/delete', follow_redirects=True)
           
            self.assertEqual(resp.status_code, 200)

            test_message = Message.query.get(1001)
            self.assertIsNone(test_message)

    def test_logged_out_add_message(self):
            with self.client as client:
                resp = client.post('/messages/new', data={"text": "Hello"}, follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('Access unauthorized', str(resp.data))

    def test_logged_out_delete_message(self):

        test_message = Message(id=1003, text='test message', user_id=self.user2.id)
        db.session.add(test_message)
        db.session.commit()

        with self.client as client:
            resp = client.post("/messages/1003/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            test_message = Message.query.get(1003)
            self.assertIsNotNone(test_message)


    # need help with two tests below
    def test_add_as_wrong_user(self):

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = client.post("/messages/new", data={"text": "Hello", "timestamp": "2017-01-21 11:04:53.522807", "user_id": "99"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
 

    def test_delete_as_wrong_user(self):

        test_message = Message(id=1003, text='test message', user_id=self.user2.id)
        db.session.add(test_message)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = client.post("/messages/1003/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1003)
            self.assertIsNotNone(m)

    