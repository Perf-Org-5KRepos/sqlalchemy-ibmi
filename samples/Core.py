"""
This tutorial will show you how to connect to the IBM i system and complete
basic functions using the Expression Language sqlalchmy method. For additional
functions see the tutorial in the docs here [1].
[1]: https://docs.sqlalchemy.org/en/13/core/tutorial.html
"""

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_
from sqlalchemy.sql import text

engine = create_engine("ibmi://nram:password12345678@oss72dev/?current_schema=SQLALC", echo=True)

# Creating Tables

metadata = MetaData()
users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(50)),
              Column('fullname', String(50)),
              )

addresses = Table('addresses', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('user_id', None, ForeignKey('users.id')),
                  Column('email_address', String(50), nullable=False),
                  )

metadata.create_all(engine)

# Insertions

with engine.connect() as conn:
    # single
    ins = users.insert().values(name='jack', fullname='Jack Jones')
    conn.execute(ins)

    # multiple
    conn.execute(addresses.insert(), [
           {'user_id': 1, 'email_address': 'jack@yahoo.com'},
           {'user_id': 1, 'email_address': 'jack@msn.com'},
        ])

    # Select statements
    result = conn.execute(select([users]))

    for row in result:
        print(row)

    # Select specific columns
    result = conn.execute(select([users.c.name, users.c.fullname]))

    for row in result:
        print(row)

    # Conjunctions

    s = select([(users.c.fullname +
                ", " + addresses.c.email_address).
                label('title')]).\
        where(
              and_(
                  users.c.id == addresses.c.user_id,
                  users.c.name.between('a', 'z'),
                  or_(
                     addresses.c.email_address.like('%@aol.com'),
                     addresses.c.email_address.like('%@msn.com')
                  )
              )
           )

    print(conn.execute(s).fetchall())

    # Textual SQL

    s = text("SELECT users.fullname || ', ' || addresses.email_address AS"
             " title FROM users, addresses WHERE users.id = addresses.user_id "
             "AND users.name BETWEEN :x AND :y "
             "AND (addresses.email_address LIKE :e1 "
             "OR addresses.email_address LIKE :e2)")

    print(conn.execute(s, x='m', y='z', e1='%@aol.com', e2='%@msn.com').fetchall())

    # Updates
    stmt = users.update(). where(users.c.name == 'jack').values(name='ed')
    conn.execute(stmt)

    # Deletion
    conn.execute(users.delete().where(users.c.name > 'h'))

    result = conn.execute(select([users]))

    for row in result:
        print(row)