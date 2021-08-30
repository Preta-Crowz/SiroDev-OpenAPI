# -*- coding: utf-8 -*-

import json
config = json.load(open("config.json"))

import zerologger as zlog
logger = zlog.Logger(config["RAVEN"]["KEY"],config["RAVEN"]["SECRET"],config["RAVEN"]["PROJECT"],config["APPNAME"],config["LOG"])

from flask import Flask,render_template,request,send_file
import Levenshtein as leven
try:
    from winmagic import magic
except:
    import magic
import base64
import time
import re
import requests
import socket
import urllib3
import execjs
logger.info(f"execjs started with {execjs.get().name}")
import ast


import squarecrypt as sqc

logger.info("Setting up application")
app = Flask(config["APPNAME"])

import logging
logging.getLogger('werkzeug').setLevel(-100)

@app.route('/', methods=['GET'])
def help():
    return response(render_template("index.html"))

@app.route('/sqc/encode', methods=['POST'])
def sqcEncode():
    rdat = request.form.to_dict()
    if rdat == {}: rdat = request.json
    query = rdat["query"]
    data = {}
    data['req'] = {'query':query}
    data['api'] = {'version':'1.0','date':'190806'}
    data['res'] = sqc.crypt(query)
    return response(data)

@app.route('/sqc/decode', methods=['POST'])
def sqcDecode():
    rdat = request.form.to_dict()
    if rdat == {}: rdat = request.json
    query = rdat["query"]
    data = {}
    data['req'] = {'query':query}
    data['api'] = {'version':'1.0','date':'190806'}
    if re.match("[　▘▝▖▗▀▌▚▞▐▄▛▜▙▟█]*",query)[0] != query:
        data['error'] = {"code":"unk_char","text":"잘못된 문자가 있는 것 같습니다. 내용을 다시 확인하세요."}
    else:
        try:
            data['res'] = sqc.decrypt(query)
        except:
            data['error'] = {"code":"decfaild","text":"복호화에 실패하였습니다. 내용을 다시 확인하세요."}
    return response(data)

@app.route('/ratio', methods=['POST'])
def simst():
    rdat = request.form.to_dict()
    if rdat == {}: rdat = request.json
    base = rdat["base"]
    compare = rdat["compare"]

    data = {}
    data['req'] = {'query':{"base":base,"compare":compare}}
    data['api'] = {'version':'1.0','date':'190806'}
    
    data['ratio'] = leven.ratio(base,compare)

    return response(data)


langList = [
    'c',
    'cpp',
    'objective-c',
    'java',
    'kotlin',
    'scala',
    'swift',
    'csharp',
    'go',
    'haskell',
    'erlang',
    'perl',
    'python',
    'python3',
    'ruby',
    'php',
    'bash',
    'r',
    'javascript',
    'coffeescript',
    'vb',
    'cobol',
    'fsharp',
    'd',
    'clojure',
    'elixir',
    'mysql',
    'rust',
    'scheme',
    'commonlisp',
    'plain'
]

aliasLangs = {
    'c++': 'cpp',
    'objc': 'objective-c',
    'c#': 'csharp',
    'python2': 'python',
    'py': 'python3',
    'py2': 'python',
    'py3': 'python3',
    'js': 'javascript',
    'cs': 'csharp',
    'f#': 'fsharp',
    'fs': 'fsharp',
    'sql': 'mysql',
    'lisp': 'commonlisp'
}


@app.route('/eval', methods=['POST'])
def ev():
    global langList
    global aliasLangs
    rdat = request.form.to_dict()
    if rdat == {}: rdat = request.json
    print(rdat)
    code = rdat["code"].replace("\\n","\n")
    lang = rdat["lang"]
    stdin = rdat.get("stdin",[])
    if lang not in langList + list(aliasLangs.keys()):
        logger.warning(f"{lang} is not aviliable on Paiza")
        return response("Unknown Language")
    else:
        if lang in list(aliasLangs.keys()):
            lang = aliasLangs[lang]
        pdat = {
            "source_code": code,
            "language": lang,
            "input": stdin,
            "longpoll": True,
            "longpoll_timeout": 1000,
            "api_key": "guest"
        }
        base = json.loads(requests.post("http://api.paiza.io/runners/create",data=pdat).text)
        if base["status"] != "completed":
            while True:
                check = json.loads(requests.get("http://api.paiza.io/runners/get_details",params={"id":base["id"],"api_key":"guest"}).text)["status"]
                if check == "completed": break
        gdata = json.loads(requests.get("http://api.paiza.io/runners/get_details",params={"id":base["id"],"api_key":"guest"}).text)
        data = {
            "stdout": gdata["stdout"],
            "stderr": gdata["stderr"],
            "exit": gdata["exit_code"],
            "time": gdata["time"]
            }
    return response(json.dumps(data))

@app.route('/lang', methods=['GET','POST'])
def evlang():
    global langList
    global aliasLangs
    return response(json.dumps({"langs":langList,"alias":aliasLangs}))


# @app.route('/<path:ldir>')
# def load(ldir):
#     ldir=re.sub('.*/\.\.(?P<dir>.*)','\g<dir>',ldir)
#     t=ldir if re.match('(.*/)?.*\..*',ldir) else ldir+'index.html' if ldir.endswith('/') else ldir+'/index.html'
#     return send_file(t,'text/css' if t.endswith('.css') else magic.Magic(mime=True).from_file(t))

# @app.route('/')
# def root():
#     return load('index.html')

def ip(): # Based on openNAMU ip_check
    xff = ""
    try:
        temp = request.headers.getlist("X-Forwarded-For")[0]
        temp = temp.split(":") [:-1]
        for t in temp:
            xff += ":" + t
        xff = xff[1:]
        ip = request.environ.get('HTTP_X_REAL_IP', xff)
    except:
        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    # if str(ip) == str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)) or str(ip) == '::1':
    #     ip = 'Reverse Proxy or Local'
    return str(ip)

def response(res):
    if "UptimeRobot" in "{}".format(request.user_agent):
        return res
    if request.method == "GET":
        logger.info("{} got".format(ip()))
    elif request.method == "POST":
        logger.info("{} posted".format(ip()))
    else:
        logger.info("{} accessed with {} request".format(ip(),request.method))
    if request.cookies:
        logger.debug("Cookies : {}".format(request.cookies))
    if request.data:
        logger.debug("Data : {}".format(request.data))
    if request.form:
        logger.debug("Form : {}".format(request.form))
    if request.json:
        logger.debug("Json : {}".format(request.json))
    if request.headers:
        logger.debug("Headers : {}".format(request.json))
    logger.debug("UA : {}".format(request.user_agent))
    if type(res) == dict:
        return json.dumps(res, ensure_ascii=False).encode().decode('utf8')
    elif type(res) == str:
        return res.encode().decode('utf8')

def loop():
    logger.info("Starting up..")
    try:
        app.run(host=config['HOST'],port=config['PORT']);
    except:
        logger.exception("Server crashed!")
        logger.info("Restarting server..")
        loop()
loop()