"""User model tests."""

# run these tests like:
#
# FLASK_ENV=production python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Likes 

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User.signup("test1", "jenkins@gmail.com", "password", None)
        user1.id = 1001

        user2 = User.signup("test2", "hello@gmail.com", "password", None)
        user2.id = 1002

        db.session.commit()

        user1 = User.query.get(user1.id)
        user2 = User.query.get(user2.id)

        self.user1 = user1
        self.user1.id = user1.id

        self.user2 = user2
        self.user2.id = user2.id

        self.client = app.test_client()


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Test message model"""
        
        test_message = Message(text="this is a test", user_id=self.user1.id)
        db.session.add(test_message)
        db.session.commit()

        self.assertEqual(len(self.user1.messages), 1)
        self.assertEqual(self.user1.messages[0].text, "this is a test")

    def test_message_like(self):
        test_message1 = Message(text="this is a test", user_id=self.user2.id)

        test_message2 = Message(text="just for fun", user_id=self.user1.id)

        db.session.add_all([test_message1, test_message2])
        db.session.commit()

        self.user1.likes.append(test_message1)
        self.user1.likes.append(test_message2)

        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == self.user1.id).all()
        self.assertEqual(len(likes), 2)
        self.assertEqual(likes[0].message_id, test_message1.id)
        self.assertEqual(likes[1].message_id, test_message2.id)
        self.assertEqual(likes[1].user_id, self.user1.id)

    def test_message_unlike(self):
        test_message1 = Message(text="this is a test", user_id=self.user1.id)

        test_message2 = Message(text="just for fun", user_id=self.user1.id)

        db.session.add_all([test_message1, test_message2])
        db.session.commit()

        self.user1.likes.append(test_message1)
        self.user1.likes.clear()
        self.user1.likes.append(test_message2)
        self.user1.likes.clear()

        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == self.user1.id).all()
        self.assertEqual(len(likes), 0)