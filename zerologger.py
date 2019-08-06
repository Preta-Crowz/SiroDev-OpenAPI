import logging
import raven
import datetime

client = None
logger = None


class TestRaven(Exception):
    def __init__(self):
        self.msg = 'User triggered test_raven function.'
    def __str__(self):
        return self.msg

class NotExist(Exception):
    def __init__(self):
        self.msg = 'Raven client or Logger is not exist.'
    def __str__(self):
        return self.msg



def test_raven():
    global client
    if client != None:
        raise NotExist
    try:
        raise TestRaven
    except TestRaven:
        client.captureException()
        return True



def set_raven(key,secret,project):
    global client
    client = raven.Client('https://{}:{}@sentry.io/{}'.format(key,secret,project))



class Logger:
    def __init__(self,key,secret,project,name=__name__,level=0):
        global client
        set_raven(key,secret,project)
        self._raven = client
        self._logger = logging.Logger(project)
        now = str(datetime.datetime.now())
        date = now[2:10].replace('-','')
        time = now[11:17].replace(':','')
        now = date+'_'+time
        fmt = '[%(levelname)s|%(filename)s] %(funcName)s@%(asctime)s > %(message)s'
        tfm = '%H:%M:%S'
        fmt = '[%(levelname)s|%(filename)s] %(funcName)s@%(asctime)s > %(message)s'
        formatter = logging.Formatter(fmt=fmt,datefmt=tfm)
        file = logging.FileHandler('log/{}_{}.log'.format(name,now))
        file.setLevel(0)
        file.setFormatter(formatter)
        stream = logging.StreamHandler()
        stream.setLevel(0)
        stream.setFormatter(formatter)
        self._logger.addHandler(file)
        self._logger.addHandler(stream)
        self.debug = self._logger.debug
        self.info = self._logger.info
        self.warning = self._logger.warning
        self.log = self._logger.log
        self.error = self._logger.error
        self.info('Logger started')

    def exception(self,msg,*args,**kargs):
        self._raven.captureException()
        self._logger.exception(msg,*args,**kargs)

    def critical(self,msg,*args,**kargs):
        self._raven.captureException()
        self._logger.critical(msg,*args,**kargs)



def get_logger(name=__name__):
    global logger
    if logger == None:
        logger = Logger(__name__)
    return logger