from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='dima', email='dmitry.burnyshev@gmail.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'cc59952929876f8fbf0ea8c92605b37a?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='cat', email='cat@mail.ru')
        u2 = User(username='dog', email='dog@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'dog')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'cat')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u1.followers.count(), 0)

    def test_follow_posts(self):
        u1 = User(username='cat', email='cat@mail.ru')
        u2 = User(username='dog', email='dog@mail.ru')
        u3 = User(username='bird', email='bird@mail.ru')
        u4 = User(username='pig', email='pig@mail.ru')
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        now = datetime.utcnow()
        p1 = Post(body='post from cat', author=u1, timestamp=now + timedelta(seconds=1))
        p2 = Post(body='post from dog', author=u2, timestamp=now + timedelta(seconds=2))
        p3 = Post(body='post from bird', author=u3, timestamp=now + timedelta(seconds=3))
        p4 = Post(body='post from pig', author=u4, timestamp=now + timedelta(seconds=4))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2)  # cat follows dog
        u1.follow(u4)  # cat follows pig
        u2.follow(u3)  # dog follows bird
        u3.follow(u4)  # bird follows pig
        db.session.commit()

        f1 = u1.followed_post().all()
        f2 = u2.followed_post().all()
        f3 = u3.followed_post().all()
        f4 = u4.followed_post().all()
        self.assertEqual(f1, [p4, p2, p1])
        self.assertEqual(f2, [p3, p2])
        self.assertEqual(f3, [p4, p3])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
