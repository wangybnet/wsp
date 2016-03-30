# coding=utf-8

"""
HTTP Request的meta的内置字段
"""
#
_META_PREFIX = "_wsp_"

# WspRequest
WSP_REQUEST = _META_PREFIX + "request"
# 重试次数
RETRY_TIMES = _META_PREFIX + "retry_times"
# 抓取深度
CRAWL_LEVEL = _META_PREFIX + "crawl_level"
