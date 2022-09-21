"""User model tests."""

# run these tests like:
#
# FLASK_ENV=production python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User

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


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    def test_validations_fail(self):
        invalid_user = User.signup(None, "hello@gmail..com", "password", None)
        invalid_user.id = 1333
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authentication(self):
        user = User.authenticate(self.user1.username, 'password')
        self.assertEqual(user.id, self.user1.id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate('dumbusername', 'password'))

    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.user1.username, 'dumbpassword'))