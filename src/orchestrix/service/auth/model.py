from sqlalchemy import Column, Integer, String, Table, ForeignKey, MetaData

metadata = MetaData()

users = Table('users', metadata, 
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('fullname', String),
)

groups = Table('groups', metadata, 
    Column('id', Integer, primary_key=True),
    Column('name', String),
)

roles = Table('roles', metadata, 
    Column('id', Integer, primary_key=True),
    Column('name', String),
)

user_groups = Table('user_groups', metadata, 
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id')),
)

user_roles = Table('user_roles', metadata, 
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id')),
)

group_roles = Table('group_roles', metadata, 
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('role_id', Integer, ForeignKey('roles.id')),
)
