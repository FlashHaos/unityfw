#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import re, telebot, logging, os
from telebot import types
from model import users

class Application():

    def __init__(self,token):
        self.bot = telebot.TeleBot(token)
        self.routes = []

    @staticmethod
    def build_route_pattern(route):
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        return re.compile("^{}$".format(route_regex))

    def route(self, route_str):
        def decorator(f):
            route_pattern = self.build_route_pattern(route_str)
            self.routes.append((route_pattern, f))
            return f

        return decorator

    def get_route_match(self, path):
        for route_pattern, view_function in self.routes:
            m = route_pattern.match(path)
            if m:
                return m.groupdict(), view_function
        return None

    def serve(self, path):
        route_match = self.get_route_match(path)
        if route_match:
            kwargs, view_function = route_match
            return view_function(**kwargs)
        else:
            logging.warning('Route "{}" has not been registered'.format(path))
            #raise ValueError('Route "{}" has not been registered'.format(path))

    def answer(self,command,message):
        userrole = users.get(id=message.chat.id)['role']
        if userrole not in ['user', 'admin'] or ('admin' in command and userrole != 'admin'):
            logging.warning('{2} {3} ({1}) requested page "{0}": ACCESS DENIED'.
                format(command, message.chat.id,message.chat.first_name, message.chat.last_name))
            return
        logging.info('{2} {3} ({1}) requested page "{0}"'.
            format(command, message.chat.id,message.chat.first_name, message.chat.last_name))
        variables=command.split('&')[1:]
        command=command.split('&')[0]
        reply = self.serve(command)
        for row in variables:
            key,value = row.split('=')
            if value.lower() in ['true','false']:
                value = (value.lower() == 'true')
            reply[key] = value
        if reply:
            keyboard = False
            if reply['keyboard']:
                keyboard = types.InlineKeyboardMarkup(row_width=int(reply['keyboard_row_width']))
                keyboard.add(*[types.InlineKeyboardButton(text=key, callback_data=value)
                               for key, value in reply['keyboard'].items()
                               if not ('admin' in value) or (userrole == 'admin')])
                if reply['back']:
                    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=reply['back']))
            if reply['image']:
                self.sendimage(self.bot,reply['image'],message.chat.id)
            if reply['newmessage']:
                message = self.bot.send_message(message.chat.id, "...")
            self.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=reply['text'],
                reply_markup=keyboard
            )
            if reply['post']:
                self.bot.register_next_step_handler(message,lambda msg: self.post(message=msg, reply=reply, command=command))
            elif reply['next']:
                self.answer(command=reply['next'],message=message)

    def post(self,message,reply,command):
        poststring = encode(message.text)
        if not poststring:
            self.answer(command=command,message=message)
            return
        logging.info('{2} {3} ({1}) posted value "{0}"'.
            format(decode(poststring), message.chat.id,message.chat.first_name, message.chat.last_name))
        if not reply['next']:
            reply['next'] = "/start"
        self.answer(command="{0}/post={1}&newmessage=True".format(reply['next'],poststring),message=message)

    def sendimage(self, bot, filename, chatid):
        try:
            photo = open(filename, 'rb')
            bot.send_photo(chatid, photo)
            return True
        except:
            logging.critical('File "{0}" cannot be opened!'.format(filename))
            return False

    def run(self):
        self.bot.polling(none_stop=True)

def template(text="...",keyboard=False,newmessage=False,back=False,next=False,keyboard_row_width=3,post=False,image=False):
    reply={
        'text':text,
        'keyboard': keyboard,
        'newmessage': newmessage,
        'back': back,
        'next': next,
        'keyboard_row_width': keyboard_row_width,
        'post': post,
        'image':image
    }
    return reply

def encode(string):
    string = string.replace('/','%s!').replace('=','%e!').replace('&','%a!').replace('\\','%b!')
    return string

def decode(string):
    string = string.replace('%s!','/').replace('%b!','\\').replace('%a!','&').replace('%e!','=')
    return string