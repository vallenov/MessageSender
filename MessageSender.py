import logging
import configparser
from flask import Flask
from flask_restful import request
import smtplib as smtp

app = Flask(__name__)


@app.route('/', methods=['POST'])
def send() -> dict:
    '''
    Input:
    dict like {'to': ...,
               'subject': ...,
               'text': ...
    '''
    resp = {}
    logging.basicConfig(filename='run.log',
                             level=logging.INFO,
                             format='%(asctime)s - %(levelname)s - %(message)s')
    config = configparser.ConfigParser()
    config.read('MessageSender.ini', encoding="windows-1251")
    sender = config['MAIL']['login']
    passwd = config['MAIL']['passwd']
    server = smtp.SMTP(config['MAIL']['SMTP'], int(config['MAIL']['port']))
    server.starttls()
    to = request.form.get('to')
    if not to:
        resp['res'] = 'ERROR'
        resp['descr'] = 'Email address is not found'
        return resp
    subj = request.form.get('subject')
    text = request.form.get('text')
    try:
        server.login(sender, passwd)
        server.sendmail(sender, to, f'Subject:{subj}\n{text}')
    except Exception as ex:
        logging.exception(f'Exception: {ex}')
        resp['res'] = 'ERROR'
        resp['descr'] = 'Mail do not sent'
        return resp
    else:
        logging.info('message has been sent')
        resp['resp'] = 'OK'
        return resp

if __name__ == "__main__":
    app.run(debug=True)