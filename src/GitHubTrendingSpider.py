# coding:utf-8
import re
import urllib2
import datetime
import os


# https://github.com/trending/python?since=daily
class GithubSpider:
    ls = ["C", "C#", "C++", "Java", "JavaScript", "Kotlin", "Python"]
    nowDate = datetime.datetime.now().strftime('%Y-%m-%d')
    uheaders = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }

    def __init__(self):
        self.switch = True

    def loadpage(self, language):
        self.fileName = "trending/GithubTrending_" + language + "_" + self.nowDate + ".txt"
        if (os.path.exists(self.fileName)):
            os.remove(self.fileName)
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.fileName, "w") as f:
            f.write('语言：%s\n时间：%s\n\n' % (language, nowTime))
        url = "https://github.com/trending/" + language + "?since=daily"
        self.handleHtml(urllib2.urlopen(urllib2.Request(url=url, headers=self.uheaders)).read())

    def handleHtml(self, html):
        p = re.compile('<li class="col-12 d-block width-full py-4 border-bottom" id=".*?">(.*?)</li>', re.S)
        ccc = p.findall(html)
        numb = 0
        for item in ccc:
            numb += 1
            try:
                p_name = re.compile('<a href="/(.*?)">')
                addr = "https://github.com/" + p_name.search(item).group(1)
                p_describe = re.compile('<p class="col-9 d-inline-block text-gray m-0 pr-4">\s*(.*?)\s*</p>')
                dec = p_describe.search(item).group(1)
                p_star = re.compile('<a class="muted-link d-inline-block mr-3".*\s*<svg .*</svg>.*\s*(.*)\s*</a>')
                stars = p_star.search(item).group(1)

            except Exception:
                print "No description"
            finally:
                self.saveTrending(numb, addr, dec, stars)

    def saveTrending(self, numb, addr, dec, stars):
        with open(self.fileName, "a") as f:
            f.write('%s:%s\n  %s\n  stars:%s\n\n' % (numb, addr, dec, stars))

    def startSpide(self):
        while self.switch:
            commond = raw_input("输入1.C.2.C#3.C++.4.Java.5.JavaScript.6.Kotlin.7.Python.爬取对应语言的trending;输入0结束.")
            if (int(commond) > 0):
                print "正在爬取" + self.ls[int(commond) - 1]
                self.loadpage(self.ls[int(commond) - 1])
            else:
                self.switch = False


spider = GithubSpider()
spider.startSpide()
