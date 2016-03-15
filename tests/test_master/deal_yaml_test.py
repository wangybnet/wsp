# encoding: utf-8

import unittest
from wsp.master.deal_yaml import DealYaml

class TestDealYaml(unittest.TestCase):

    def test_yaml_to_dict(self):
        filename = '../../release/etc/master.yaml'
        deal_yaml = DealYaml()
        deal_yaml.yaml_to_dict(filename)