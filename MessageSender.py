import logging
import configparser
from flask import Flask
from flask_restful import request

import smtplib as smtp
import telebot

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

handler = logging.FileHandler('run.log')
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)

app.logger.info('MessageSender is start')

MAX_TRY = 15


class Sender:

    config = None

    @staticmethod
    def load_config():
        """
        Load config from ini
        """
        Sender.config = configparser.ConfigParser()
        Sender.config.read('MessageSender.ini', encoding="windows-1251")

    @staticmethod
    def send_mail(data: dict) -> dict:
        """
        Send message by the SMTP
        :param data: {'to': 'name', 'subject': 'Subj', 'text': 'text'}
        :return: {'res': 'OK'} or {'res': 'ERROR', 'descr': 'something is wrong'}
        """
        resp = {}
        sender = Sender.config['MAIL']['login']
        passwd = Sender.config['MAIL']['passwd']
        server = smtp.SMTP(Sender.config['MAIL']['SMTP'], int(Sender.config['MAIL']['port']))
        server.starttls()
        to = data.get('to', None)
        if to is None:
            erm = 'user not found'
            app.logger.error(erm)
            resp['res'] = 'ERROR'
            resp['descr'] = erm
            return resp
        subject = data.get('subject', '')
        text = data.get('text', None)
        if text is None:
            erm = 'send text is empty'
            app.logger.error(erm)
            resp['res'] = 'ERROR'
            resp['descr'] = erm
            return resp
        current_try = 0
        while current_try <= MAX_TRY:
            current_try += 1
            try:
                server.login(sender, passwd)
                server.sendmail(sender, to, f'Subject:{subject}\n{text}')
            except Exception as ex:
                app.logger.exception(f'Exception: {ex}')
            else:
                app.logger.info('Send by SMTP was successful')
                resp['resp'] = 'OK'
                return resp
        resp['res'] = 'ERROR'
        resp['descr'] = 'Mail do not sent'
        return resp

    @staticmethod
    def send_telegram(data: dict) -> dict:
        """
        Send message by the telegram
        :param data: {'to': 'name', 'text': 'text'}
        :return: {'res': 'OK'} or {'res': 'ERROR', 'descr': 'something is wrong'}
        """
        resp = {}
        if not Sender.config.has_section('TELEGRAM'):
            app.logger.error(f'ini has no section TELEGRAM')
            resp['res'] = 'ERROR'
            return resp
        chat = int(Sender.config.get('TELEGRAM', data['to']))
        if not chat:
            erm = 'user not found'
            app.logger.error(erm)
            resp['res'] = 'ERROR'
            resp['descr'] = erm
            return resp
        text = data.get('text', None)
        if text is None:
            erm = 'send text is empty'
            app.logger.error(erm)
            resp['res'] = 'ERROR'
            resp['descr'] = erm
            return resp
        else:
            token = Sender.config['TELEGRAM']['token']
            bot = telebot.TeleBot(token)
            try:
                is_bot = bot.get_me()
            except telebot.apihelper.ApiException as taa:
                app.logger.exception(f'{taa}')
                resp['res'] = 'ERROR'
                resp['descr'] = 'Bot API exception'
                return resp
            if not hasattr(is_bot, 'id'):
                resp['res'] = 'ERROR'
                resp['descr'] = 'Bot not found'
                app.logger.exception(resp['descr'])
                return resp
            else:
                app.logger.info(f'Bot: {is_bot}')
            current_try = 0
            while current_try <= MAX_TRY:
                current_try += 1
                try:
                    bot.send_message(chat, text)
                except Exception as _ex:
                    app.logger.exception(f'Unrecognized exception: {_ex}')
                else:
                    app.logger.info('Send by telegram was successful')
                    resp['res'] = 'OK'
                    return resp
            erm = 'Send message is unsuccessful. MAX_TRY exceeded'
            app.logger.error(erm)
            resp['res'] = 'ERROR'
            resp['descr'] = erm
            return resp


@app.route('/', methods=['GET'])
def check() -> dict:
    resp = {}
    if request.method == 'GET':
        resp['res'] = 'OK'
        app.logger.info('Check server')
        return resp


@app.route('/telegram', methods=['POST'])
def telegram() -> dict:
    resp = {}
    Sender.load_config()
    data = {'to': request.form.get('to')}
    if not data['to']:
        resp['res'] = 'ERROR'
        resp['descr'] = 'Email address is not found'
        return resp
    data['text'] = request.form.get('text')
    if not data['text']:
        resp['res'] = 'ERROR'
        resp['descr'] = 'Message text is not found'
        return resp
    resp = Sender.send_telegram(data)
    return resp


@app.route('/mail', methods=['POST'])
def mail() -> dict:
    resp = {}
    Sender.load_config()
    data = {'to': request.form.get('to')}
    if not data['to']:
        resp['res'] = 'ERROR'
        resp['descr'] = 'Email address is not found'
        return resp
    if request.form.get('subject'):
        data['subject'] = request.form.get('subject')
    data['text'] = request.form.get('text')
    if not data['text']:
        resp['res'] = 'ERROR'
        resp['descr'] = 'Message text is not found'
        return resp
    resp = Sender.send_mail(data)
    return resp
