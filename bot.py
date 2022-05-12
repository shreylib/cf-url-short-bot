# -*- coding: utf-8 -*-

import re
import telegram
import telebot
import requests
import json
import logging
from functools import wraps
from random import *
from api import access_api, short_url, list_url, delete_url, cr_token, readable_time, check_url_exist

min_char = 4
max_char = 6

# CONFIG

from config import Config

API_TOKEN = Config.BOT_TOKEN
SHORTENER_DOMAIN = Config.SHORTENER_DOMAIN
EXT_TOKEN = Config.EXT_TOKEN
ADMIN_IDS = Config.ADMIN_IDS

# BOT CODE

try:
    ADMIN_LIST = ADMIN_IDS 
    restricted_mode = True
except:
    ADMIN_LIST = []  # ==> Do Not Touch This !!
    restricted_mode = False

bot = telebot.TeleBot(API_TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

def restricted(func):
    @wraps(func)
    def wrapped(update, *args, **kwargs):
        user_id = update.from_user.id
        if (restricted_mode) and (str(user_id) not in ADMIN_LIST):
            print("Unauthorized access denied for {} - {}.".format(user_id, update.from_user.username))
            bot.send_message(update.chat.id, "*Error :\t\t*You are not Authorized to access the bot.\n\nPls Contact [Bot Admin](https://t.me/s_rawal) !!", parse_mode='Markdown', disable_web_page_preview=True)
            return
        return func(update, *args, **kwargs)
    return wrapped

@bot.message_handler(commands=['start'])
@restricted
def start(m):
    bot.send_message(m.chat.id, text="""Hey !! Welcome to Shrey23 URL Shorten Bot !
    \n<b>To Shorten your URLs :-</b>
    Send /short <code>&lt;link&gt;</code> to the bot.
    \nSend /help for More Info !""", parse_mode=telegram.ParseMode.HTML)

@bot.message_handler(commands=['help'])
@restricted
def help(m):
    bot.send_message(chat_id=m.chat.id, text="""This Bot can Shorten Your URLs with support for Custom Keywords.
    \n<b>For using Random Keyword :-</b>
    Send /short <code>&lt;link&gt;</code>
    \n<b>For using Custom Keyword :-</b>
    Send /short <code>&lt;link&gt;</code> <code>&lt;keyword&gt;</code>
    \n<b>To get Link Info :-</b>
    Send /info <code>&lt;keyword/link&gt;</code>
    \n<b>To Delete A Link :-</b>
    Send /delete <code>&lt;keyword&gt;</code>""", parse_mode=telegram.ParseMode.HTML)

@bot.message_handler(commands=['short'])
@restricted
def short(m):
    chat = m.text.split()
    if len(chat) == 1:
        bot.send_message(chat_id=m.chat.id, text="""Pls Send the Command with Valid Queries !!
        \n<b>For using Random Keyword :-</b>
        Send /short <code>&lt;link&gt;</code>
        \n<b>For using Custom Keyword :-</b>
        Send /short <code>&lt;link&gt;</code> <code>&lt;keyword&gt;</code>""", parse_mode=telegram.ParseMode.HTML)
    else:
        link = m.text.split()[1]

        if re.match(r'^(?:http|ftp)s?://', link) is not None:
            allchar = "abcdefghijklmnopqrstuvwxyz0123456789"
            if len(m.text.split()) == 3:
                word = m.text.split()[2]
            if len(m.text.split()) == 2:
                word = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
            try:
                res = short_url(link, word)
                if res['status'] == 'success':
                    shortened_url = f'{SHORTENER_DOMAIN.rstrip("/")}/{res["result"]["shortName"]}'
                    bot.send_message(m.chat.id, "*Shortened URL :*\t\t" + str(shortened_url), parse_mode='Markdown', disable_web_page_preview=True)
                else:
                    bot.send_message(m.chat.id, "*Error :\t\t*" + str(res["message"]), parse_mode='Markdown', disable_web_page_preview=True)
            except:
                bot.send_message(m.chat.id, text = "*Error :\t\t*SYNTAX ERROR OR SERVER NOT REACHABLE; TRY AGAIN LATER\n\nSend /help for the correct syntax.", parse_mode='Markdown')
        else:
            bot.send_message(m.chat.id, text = "*Error :\t\t*Send A Valid URL.", parse_mode='Markdown')

@bot.message_handler(commands=['list'])
@restricted
def list(m):
    try:
        res = list_url()['result']
        n = 1
        msg_str = "*Your Shortened URLs :-*\n\n"
        for entry in res:
            long_url = entry['url']
            key = entry['shortName']
            entry_str = f"*{n}.* Long Url : `{long_url}`\nKeyword : `{key}`\nAccess Here -> [🔗]({SHORTENER_DOMAIN.rstrip('/')}/{key})\n\n"
            msg_str += entry_str
            n += 1
        bot.send_message(m.chat.id, msg_str, parse_mode='Markdown', disable_web_page_preview=True)
    except:
        bot.send_message(m.chat.id, text = "*Error :\t\t*SYNTAX ERROR OR SERVER NOT REACHABLE; TRY AGAIN LATER\n\nSend /help for the correct syntax.", parse_mode='Markdown')

@bot.message_handler(commands=['info'])
@restricted
def info(m):
    chat = m.text.split()
    if len(chat) == 1:
        bot.send_message(m.chat.id, text = """Pls Send the Command with Valid Queries !!
        \n<b>To get Link Info :-</b>
        Send /info <code>&lt;keyword&gt;</code>""", parse_mode=telegram.ParseMode.HTML)
    else:
        key = m.text.split()[1]
        try:
            if check_url_exist(key):
                res = list_url()['result']
                req_entry = [entry for entry in res if (entry['shortName'] == key)][0]
                long_url = req_entry['url']
                keyword = req_entry['shortName']
                created_at = readable_time(int(req_entry['createdAt']))
                created_by = req_entry['createdBy'].split('<')[0].strip()
                email_id = req_entry['createdBy'].split('<')[1].rstrip('>')
                msg_str = f"*URL Info :-*\n\nLong Url : `{long_url}`\nKeyword : `{keyword}` -> [🔗]({SHORTENER_DOMAIN.rstrip('/')}/{keyword})\nCreated At : `{created_at}`\nCreated By : `{created_by}`\nEmail ID : `{email_id}`"
                bot.send_message(m.chat.id, msg_str, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                bot.send_message(m.chat.id, "*Error :\t\t*Short URL does not exist.", parse_mode='Markdown')
        except:
            bot.send_message(m.chat.id, text = "*Error :\t\t*SYNTAX ERROR OR SERVER NOT REACHABLE; TRY AGAIN LATER\n\nSend /help for the correct syntax.", parse_mode='Markdown')

@bot.message_handler(commands=['delete'])
@restricted
def info(m):
    chat = m.text.split()
    if len(chat) == 1:
        bot.send_message(m.chat.id, text = """Pls Send the Command with Valid Queries !!
        \n<b>To Delete A Link :-</b>
        Send /delete <code>&lt;keyword&gt;</code>""", parse_mode=telegram.ParseMode.HTML)
    else:
        key = m.text.split()[1]
        try:
            if check_url_exist(key):
                res = delete_url(key)
                if res["status"] == 'success':
                    bot.send_message(m.chat.id, "The <b>keyword</b>: <code>"+res['result']['shortName']+"</code> has been successfully deleted.", parse_mode=telegram.ParseMode.HTML)
                else:
                    bot.send_message(m.chat.id, "*Error :\t\t*" + str(res["message"]), parse_mode='Markdown', disable_web_page_preview=True)
            else:
                bot.send_message(m.chat.id, "*Error :\t\t*Short URL does not exist.", parse_mode='Markdown')
        except:
            bot.send_message(m.chat.id, text = "*Error :\t\t*SYNTAX ERROR OR SERVER NOT REACHABLE; TRY AGAIN LATER\n\nSend /help for the correct syntax.", parse_mode='Markdown')

bot.polling(none_stop=True, timeout=3600)
