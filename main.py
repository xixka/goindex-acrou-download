import json
import requests
from urllib.parse import urlparse
from urllib.parse import unquote,quote
import aria2c

#定义基本信息
#网址
weburl = ""
aria2host="127.0.0.1"
aria2port="6800"
downloadpath =r'/root/downloads'
#aria2密码
aria2session= '1'
#aria有密码  #aria2session= '1'   密码为空   aria2session= None


#判断字符串是否为合法json格式
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


#递归遍历目录
def ListGoindex(url):
    #设置请求参数
    d = json.dumps({
    'page_index': 0
    })
    headers = {'Content-Type': 'application/json','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    #发送请求
    res = requests.post(url=url, data=d, headers=headers)
    while not is_json(res.text):
        print("网络波动重新请求")
        res = requests.post(url=url, data=d, headers=headers)
    #处理返回结果
    res=json.loads(res.text)["data"]["files"]
    #循环取出结果
    for item in res:
        #判断是目录递归
        if item["mimeType"] == 'application/vnd.google-apps.folder':
            #取出子路径
            tmp=url+item["name"]+'/'
            ListGoindex(tmp)
        else:
            #添加到下载器
            # print(url+quote(item["name"],'utf-8'))
            FileDownload(url+quote(item["name"],'utf-8'))

def FileDownload(url):
    #使用的下载器
    aria2(url)

print("第一次使用请打开文件配置aria2参数")
print("正在测试aria2链接情况，下面输出aria2版本号即为成功")
aria2 = aria2c.Aria2c(host=aria2host, port=aria2port,token=aria2session)
print("aria2版本号为:"+aria2.getVer())
print("-------------------------")

def aria2(url):
    tmp=urlparse(url.replace('/'+url.split('/')[-1],''))
    tmp=unquote(tmp.path, encoding="utf-8").replace('/0:','')
    options = {"dir": downloadpath+tmp}
    aria2 = aria2c.Aria2c(host=aria2host, port=aria2port,token=aria2session)
    aria2.addUri(url,options=options)

weburl = input("请输入goindex-theme-acrou的网址:\n")
ListGoindex(weburl)

print("提交成功")
