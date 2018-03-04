#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pony.orm import *

dbfilename='database.sqlite'

db = Database()
db.bind(provider='sqlite', filename=dbfilename, create_db=True)

class Users(db.Entity):
    id = PrimaryKey(int)
    username = Optional(str, unique=True)
    description = Optional(str)
    role = Optional(str, default='user')
    phone = Optional(str, default='')

sql_debug(False)
db.generate_mapping(create_tables=True)

@db_session
def refreshdb():
    for user in Users.select():
        user.delete()

@db_session
def get(id=False,role=False):
    if id:
        try:
            user=Users[id]
            return ({'id': user.id, 'username': user.username, 'description': user.description, 'role': user.role, 'phone_number': user.phone})
        except:
            return False
    elif role=='admin':
        result = []
        for user in Users.select(lambda u: u.role == 'admin').order_by(Users.id):
            result.append({'id': user.id, 'username': user.username, 'description': user.description, 'role': user.role, 'phone_number': user.phone})
        return result
    else:
        result = []
        for user in Users.select().order_by(Users.id):
            result.append({'id': user.id, 'username': user.username, 'description': user.description, 'role': user.role, 'phone_number': user.phone})
        return result

@db_session
def add(id,description=False,role='user',username=False,phone=False):
    if not id:
        raise ValueError('User id must be specified')
    with db_session:
        Users(id=id, username=username, description=description, phone=phone, role=role)

@db_session
def remove(id):
    user=Users.get(id=id)
    if user:
        user.delete()
    else:
        raise ValueError('User not found')

@db_session
def set(**kwargs):
    if not 'id' in kwargs:
        raise ValueError('User id must be specified')
    user=Users.get(id=kwargs['id'])
    if 'description' in kwargs:
        user.set(description=kwargs['description'])
    if 'role' in kwargs:
        user.set(role=kwargs['role'])