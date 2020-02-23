import queue
import argparse
import threading
import requests
import time
import tqdm

class DirScanGo():
    def __init__(self, Dict_Path, Thread, Url, ip):
        # 初始化
        self.Dict_Path = Dict_Path
        self.Thread = Thread
        self.Url = Url
        self.ip = ip
        self.lock = threading.Lock()
        self.list = []

        # 加载字典
        self.Dict_Content = queue.Queue()
        with open(self.Dict_Path, 'r') as Dict_File:
            for line in Dict_File:
                if line[0] != '/':
                    line = '/'+line
                line=line.strip('\n')   # 这句话极为关键，坑了朕一个小时
                self.Dict_Content.put(line)
        if self.Dict_Content.qsize()<1:
            tqdm.tqdm.write("字典是空的，请确认")
            quit()


        # 设置http请求头
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://www.baidu.com/',
            'X-Forwarded-For': self.ip
        }


    def Scan(self, CurrentUrl):

        Url_Result = 0
        try:
            Url_Result = requests.get(CurrentUrl, headers=self.headers, timeout=60)
        except Exception:
            tqdm.tqdm.write("[error] 出现不明错误。如果大量报错请尝试重新扫描。如果仅报几例错误，则可以忽略。出错的url：{}".format(CurrentUrl))


        if Url_Result != 0 and Url_Result.status_code != 404 and Url_Result.status_code!=403:
            # self.lock.acquire()
            Url_Path = "[{}] {}".format(Url_Result.status_code, CurrentUrl)
            if Url_Path not in self.list:
                tqdm.tqdm.write("[+] {}".format(Url_Path))
                self.list.append(Url_Path)
            # self.lock.release()

        else:
            # tqdm.tqdm.write("{} {}".format(Url_Result.status_code, CurrentUrl))
            pass

    def Go(self):
        temp = self.Dict_Content.qsize()
        for i in tqdm.tqdm(range(temp), leave=False):
        # while not self.Dict_Content.empty():
            self.lock.acquire()
            CurrentUrl = self.Url + self.Dict_Content.get()
            self.lock.release()
            self.Scan(CurrentUrl)
            if i!=0 and i %10000 == 0:
                time.sleep(3)

def main():
    # 生成参数解析器对象
    Parser = argparse.ArgumentParser(description='该工具使用说明如下:')
    Parser.add_argument('-d', '--dict', help='字典路径', default='./dictionaries/c.txt', dest='Dict_Path', metavar='')
    Parser.add_argument('-t', '--thread', help='线程数量', default=30, dest='Thread', type=int, metavar='') # 添加参数
    Parser.add_argument('-u','--url', help='待扫描网站url', required=True, dest='Url', metavar='')
    Parser.add_argument('-i','--ip', help='指定 X-Forwarded-For', dest='ip', metavar='', default='192.168.1.1')
    Arguments = Parser.parse_args()

    DirScanGo_Obj = DirScanGo(Arguments.Dict_Path, Arguments.Thread, Arguments.Url, Arguments.ip)

    # for i in range(Arguments.Thread):
    #     t = threading.Thread(target=DirScanGo_Obj.Go())
    #     t.setDaemon(True)
    #     t.start()
    DirScanGo_Obj.Go()


if __name__ == '__main__':
    main()



