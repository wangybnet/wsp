# coding=utf-8

"""
HTTP Request的meta的内置字段
"""
#
META_PREFIX = "_wsp_"

# WspRequest
WSP_REQUEST = META_PREFIX + "request"
# 重试次数
RETRY_TIMES = META_PREFIX + "retry_times"
# 抓取深度
CRAWL_LEVEL = META_PREFIX + "crawl_level"
