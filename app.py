from __future__ import division
from datetime import datetime, timedelta

import os
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
import json
#import redis
from redis import StrictRedis
from flask_restful import reqparse
from helper import getCurrentKey, getPassword
import urllib
from ML import pipeline as pipe

from ML import tStreaming as tstream


import time
from functools import update_wrapper

import pickle

from flask import Flask, abort, request, jsonify, g, url_for, Response, render_template,  session, redirect


from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

import requests

 
dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"


gevent.monkey.patch_all()

CDELAY = 30 #1 minutes
MINUTE = 60 #1 minutes


app = Flask(__name__)



parser = reqparse.RequestParser()

redis = StrictRedis(host='localhost', port=6379, db=0)



app.config['SECRET_KEY'] = getPassword ( )
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://test:test@localhost/newsdb"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)
auth = HTTPBasicAuth()


mlPipe = pipe.Pipeline () #create the pipeline object once


#start the tweet stream

twtStreamObj = tstream.TweetStream()
twtStreamObj.runEveryStream( )


version = "/v1"


class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)

def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)

def on_over_limit(limit):
    return 'You hit the rate limit', limit

def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator


@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route(version + '/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return ( jsonify({'username': user.username}) )



def event_messages(key):
    '''
        This provided the tweet that has been labeled with topic, sentiment, and spam metadata
    '''
    count = 0
    one_hour = 3600
    userObj = pickle.loads(redis.get(key))

    token =  userObj.generate_auth_token(one_hour)

    try:
        while User.verify_auth_token(token): #verify the user again

            if (count % MINUTE) == 0:
                yield "current data\n"
                #yield str (unpacked_object) + "\n"
                key = getCurrentKey ( )

                token =  userObj.generate_auth_token(one_hour)

                #start the tweet stream
                twtStreamObj.runEveryStream( )
 
            #while waiting send a fake message to keep channels open
            yield "waiting \n"
            gevent.sleep(CDELAY)
            count = count + 1

    except GeneratorExit: # Or maybe use flask signals
        pass


@app.route(version + '/messages')
@auth.login_required
def messages():
    #session.clear()
    userObj = g.user
    userID = userObj.id

    pickled_object = pickle.dumps(userObj )
    key = 'user_'+  str(userID)
    redis.set(key, pickled_object)

    expireTime = 24 * 3600 * 365 # 1 year

    redis.expire (key, expireTime) 

    return Response( event_messages(key), mimetype='text/event-stream' )

"""
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"miguel","password":"python"}' http://127.0.0.1:8001/v1/api/users


curl -u miguel:python -i -X GET http://127.0.0.1:8001/v1/messages

"""


if __name__ == '__main__':
    '''
    if not os.path.exists('db.sqlite'):
        db.create_all()
    '''
    db.create_all()
    http_server = WSGIServer(('127.0.0.1', 8001), app)
    http_server.serve_forever()


