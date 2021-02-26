import json
import requests
from urllib.parse import urlparse
from urllib.parse import unquote, quote
import aria2c
import os
import configparser

# Define basic information
url = ''
aria2host = "127.0.0.1"
aria2port = "6800"
downloadpath = r'h:\aria2downloads'
user = ''
passwd = ''
aria2session = None
# Number of retry requests
retry = 1


def loadini(path):
    conf = configparser.ConfigParser()
    conf.read(inipath, encoding="utf-8")
    aria2host = conf.get('aria2', 'host')
    aria2port = conf.get('aria2', 'port')
    downloadpath = conf.get('aria2', 'downloadpath')
    aria2session = conf.get('aria2', 'session')
    if (aria2session == ''):
        aria2session = None


def addini(path):
    conf = configparser.ConfigParser()
    conf.add_section("aria2")
    aria2host = input("Please enter aria2 host:")
    conf.set("aria2", "host", aria2host)
    aria2port = input("Please enter aria2 port:")
    conf.set("aria2", "port", aria2port)
    downloadpath = input("Please enter aria2 download path:")
    conf.set("aria2", "downloadpath", downloadpath)
    aria2session = input("Please enter aria2 download session，If the password is not left blank:")
    conf.set("aria2", "session", aria2session)
    if aria2session == '':
        aria2session = None
    conf.write(open(path, 'w', encoding="utf-8"))

    # 判断字符串是否为合法json格式


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


# 递归遍历目录
def ListGoindex(url):
    # 设置请求参数
    d = {
        'page_index': 0
    }
    headers = {'Content-Type': 'multipart/form-data',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    res = None
    # 发送请求
    if user != '' and passwd != '':
        res = requests.post(url=url, data=d, headers=headers, auth=(user, passwd))
    else:
        res = requests.post(url=url, data=d, headers=headers)
    if res.status_code == 200:
        # An error occurred and try again
        i = 0
        while not is_json(res.text) and i != retry:
            i = i + 1
            if user != '' and passwd != '':
                res = requests.post(url=url, data=d, headers=headers, auth=(user, passwd))
            else:
                res = requests.post(url=url, data=d, headers=headers)
    else:
        print("Request error, http status code is："+str(res.status_code))
        print("The error content is："+res.text)
    # 处理返回结果
    res = json.loads(res.text)["data"]["files"]
    # 循环取出结果
    for item in res:
        # 判断是目录递归
        if item["mimeType"] != 'application/vnd.google-apps.folder':
            # 添加到下载器
            # print(url+quote(item["name"],'utf-8'))
            FileDownload(url + quote(item["name"], 'utf-8'))
            print("Add task to aria2，file name："+item["name"])
        else:
            # 取出子路径
            tmp = url + item["name"] + '/'
            ListGoindex(tmp)


def FileDownload(url):
    # 使用的下载器
    aria2(url)


def aria2(url):
    tmp = urlparse(url.replace('/' + url.split('/')[-1], ''))
    tmp = unquote(tmp.path, encoding="utf-8").replace('/0:', '')
    options = {"dir": downloadpath + tmp}
    aria2 = aria2c.Aria2c(host=aria2host, port=aria2port, token=aria2session)
    aria2.addUri(url, options=options)


if __name__ == '__main__':
    # Determine whether the configuration file exists
    curpath = os.path.dirname(os.path.realpath(__file__))
    inipath = os.path.join(curpath, "conf.ini")
    if os.path.exists("conf.ini"):
        loadini(inipath)
    else:
        print("No aria configuration information was found, the configuration will be performed below")
        addini(inipath)
    aria2 = aria2c.Aria2c(host=aria2host, port=aria2port, token=aria2session)
    try:
        aria2ver = aria2.getVer()
        print("The connection to aria2 is successful, the version number of aria2 is:" + aria2ver)
    except:
        print("Unable to connect to aria2")
    weburl = input("Please enter the download URL:\n")
    basicauth = input("If there is basic-auth, please enter y:")
    if basicauth == 'y':
        user = input("Enter your user name:")
        passwd = input("Please enter password:")
    ListGoindex(weburl)
    print("提交成功")
