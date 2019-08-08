# -*- coding: utf-8 -*-

import json
config = json.load(open("config.json"))

import zerologger as zlog
logger = zlog.Logger(config["RAVEN"]["KEY"],config["RAVEN"]["SECRET"],config["RAVEN"]["PROJECT"],config["APPNAME"],config["LOG"])

from flask import Flask,render_template,request,send_file
logger.debug("flask imported")
import Levenshtein as leven
logger.debug("Levenshtein imported")
try:
    from winmagic import magic
except:
    import magic
logger.debug("magic imported")
import base64
logger.debug("base64 imported")
import time
logger.debug("time imported")
import re
logger.debug("re imported")
import requests
logger.debug("requests imported")
import socket
logger.debug("socket imported")
import urllib3
logger.debug("urllib3 imported")
import execjs
logger.debug("execjs imported")
logger.info(f"execjs started with {execjs.get().name}")
import ast
logger.debug("ast imported")


import squarecrypt as sqc
logger.debug("squarecrypt imported")

logger.info("Setting up application")
app = Flask(config["APPNAME"])

import logging
logging.getLogger('werkzeug').setLevel(-100)
logger.debug("Flask logging disabled")

url = [
    # {'code':'kkr','name':'끄투코리아','url':'https://kkutu.co.kr/'},
    {'code':'com','name':'끄투닷컴','url':'http://kkutu.club/'},
    {'code':'han','name':'끄투한국','url':'https://kkutu.cc/'},
    {'code':'pkt','name':'프로젝트 끄투','url':'https://prjkt.online/'},
    {'code':'bfk','name':'BF끄투','url':'https://bfk.playts.net/'},
    {'code':'mdk','name':'모두끄투','url':'https://modukkutu.kro.kr/'},
    {'code':'nbk','name':'나비끄투','url':'https://nabitu.ze.am/'},
    {'code':'k25','name':'끄투25시','url':'http://kt24.playts.net/'}
]

@app.route('/', methods=['GET'])
def help():
    return response(render_template("index.html"))



@app.route('/urls', methods=['GET', 'POST'])
def urls():
    global url
    data = {}
    data['api'] = {'date':'190806'}
    data["url"] = url
    return response(data)



@app.route('/word', methods=['POST'])
def get_word():
    rdat = request.form.to_dict()
    if rdat == {}: rdat = request.json
    word = rdat["word"]
    lms = rdat.get('listing', '0')
    start = time.time()
    global url
    data = {}
    
    if lms != '0' and lms != '1':
        return response('<h3>대신 FFF를 드립니다.</h3><iframe width="560" height="315" src="https://www.youtube.com/embed/Vo5WvNfOuAM" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>')

    if re.match("[a-zA-Z0-9 ]*",word)[0] == word:
        lang = "en"
    elif re.match("[ㄱ-ㅣ가-힣0-9 ]*",word)[0] == word:
        lang = "ko"
    else:
        lang = "nul"
    data['req'] = {'word':word,'lang':lang,'server':'all'}
    data['api'] = {'version':'1.0','date':'190806'}
    if lang == 'nul':
        data['error'] = {"code":"unk_lang","text":"언어 인식에 실패하였습니다. 단어를 맞게 입력했는지 확인하시고, 해당 현상이 지속되면 관리자에게 문의하세요."}
        return response(data)

    for sv in url:
        # print('word : {}/{}'.format(sv["code"],word))
        cfail = False
        try:
            r = requests.get(sv["url"]+'dict/{}?lang={}'.format(word,lang),timeout=1)
        except requests.exceptions.Timeout:
            data[sv["code"]] = {'responce':'nul','error':{'code':'timedout','text':'서버 연결에 실패했습니다. 서버 응답이 늦거나, 서버가 오프라인입니다.'}}
            cfail = True
        except Exception as e:
            data[sv["code"]] = {'responce':'nul','error':{'code':'unk_conn','text':'서버 연결에 실패했습니다. 원인 추적에 실패하였습니다.','exception':{'name':str(e),'traceback':str(e.with_traceback(None))}}}
            cfail = True
        if cfail: continue

        if r.status_code == 200:
            svd = json.loads(r.text)
        else:
            svd = {'responce':r.status_code}
        if 'word' in svd: svd.pop('word')
        if 'error' in svd:
            svd['responce'] = svd.pop('error')
        else:
            svd['responce'] = 200
        if svd['responce'] == 404:
            svd['error'] = {'code':'notfound','text':'없는 단어입니다.'}
            data[sv["code"]] = svd
            continue
        elif svd['responce'] == 400:
            svd['error'] = {'code':'badreque','text':'권한이 없습니다.'}
            data[sv["code"]] = svd
            continue

        if lms == '1':
            svd['theme'] = svd['theme'].split(",")
            svd['type'] = svd['type'].split(",")
            if sv["code"] == 'han':
                svd['mean'] = [[re.split("\＂\d*\＂",svd['mean'])[1:]]]
            else:
                mean = svd['mean']
                mean = re.split("\＂\d*\＂",mean)[1:]
                tmp1 = []
                final = []
                for m in mean:
                    tmp1 = (re.split("\［\d*\］",m)[1:])
                    tmp2 = []
                    for t in tmp1:
                        tmp2.append(re.split("\（\d*\）",t)[1:])
                    final.append(tmp2)
                svd['mean'] = final
        data[sv["code"]] = svd

    data['api']['responce_time'] = time.time() - start
    return response(data)



@app.route('/status', methods=['GET', 'POST'])
def get_info():
    start = time.time()
    global url
    data = {}
    data['api'] = {'version':'1.0','date':'190806'}

    for sv in url:
        print('info : {}'.format(sv['code']))
        cfail = False
        try:
            r = requests.get(sv['url']+'servers',timeout=1)
        except requests.exceptions.Timeout:
            data[sv["code"]] = {'responce':'nul','error':{'code':'timedout','text':'서버 연결에 실패했습니다. 서버 응답이 늦거나, 서버가 오프라인입니다.'}}
            cfail = True
        except Exception as e:
            data[sv["code"]] = {'responce':'nul','error':{'code':'unk_conn','text':'서버 연결에 실패했습니다. 원인 추적에 실패하였습니다.','exception':{'name':str(e),'traceback':str(e.with_traceback(None))}}}
            cfail = True
        if cfail: continue

        if r.status_code == 200:
            svd = json.loads(r.text)
        else:
            svd = {'responce':r.status_code}
        if 'error' in svd:
            svd['responce'] = svd.pop('error')
        else:
            svd['responce'] = 200
        if svd['responce'] == 404:
            svd['error'] = {'code':'notfound','text':'없는 페이지입니다.'} # 출력될 일이 없어야한다.
            data[sv["code"]] = svd
            continue
        elif svd['responce'] == 400:
            svd['error'] = {'code':'badreque','text':'권한이 없습니다.'} # 아마 이 것도 출력 될 일이 없을 것이다.
            data[sv["code"]] = svd
            continue
        svd['all'] = {'current':0,'max':0}
        for sl in svd['list']:
            if sl == None:
                continue
            svd['all']['current'] += sl
            svd['all']['max'] += svd['max']
        data[sv["code"]] = svd

    data['api']['responce_time'] = time.time() - start
    return response(data)



@app.route('/starts', methods=['POST'])
def starts():
    rdat = request.form.to_dict()
    if rdat == {}: rdat = request.json
    query = rdat["query"]
    data = {}
    if re.match("[a-zA-Z0-9 ]*",query)[0] == query:
        lang = "en"
    elif re.match("[ㄱ-ㅣ가-힣0-9 ]*",query)[0] == query:
        lang = "ko"
    else:
        lang = "nul"
    data['req'] = {'query':query,'lang':lang}
    data['api'] = {'version':'1.0','date':'190806'}
    if lang == 'nul':
        data['error'] = {"code":"unk_lang","text":"언어 인식에 실패하였습니다. 단어를 맞게 입력했는지 확인하시고, 해당 현상이 지속되면 관리자에게 문의하세요."}
        return response(data)
    r = requests.get(f"https://prjkt.online/starts/{query}?lang={lang}",timeout=1)
    if r.status_code == 200:
        rdat = json.loads(r.text)
    code = r.status_code
    if code == 400:
        data['error'] = {'code':'badreque','text':'권한이 없습니다.'} # 아마 이 것도 출력 될 일이 없을 것이다.
        data['list'] = []
    else:
        data['list'] = rdat
    return response(data)

@app.route('/ends', methods=['POST'])
def ends(query):
    rdat = request.form.to_dict()
    if rdat == {}: rdat = request.json
    query = rdat["query"]
    data = {}
    if re.match("[a-zA-Z0-9 ]*",query)[0] == query:
        lang = "en"
    elif re.match("[ㄱ-ㅣ가-힣0-9 ]*",query)[0] == query:
        lang = "ko"
    else:
        lang = "nul"
    data['req'] = {'query':query,'lang':lang}
    data['api'] = {'version':'1.0','date':'190806'}
    if lang == 'nul':
        data['error'] = {"code":"unk_lang","text":"언어 인식에 실패하였습니다. 단어를 맞게 입력했는지 확인하시고, 해당 현상이 지속되면 관리자에게 문의하세요."}
        return response(data)
    r = requests.get(f"https://prjkt.online/ends/{query}?lang={lang}",timeout=1)
    if r.status_code == 200:
        rdat = json.loads(r.text)
    code = r.status_code
    if code == 400:
        data['error'] = {'code':'badreque','text':'권한이 없습니다.'} # 아마 이 것도 출력 될 일이 없을 것이다.
        data['list'] = []
    else:
        data['list'] = rdat
    return response(data)



@app.route('/sqc/encode', methods=['POST'])
def sqcEncode(query):
    rdat = request.form.to_dict()
    if rdat == {}: rdat = request.json
    query = rdat["query"]
    data = {}
    data['req'] = {'query':query}
    data['api'] = {'version':'1.0','date':'190806'}
    data['res'] = sqc.crypt(query)
    return response(data)

@app.route('/sqc/decode', methods=['POST'])
def sqcDecode(query):
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

# Disabled until V2
# @app.route('/eval', methods=['POST'])
# def ev():
#     rdat = request.form.to_dict()
#     if rdat == {}: rdat = request.json
#     print(rdat)
#     code = rdat["code"].replace("\\n","\n")
#     lang = rdat["lang"]
#     if lang not in ["js","py"]:
#         logger.log(f"{lang} is not aviliable")
#         return response("Unknown Language")
#     elif lang == "js":
#         try:
#             code = base64.b64encode(code.encode("raw_unicode_escape"))
#             code = eval("\"" + str(code)[2:-1] + "\"")
#             ctx = execjs.compile(f"dec=require(\"Base64\").atob;delete require;x=Function(dec(\"{code}\"));delete dec")
#             data = ctx.call("x")
#             logger.info(code)
#             logger.info(data)
#         except execjs._exceptions.ProgramError as e:
#             e = str(e).replace("\\n","\n")
#             logger.error(e)
#             return response(e)
#         except execjs._exceptions.ProcessExitedWithNonZeroStatus as e:
#             logger.error(e.stderr)
#             return response(e.stderr)
#     elif lang == "py":
#         try:
#             tree = ast.parse(code)
#             eval_expr = ast.Expression(tree.body[-1].value)
#             exec_expr = ast.Module(tree.body[:-1])
#             exec(compile(exec_expr,'file','exec'),{})
#             data = eval(compile(eval_expr,'file','eval'),{})
#             data = str(data)
#         except Exception as e:
#             logger.error(e)
#             return response(str(e))
#     else:
#         return "Unknown Error"

#     return response(json.dumps(data))


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