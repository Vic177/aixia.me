# -*- coding: utf-8 -*-
import datetime, bleach
from . import db, login_manager

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from markdown import markdown


class User(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  # 与存储在User模型中的密码散列值对比
        return check_password_hash(self.password_hash, password)


belong_to = db.Table('belong_to',
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
                     )


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    cover = db.Column(db.String(64))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    scheme = db.Column(db.Text)
    publish = db.Column(db.Boolean, default=True, index=True)

    create_date = db.Column(db.DateTime, default=datetime.date.today())
    update_date = db.Column(db.DateTime, default=datetime.date.today())

    tags = db.relationship('Tag',
                           secondary=belong_to,
                           backref=db.backref('posts', lazy='dynamic'),
                           lazy='dynamic')

    @staticmethod
    def generate_fake(count=20):
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            p = Post(title=forgery_py.internet.user_name(True),
                     body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     create_date=forgery_py.date.date(True),
                     )
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """把body字段中的文本渲染成HTML格式，保存在body_html"""
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']  # 白名单
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))  # 真实的转换过程

    @staticmethod
    def scheme_html(target, value, oldvalue, initiator):
        allowed_tags = []
        target.scheme = bleach.linkify(bleach.clean(value, tags=allowed_tags, strip=True))[:42] + '...'


db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Post.body_html, 'set', Post.scheme_html)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    cover = db.Column(db.String(64))
    name = db.Column(db.String(64))
    url_name = db.Column(db.String(64), index=True)


class General(db.Model):
    __tablename__ = '设置'
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(64), default="Let's face reality, loyalty to an ideal.")
    blog_description = db.Column(db.String(64), default="面对现实，忠于理想")
    blog_cover = db.Column(db.String(64), default='https://luoleiorg.b0.upaiyun.com/tmp/yasuko/yasuko.jpg')
    Posts_per_page = db.Column(db.Integer, default=5)
    author_detail = db.Column(db.String(64), default='自学Python，尝试Flask-Web开发，尝试写博客，现居上海')


@login_manager.user_loader
def load_user(id_user):
    """加载用户的回调函数"""
    return User.query.get(int(id_user))
