import sqlite3
import os
import time,json
import datetime
class sqlClass(object):
    def __new__(cls):
        if not hasattr(cls,'instance'):
            cls.instance = super(sqlClass,cls).__new__(cls)
        return cls.instance
    def __init__(self):
        self.createSystemInfo()
    def createSystemInfo(self):
        logDB = 'log.db'
        sqlpath=(os.path.dirname(os.path.realpath(__file__)))
        if logDB in os.listdir(sqlpath):
            self.con = sqlite3.connect(os.path.join(sqlpath,logDB),check_same_thread = False)
        else:
            self.con = sqlite3.connect(os.path.join(sqlpath,logDB),check_same_thread = False)
            self.con.execute('''CREATE TABLE SYSTEMINFO 
                (INFO    TEXT,
                TIM      NUMBER
                );''')
            self.con.execute('''CREATE TABLE RemoteHost 
                (IP           TEXT,
                PORT          TEXT,
                CTYPE         TEXT,
                USERNAME      TEXT,
                PWD           TEXT,
                PKPATH        TEXT,
                GROUPS        TEXT,
                NOTE          TEXT,
                CARETETIME    TEXT,
                ROOTPWD       TEXT
                );''')
    def getTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    #----------------------系统资源统计--------------------
    #写入系统信息
    def insertInfo(self,info):
        info = json.dumps(info)
        self.con.execute("INSERT INTO SYSTEMINFO (INFO,TIM) VALUES (?,?)",(info,self.getTime()))
        self.con.commit()
    #查询记录的信息
    def selectInfo(self,day):
        try:
            date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-(int(day) * 86400)))
            resultData = self.con.execute('SELECT * FROM SYSTEMINFO WHERE TIM > (?)',(date,)).fetchall()
            result = [True,resultData]
        except Exception as e:
            result = [False,str(e)]
        return result
    #删除过期数据
    def deleteInfo(self,day):
        date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-(int(day) * 86400)))
        self.con.execute('DELETE FROM SYSTEMINFO WHERE TIM < (?)',(date,))
        self.con.commit()

    #----------------------远程主机--------------------
    #新建主机
    def insertRemoteHost(self,IP,PORT,CTYPE,USERNAME,GROUPS,NOTE,ROOTPWD,PWD=None,PKPATH=None):
        print(IP)
        try:
            self.con.execute("INSERT INTO RemoteHost (IP,PORT,CTYPE,USERNAME,PWD,PKPATH,GROUPS,NOTE,CARETETIME,ROOTPWD) VALUES (?,?,?,?,?,?,?,?,?,?)",(IP,PORT,CTYPE,USERNAME,PWD,PKPATH,GROUPS,NOTE,self.getTime(),ROOTPWD))
            self.con.commit()
        except Exception as e:
            return [False,str(e)]
        else:
            return [True]
    #查询全部主机
    def selectRemoteHost(self):
        try:
            resultData = self.con.execute('SELECT IP,PORT,USERNAME,GROUPS,NOTE,CARETETIME FROM RemoteHost').fetchall()
            result = [True,resultData]
        except Exception as e:
            result = [False,str(e)]
        return result
    #删除主机记录
    def deleteRemoteHost(self,IP):
        try:
            self.con.execute('DELETE FROM RemoteHost WHERE IP = (?)',(IP,))
            self.con.commit()
        except Exception as e:
            result = [False,str(e)]
        else:
            result = [True]
        return result
    #按照IP查询主机
    def selectRemoteHostForIP(self,IP):
        try:
            resultData = self.con.execute('SELECT IP,PORT,USERNAME,PWD,ROOTPWD FROM RemoteHost WHERE IP = (?)',(IP,)).fetchall()[0]
            result = [True,resultData]
        except Exception as e:
            result = [False,str(e)]
        return result