from flask_socketio import emit
from .extensions import socketio
from flask import request

local_data = {}


from timeit import default_timer as timer

# request.sid => The session id of the user 
# can use it to identify if it is the same user

all_users = dict()

@socketio.on("connect")
def handle_connect():
    print("Connected Python")

@socketio.on("my event")
def handle_my_event(data=dict()):
    print('data is', data)
