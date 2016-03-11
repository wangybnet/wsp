# coding=utf-8

import re
import pickle
html = """<a   href="http://historylist/%E7%BB%B4%E5%9F%BA%E7%99%BE%E7%A7%91/106382" class="nslog:1021" target="_blank">历史版本</a>"""
#list = re.findall(r'<a[\s]*href="(.*?)">',html)
url =  """https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=56060048_4_pg&wd=startswith&oq=python%26lt%3B.5%20urlopen%20import&rsv_pq=898ff26a00002912&rsv_t=8c4a5G9kUGJKgvt5x2mIrgD9bH3BRfu2EaInbtLRYgCLVD0OIHgKGvXY6ymnrYQHFR0orQ&rsv_enter=1&inputT=5137&rsv_sug3=95&rsv_sug1=40&rsv_sug7=100&bs=python3.5%20urlopen%20import"""
list = url.__contains__('http')
print(list)
print('123'+'456')


class Profile:
    name = "AlwaysJane"

profile = Profile()
pickledclass = pickle.dumps(profile)
print (pickledclass)
print (pickle.loads(pickledclass))

