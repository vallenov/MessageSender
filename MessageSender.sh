#!/usr/bin/sh

WORK_DIR=/home/vladimir/prog/python/projects/MessageSender

cd $WORK_DIR
if [ -d .venv ]
then
  venv=True
else
  venv=False
fi

if [ $venv = True ]
then
  . .venv/bin/activate && echo activate venv
else
  pyenv activate MessageSender && echo activate venv
fi

export FLASK_APP=MessageSender.py && echo export vars

echo Message server is start

if [ $venv = True ]
then
  ./.venv/bin/flask run --host=0.0.0.0 --port=5111
else
  /home/vladimir/.pyenv/versions/MessageSender/bin/flask run --host=0.0.0.0 --port=5111
fi
#python MessageSender.py
