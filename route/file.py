from flask import request,render_template,redirect,send_file, send_from_directory,url_for,session,make_response
import time
from index import app
import json
import os
import zipfile
import base64
import chardet
import shutil
import traceback
from lib import extract
from config.config import workPath
from .login import cklogin

sep=os.path.sep          #当前系统分隔符
@app.route('/file',methods=['GET','POST'])
@cklogin()
def file():
    return render_template('file.html',nowPath=b64encode_(workPath),sep=b64encode_(sep),workPath=b64encode_(workPath))

#返回文件目录
@app.route('/GetFile',methods=['POST'])
@cklogin()
def GetFile():
    try:
        path = b64decode_(request.form['path']) 
        Files =  sorted(os.listdir(path)) 
        dir_=[]
        file_=[]
        fileQuantity = len(Files)
        for i in Files:
            try:
                i=os.path.join(path, i)
                if not os.path.isdir(i):
                    if os.path.islink(i):
                        fileLinkPath = os.readlink(i)
                        file_.append({
                            'fileName':i,
                            'fileSize':('%.2f' % (os.stat(i).st_size/1024))+'k',
                            'fileOnlyName':os.path.split(i)[1] +'-->'+ fileLinkPath,
                            'fileMODTime':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.stat(i).st_mtime)),
                            'power':oct(os.stat(i).st_mode)[-3:],
                            'fileType':'file'
                            })
                    else:
                        file_.append({
                            'fileName':i,
                            'fileSize':('%.2f' % (os.path.getsize(i)/1024))+'k',
                            'fileOnlyName':os.path.split(i)[1],
                            'fileMODTime':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.stat(i).st_mtime)),
                            'power':oct(os.stat(i).st_mode)[-3:],
                            'fileType':'file'
                            })
                else:
                    dir_.append({
                        'fileName':i,
                        'fileOnlyName':os.path.split(i)[1],
                        'fileSize':('%.2f' % (os.path.getsize(i)/1024 ))+'k',
                        'fileMODTime':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.stat(i).st_mtime)),
                        'power':oct(os.stat(i).st_mode)[-3:],
                        'fileType':'dir'
                        })
            except:
                continue
        returnJson = {
        'path':base64.b64encode(path.encode()).decode(),
        'fileQuantity':fileQuantity,
        'files':dir_ + file_
        }
    except Exception as e:
        return json.dumps({'resultCode':1,'result':str(traceback.format_exc())})
    else:
        return json.dumps({'resultCode':0,'result':returnJson})
#下载
@app.route('/DownFile',methods=['GET','POST'])
@cklogin()
def DownFile():
    fileName = request.values.get('filename')
    fileName = b64decode_(fileName)
    if os.path.isdir(fileName):
        result = zip_(fileList=[fileName],zipPath=os.path.split(fileName)[0])
        if result[0] :
            fileName = result[1] 
        else:
            return json.dumps({'resultCode':1,'fileCode':str(e)})
    response = make_response(send_from_directory(os.path.split(fileName)[0],os.path.split(fileName)[1],as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(fileName.encode().decode('latin-1'))
    return response



#在线编辑
@app.route('/codeEdit',methods=['GET','POST'])
@cklogin()
def codeEdit():
    #前端点击编辑时,传来一个get请求,filename为base64编码的包含路径的文件全名
    fileName = request.values.get('filename',None)
    if fileName:
        return render_template('iframe/codeEdit.html',filename=fileName)
    #返回的网页打开后,自动ajax请求该文件内容
    filename = b64decode_(request.form['path'])
    if os.path.getsize(filename) > 2097152 : return json.dumps({'resultCode':1,'fileCode':'不能在线编辑大于2MB的文件！'});
    with open(filename, 'rb') as f:
        #文件编码,fuck you
        srcBody = f.read()
        char=chardet.detect(srcBody)
        fileCoding = char['encoding']
        if fileCoding == 'GB2312' or not fileCoding or fileCoding == 'TIS-620' or fileCoding == 'ISO-8859-9': fileCoding = 'GBK';
        if fileCoding == 'ascii' or fileCoding == 'ISO-8859-1': fileCoding = 'utf-8';
        if fileCoding == 'Big5': fileCoding = 'BIG5';
        if not fileCoding in ['GBK','utf-8','BIG5']: fileCoding = 'utf-8';
        if not fileCoding:
            fileCoding='utf-8'
        try:
            fileCode = srcBody.decode(fileCoding).encode('utf-8')
        except:
            #这一步说明文件编码不被支持,可以按需修改返回数据
            return json.dumps({'resultCode':0,'fileCode':str(srcBody)})
        else:
            return json.dumps({'resultCode':0,'fileCode':fileCode.decode(),'encoding':fileCoding,'fileName':filename})

#保存编辑后的文件
@app.route('/saveEditCode',methods=['POST'])
@cklogin()
def saveEditCode():
    editValues = b64decode_(request.form['editValues'])
    fileName = b64decode_(request.form['fileName'])
    try:
        with open(fileName,'w',encoding='utf-8') as f:
            f.write(editValues)
    except Exception as e :
        return json.dumps({'resultCode':1,'result':str(e)})
    else:
        return json.dumps({'resultCode':0,'result':'success'})

#删除
@app.route('/Delete',methods=['POST'])
@cklogin()
def Delete():
    fileName = b64decode_(request.values.get('filename'))
    result = delete_(fileName)
    if result[0]:
        return json.dumps({'resultCode':0,'result':'success'})
    else:
        return json.dumps({'resultCode':1,'result':str(result[1])})
        
#修改文件权限
@app.route('/chmod',methods=['POST'])
@cklogin()
def chmod():
    fileName = b64decode_(request.values.get('filename'))
    power = request.values.get('power')
    try:
        os.chmod(fileName,int(power))
    except Exception as e:
        return json.dumps({'resultCode':1,'result':str(e)})
    else:
        return json.dumps({'resultCode':0,'result':'success'})
        

#重命名
@app.route('/RenameFile',methods=['POST'])
@cklogin()
def RenameFile():
    try:
        newFileName = b64decode_(request.values.get('newFileName'))
        oldFileName = b64decode_(request.values.get('oldFileName')) #原文件名,包含路径
        filePath = os.path.split(oldFileName)[0]     #提取路径
        oldFileName = os.path.split(oldFileName)[1]  #原文件名,不包含路径
        if newFileName in os.listdir(filePath):
            return json.dumps({'resultCode':1,'result':'新文件名和已有文件名重复!'})
        else:
            os.rename(os.path.join(filePath,oldFileName),os.path.join(filePath,newFileName))
    except Exception as e:
        return json.dumps({'resultCode':1,'result':str(e)})
    else:
        return json.dumps({'resultCode':0,'result':'success'})

#创建目录
@app.route('/CreateDir',methods=['POST'])
@cklogin()
def CreateDir():
    try:
        dirName = b64decode_(request.values.get('dirName'))
        path = b64decode_(request.values.get('path'))
        if dirName in os.listdir(path):
            return json.dumps({'resultCode':1,'result':'目录已存在'})
        else:
            os.mkdir(os.path.join(path,dirName))
    except Exception as e:
        return json.dumps({'resultCode':1,'result':str(e)})
    else:
        return json.dumps({'resultCode':0,'result':'success'})

#创建文件
@app.route('/CreateFile',methods=['POST'])
@cklogin()
def CreateFile():
    try:
        fileName = b64decode_(request.values.get('fileName'))
        path = b64decode_(request.values.get('path'))
        if fileName in os.listdir(path):
            return json.dumps({'resultCode':1,'result':'文件已存在'})
        else:
            open(os.path.join(path,fileName),'w',encoding='utf-8')
    except Exception as e:
        return json.dumps({'resultCode':1,'result':str(e)})
    else:
        return json.dumps({'resultCode':0,'result':'success'})

#批量操作
@app.route('/batch',methods=['POST'])
@cklogin()
def batch():
    batchType = request.values.get('type')
    selectedListBase64 = json.loads(request.values.get('selectedList'))
    path = b64decode_(request.values.get('path'))
    selectedList = list(b64decode_(i) for i in selectedListBase64)
    if batchType == 'cut':
        return json.dumps({'resultCode':1,'result':'未知请求'})
    elif batchType == 'copy':
        return json.dumps({'resultCode':1,'result':'未知请求'})
    elif batchType == 'delete':
        for i in selectedList:
            result = delete_(i)
            if not result[0] : 
                return json.dumps({'resultCode':1,'result':str(result[1])})
        return json.dumps({'resultCode':0,'result':'success'})
    elif batchType == 'zip':
        result = zip_(fileList=selectedList,zipPath=path)
        if not result[0] : 
            return json.dumps({'resultCode':1,'result':str(result[1])})
        return json.dumps({'resultCode':0,'result':'success'})
    return json.dumps({'resultCode':1,'result':'未知请求'})

#上传文件
@app.route('/UploadFile',methods=['POST'])
@cklogin()
def UploadFile():
    try:
        nowPath =  b64decode_(request.values.get('nowPath'))
        UploadFileContent = request.files['File']
        UploadFileName = UploadFileContent.filename
        UploadFileContent.save(os.path.join(nowPath,UploadFileName))
    except Exception as e :
        return json.dumps({'resultCode':1,'result':str(e)})
    else:
        return json.dumps({'resultCode':0,'result':'success'})

#解压文件
@app.route('/Extract',methods=['POST'])
@cklogin()
def Extract_():
    fileName =  b64decode_(request.values.get('filename'))
    extractResult = extract.main(fileName)
    if extractResult[0]:
        return json.dumps({'resultCode':0,'result':'success'})
    else:
        return json.dumps({'resultCode':1,'result':str(extractResult[1])})






#--------------API---------------#
def delete_(fileName):
    try:
        if os.path.exists(fileName):
            if os.path.isfile(fileName):
                os.remove(fileName)
            else:
                shutil.rmtree(fileName)
        else:
            return [False,"文件或目录不存在"]
    except Exception as e:
        return [False,e]
    else:
        return [True]

def zip_(fileList,zipPath):
    try:
        if len(fileList)>1:
            zipName=os.path.split(zipPath)[1]
        else:
            zipName=os.path.split(fileList[0])[1]
        zipName=('根目录' if zipName == '' else zipName)
        f = zipfile.ZipFile(os.path.join(zipPath,zipName)+'.zip','w',zipfile.ZIP_DEFLATED)
        for i in fileList:
            if os.path.isdir(i):
                for dirpath, dirnames, filenames in os.walk(i):
                    for filename in filenames:
                      f.write(os.path.join(dirpath,filename))
            else:
                f.write(i)
        f.close()
    except Exception as e :
        return [False,e]
    else:
        return [True,os.path.join(zipPath,zipName)+'.zip']
def b64decode_(v):
    try:
        return base64.b64decode(v).decode()
    except:
        #网页传来的base64内容,在被flask捕捉的时候,加号会被解码成空格,导致解码报错
        #这个bug调了我半个小时,我还以为前端js生成的base64有问题,fuck
        return base64.b64decode(v.replace(' ','+')).decode()

def b64encode_(v):
    return base64.b64encode(v.encode()).decode()