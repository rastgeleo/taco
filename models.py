import datetime

from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash

DATABASE = SqliteDatabase('taco.db')


class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    @classmethod
    def create_user(cls, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            raise ValueError("User already exist")


class Taco(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
        User,
        backref='tacos'
    )
    protein = CharField(max_length=100)
    shell = CharField(max_length=100)
    cheese = BooleanField(default=False)
    extras = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


def initialize():
    """Initialize database. Create tables"""
    DATABASE.connect()
    DATABASE.create_tables([User, Taco], safe=True)
    DATABASE.close()
