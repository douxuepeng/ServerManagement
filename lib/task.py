import datetime
import threading
import subprocess
import time

class taskset():
    def __init__(self):
        self.taskList=[]

    def TaskFunc(self,data):
        if data not in self.taskList:
            return True
        self.taskList.remove(data)
        subprocess.Popen(data['value'])
        interval = self.GetNextTaskSenc(data)
        data['nextRunTime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()+int(interval)))
        self.taskList.append(data)
        timer = threading.Timer(interval, self.TaskFunc,(data,))
        timer.start()
    def CreatTask(self,data):
        interval = self.GetNextTaskSenc(data)
        data['nextRunTime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()+int(interval)))
        self.taskList.append(data)
        timer = threading.Timer(interval, self.TaskFunc,(data,))
        timer.start()
    def GetTaskList(self):
        return self.taskList
    def DeleteTask(self,taskID):
        for i in self.taskList:
            if i['taskID'] == taskID:
                self.taskList.remove(i)
    def GetNextTaskSenc(self,data):
        if data['type'] == 'senc':
            return int(data['senc'])
            #设定周期不为秒的话,计算出下一次执行是几天之后
        elif data['type'] == 'day' :
            now_time = datetime.datetime.now()
            next_time = now_time + datetime.timedelta(days=1)
        elif data['type'] == 'week' :
            if str(data['week']) not in list(str(i) for i in range(0,8)):
                raise ValueError('日期设定错误,星期数值应在1-7内!')
            now_time = datetime.datetime.now()
            tip = 1  #从第二天计算,避免设定周几和今天相同,产生循环
            while True:
                next_time = now_time + datetime.timedelta(days=tip)
                if next_time.strftime('%w') == data['week']:
                    break
                else:
                    tip+=1
            next_time = now_time + datetime.timedelta(days=tip)
        elif data['type'] == 'month' :
            if str(data['day']) not in list(str(i) for i in range(1,32)):
                raise ValueError('日期设定错误,日期数值应在1-31内!')
            now_time = datetime.datetime.now()
            tip = 1 
            while True:
                next_time = now_time + datetime.timedelta(days=tip)
                if str(next_time.day) == str(data['day']):
                    break
                else:
                    tip+=1
            next_time = now_time + datetime.timedelta(days=tip)
        else:
            raise ValueError('无法解析下次执行的日期,请检查设定时间格式!')
        #下次执行任务的时间
        next_year = next_time.date().year
        next_month = next_time.date().month
        next_day = next_time.date().day
        try:
            #根据下次运行的时间,计算出秒数
            next_time = datetime.datetime.strptime(f'{next_year}-{next_month}-{next_day} {data["hour"]}:{data["mint"]}:{data["senc"]}', "%Y-%m-%d %H:%M:%S")
            timer_start_time = (next_time - now_time).total_seconds()
        except :
            raise ValueError('请检查时间格式!')
        return (int(timer_start_time)+1 if (timer_start_time//1 > 0) else int(timer_start_time)) #向上取整,只有这一个需求,懒得用math.ceil