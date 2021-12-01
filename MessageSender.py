import logging
import configparser

import smtplib as smtp

class MessageSender:
    def __init__(self):
        self.logging = logging
        self.logging.basicConfig(filename='run.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.config = configparser.ConfigParser()
        self.config.read('MessageSender.ini', encoding="windows-1251")
        self.sender = self.config['MAIL']['login']
        self.passwd = self.config['MAIL']['passwd']
        self.server = smtp.SMTP(self.config['MAIL']['SMTP'], self.config['MAIL']['port'])
        self.server.starttls()

    def send(self, mail: dict) -> None:
        '''
        Input:
        dict like {'to': ...,
                   'subject': ...,
                   'text': ...
        '''
        to = mail['to']
        subj = mail['subject']
        text = mail['text']
        try:
            self.server.login(self.sender, self.passwd)
            self.server.sendmail(self.sender, to, f'Subject:{subj}\n{text}')
        except Exception as ex:
            self.logging.exception(f'Exception: {ex}')
        else:
            self.logging.info('message has been sent')

if __name__ == "__main__":
    MS = MessageSender()
    m = {}
    m['to'] = 'something@mail.ru'
    m['subject'] = 'Info'
    m['text'] = 'Test'
    MS.send(m)