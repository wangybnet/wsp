from Operation import Operation
import unittest
class testOperation(unittest.TestCase):
    def testProduct(self):
        op = Operation()
        self.assertEqual(op.product(2,3),6)
        self.assertEqual(op.product(0,7),0)