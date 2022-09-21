"""User views tests."""

# run these tests like:
#
# FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase
from models import db, connect_db, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """User views tests."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        user1 = User.signup("test1", "jenkins@gmail.com", "password", None)
        user1.id = 1001

        user2 = User.signup("test2", "hello@gmail.com", "password", None)
        user2.id = 1002

        user3 = User.signup("test3", "scooby@gmail.com", "password", None)
        user3.id = 1003

        db.session.commit()

        self.user1 = user1
        self.user1.id = user1.id

        self.user2 = user2
        self.user2.id = user2.id

        self.user3 = user3
        self.user3.id = user3.id

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as client:
            resp = client.get('/users')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('.com', str(resp.data))
            self.assertIn('test2', str(resp.data))

    def test_users_show(self):
        with self.client as client:
            resp = client.get(f'/users/{self.user1.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test1', str(resp.data))

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.user1.id, user_following_id=self.user3.id)
        f2 = Follows(user_being_followed_id=self.user3.id, user_following_id=self.user1.id)
        f3 = Follows(user_being_followed_id=self.user2.id, user_following_id=self.user3.id)


        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_show_following(self):
        self.setup_followers()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user3.id

            resp = client.get(f'/users/{self.user3.id}/following')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test2', str(resp.data))

    def test_show_followers(self):
        self.setup_followers()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user3.id

            resp = client.get(f'/users/{self.user3.id}/followers')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test1', str(resp.data))

    def test_logged_out_following_page(self):
        self.setup_followers()
        with self.client as client:

            resp = client.get(f'/users/{self.user3.id}/following', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))

    def test_logged_out_followers_page(self):
        self.setup_followers()
        with self.client as client:

            resp = client.get(f'/users/{self.user3.id}/followers', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', str(resp.data))