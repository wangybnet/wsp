# coding=utf-8

import re

if __name__ == "__main__":
    htmllist = ["""<body><span ahref="http://www.baidu.com">百度</span></body>""",
                """<body><a class= "href" href ="http://www.baidu.com"   >百度</a></body>""",
                """<body><a  href="http://www.baidu.com" class="href">百度</a></body>""",
                """<body><a type="abc" href =  "http://www.baidu.com" class =   "href"  >百度</a></body>""",
                """<body><a href= 'http://www.baidu.com'>百度</a></body>""",
                """<body><a href=http://www.baidu.com>百度</a></body>"""]
    """
    Case1:
    空

    Case2:
    http://www.baidu.com

    Case3:
    http://www.baidu.com

    Case4:
    http://www.baidu.com

    Case5:
    http://www.baidu.com

    Case6:
    http://www.baidu.com
    """
    i = 0
    for html in htmllist:
        url_list = re.findall(r'<a[\s]*href[\s]*=[\s]*["|\']?(.*?)["|\']?>', html)
        i += 1
        print("Case %d:" % i, url_list)
