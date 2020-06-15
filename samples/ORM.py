"""
This tutorial will show you how to connect to the IBM i system and complete
basic functions using the ORM sqlalchmy method. For additional functions see
the sqlalchemy ORM tutorial in the docs here [1].
[1]: https://docs.sqlalchemy.org/en/13/orm/tutorial.html
"""

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

engine = sa.create_engine("ibmi://nram:password12345678@oss72dev/?current_schema=SQLALC")

Base = declarative_base()


# defining the User object mapping
class User(Base):
    __tablename__ = 'users'

    schema = 'SQLALC'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    nickname = Column(String(50))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name, self.fullname, self.nickname)


# create the mapping
Base.metadata.create_all(engine)


# set up session to create Users
Session = sessionmaker(bind=engine)

session = Session()

# define and add user
ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
session.add(ed_user)

# search for added user
our_user = session.query(User).filter_by(name='ed').first()

print(our_user)

# Adding and Updating Objects

session.add_all([
    User(name='wendy', fullname='Wendy Williams', nickname='windy'),
    User(name='mary', fullname='Mary Contrary', nickname='mary'),
    User(name='fred', fullname='Fred Flintstone', nickname='freddy')])

ed_user.nickname = 'eddie'

print(session.dirty)

print(session.new)

session.commit()

# Rolling Back

ed_user.name = 'Edwardo'
fake_user = User(name='fakeuser', fullname='Invalid', nickname='12345')
session.add(fake_user)
session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()

# rollback new user added

session.rollback()

session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()

# Querying

for instance in session.query(User).order_by(User.name):
    print(instance.name, instance.fullname)

for name, fullname in session.query(User.name, User.fullname):
    print(name, fullname)


# Relationships
class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    # create relationship with user
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address


# create User relationship with Address
User.addresses = relationship(
    "Address", order_by=Address.id, back_populates="user")
# add cascade="all, delete, delete-orphan" to relationship to cascade delete

Base.metadata.create_all(engine)

jack = User(name='jack', fullname='Jack Bean', nickname='gjffdd')

jack.addresses = [
                Address(email_address='jack@google.com'),
                Address(email_address='j25@yahoo.com')]

session.add(jack)
session.commit()

jack = session.query(User).filter_by(name='jack').one()

# Joins

print(session.query(User).join(Address, User.id == Address.user_id).all())

# Deleting

session.delete(jack)
print(session.query(User).filter_by(name='jack').count())