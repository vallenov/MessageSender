#!/usr/bin/sh

WORK_DIR=/home/vladimir/prog/python/projects/MessageSender

cd $WORK_DIR
#. .venv/bin/activate && echo activate venv
pyenv activate MessageSender && echo activate venv
export FLASK_APP=MessageSender.py && echo export vars
echo Message server is start
#./.venv/bin/flask run --host=0.0.0.0 --port=5111
~/.pyenv/versions/MessageSender/bin/flask run --host=0.0.0.0 --port=5111
#python MessageSender.py
