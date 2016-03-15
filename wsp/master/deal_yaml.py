# encoding: utf-8

import yaml

class DealYaml(object):

    '''
    处理yaml文件配置
    '''

    def __init__(self):
        pass
    
    def yaml_to_dict(self, filename):
        f = open(filename, 'r')
        dict = yaml.load(f)
        return dict

