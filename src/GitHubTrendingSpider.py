# coding:utf-8
import re
import threading
from Queue import Queue
import requests
import datetime
import os

SPIDER_EXIT = False
HANDLE_EXIT = False


class SpiderThread(threading.Thread):  # 采集线程
    def __init__(self, threadName, languageQueue, dataQueue):
        super(SpiderThread, self).__init__()
        self.threadName = threadName
        self.languageQueue = languageQueue
        self.dataQueue = dataQueue

    def run(self):
        while not SPIDER_EXIT:
            try:
                language = self.languageQueue.get(False)
                url = "https://github.com/trending/" + language + "?since=daily"
                print "正在爬取" + language
                content = requests.get(url=url).text.encode("utf-8")
                self.dataQueue.put({language: content})
            except:
                pass


class HandleThread(threading.Thread):  # 解析线程
    def __init__(self, threadName, dataQueue, queueLock):
        super(HandleThread, self).__init__()
        self.threadName = threadName
        self.dataQueue = dataQueue
        self.queueLock = queueLock

    def run(self):
        while not HANDLE_EXIT:
            try:
                content = self.dataQueue.get(False)
                self.handle_html(content)
            except:
                pass

    def handle_html(self, content):
        for language in content:
            fileName = "trending/GithubTrending_" + language + "_" + datetime.datetime.now().strftime(
                '%Y-%m-%d') + ".txt"
            html = content[language]
            if (os.path.exists(fileName)):
                os.remove(fileName)
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(fileName, "w") as f:
                f.write('语言：%s\n时间：%s\n\n' % (language, now_time))

        p = re.compile('<li class="col-12 d-block width-full py-4 border-bottom" id=".*?">(.*?)</li>', re.S)
        ccc = p.findall(html)
        numb = 0
        dec = 'No description'
        print "正在保存" + fileName
        for item in ccc:
            numb += 1
            try:
                p_name = re.compile('<a href="/(.*?)">')
                addr = "https://github.com/" + p_name.search(item).group(1)
                p_star = re.compile('<a class="muted-link d-inline-block mr-3".*\s*<svg .*</svg>.*\s*(.*)\s*</a>')
                stars = p_star.search(item).group(1)
                p_describe = re.compile('<p class="col-9 d-inline-block text-gray m-0 pr-4">\s*(.*?)\s*</p>')
                dec = p_describe.search(item).group(1)
            except Exception:
                print "No description"
            finally:
                self.queueLock.acquire()
                self.save_trending(fileName, numb, addr, dec, stars)
                self.queueLock.release()

    def save_trending(self, fileName, numb, addr, dec, stars):
        with open(fileName, "a") as f:
            f.write('%s:%s\n  %s\n  stars:%s\n\n' % (numb, addr, dec, stars))


class GithubSpider:
    languages = ["C", "C#", "C++", "Java", "JavaScript", "Kotlin", "Python"]
    nowDate = datetime.datetime.now().strftime('%Y-%m-%d')
    uheaders = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }

    def __init__(self):
        self.switch = True
        self.languageQueue = Queue(7)
        self.contentQueue = Queue()
        self.fileName = ''

    def loadpage(self, language):
        self.fileName = "trending/GithubTrending_" + language + "_" + self.nowDate + ".txt"
        if (os.path.exists(self.fileName)):
            os.remove(self.fileName)
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.fileName, "w") as f:
            f.write('语言：%s\n时间：%s\n\n' % (language, now_time))
        url = "https://github.com/trending/" + language + "?since=daily"
        self.handle_html(requests.get(url=url).text.encode("utf-8"))

    def handle_html(self, html):
        p = re.compile('<li class="col-12 d-block width-full py-4 border-bottom" id=".*?">(.*?)</li>', re.S)
        ccc = p.findall(html)
        numb = 0
        dec = 'No description'
        stars = ''
        for item in ccc:
            numb += 1
            try:
                p_name = re.compile('<a href="/(.*?)">')
                addr = "https://github.com/" + p_name.search(item).group(1)
                p_star = re.compile('<a class="muted-link d-inline-block mr-3".*\s*<svg .*</svg>.*\s*(.*)\s*</a>')
                stars = p_star.search(item).group(1)
                p_describe = re.compile('<p class="col-9 d-inline-block text-gray m-0 pr-4">\s*(.*?)\s*</p>')
                dec = p_describe.search(item).group(1)
            except Exception:
                print "No description"
            finally:
                self.save_trending(numb, addr, dec, stars)

    def save_trending(self, numb, addr, dec, stars):
        with open(self.fileName, "a") as f:
            f.write('%s:%s\n  %s\n  stars:%s\n\n' % (numb, addr, dec, stars))

    def start_multi_thread(self):  # 多线程爬虫;
        thread_names = ["采集线程1", "采集线程2", "采集线程3", "采集线程4", "采集线程5"]
        handle_names = ["解析线程1", "解析线程2", "解析线程3", "解析线程4", "解析线程5"]
        threads = []
        threadsH = []
        queueLock = threading.Lock()

        for lan in self.languages:
            self.languageQueue.put(lan)
        for thread_name in thread_names:
            thread = SpiderThread(thread_name, self.languageQueue, self.contentQueue)
            thread.start()
            threads.append(thread)
        for thread_name in handle_names:
            thread = HandleThread(thread_name, self.contentQueue, queueLock)
            thread.start()
            threadsH.append(thread)

        while not self.languageQueue.empty():
            pass
        global SPIDER_EXIT
        SPIDER_EXIT = True
        for thread in threads:
            thread.join()

        while not self.contentQueue.empty():
            pass
        global HANDLE_EXIT
        HANDLE_EXIT = True
        for thread in threadsH:
            thread.join()

    def start_spider(self):
        while self.switch:
            commond = raw_input("输入1.C;2.C#;3.C++;4.Java;5.JavaScript;6.Kotlin;7.Python;a.以上全部.爬取对应语言的trending;输入0结束.")
            if (str(commond) == "a"):
                global SPIDER_EXIT
                SPIDER_EXIT = False
                global HANDLE_EXIT
                HANDLE_EXIT = False
                self.start_multi_thread()

            elif (int(commond) > 0):
                print "正在爬取" + self.languages[int(commond) - 1]
                self.loadpage(self.languages[int(commond) - 1])
            else:
                self.switch = False


if __name__ == "__main__":
    spider = GithubSpider()
    spider.start_spider()
