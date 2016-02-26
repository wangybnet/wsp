#!/usr/bin/env python2.7
# encoding: utf-8
import unittest
from add import Add

class TestAdd(unittest.TestCase):
	def test_add(self):
		a = Add()	
		self.assertEquals(a.add(3, 3), 6)


