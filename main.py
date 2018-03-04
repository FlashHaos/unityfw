#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

from modules.telebottle import Application, template, decode
from modules.configmodule import config
from model import users
import logging

logging.basicConfig(level=logging.INFO)

app = Application(token=config().get('telegram','token'))

@app.bot.message_handler(commands=["start"])
def start(message):
    app.answer(command=message.text,message=message)

@app.bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    app.answer(command=call.data,message=call.message)


@app.route("/start")
def start():
    keyboard={
            'Пользователи':'/admin/users',
            'Вышли текст':'/manual',
            'Вышли картинку':'/image',
            'Проверка ввода':'/hello'
        }
    return template("Главное меню",keyboard,newmessage=True)


@app.route("/hello")
def hello():
    return template("Привет, введите текст:",next='/hello',newmessage=True,post=True)


@app.route("/hello/post=<poststring>")
def hello(poststring):
    poststring=decode(poststring)
    return template("Введен {0}".format(poststring),next='/start',newmessage=True)


@app.route("/manual")
def usersList():
    return template("Длинный текст без кнопок",next='/start')


@app.route("/image")
def usersList():
    return template("image",image=r'C:\Users\Alex\Pictures\2018-01-08\IMG_1464.JPG',next='/start')


@app.route("/admin/users")
def usersList():
    keyboard = {user['username']:'/admin/users/{0}'.format(user['id']) for user in users.get()}
    return template("Список пользователей:",keyboard,back='/start&newmessage=False',keyboard_row_width=1)


app.run()