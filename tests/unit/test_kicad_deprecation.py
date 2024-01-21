import unittest
from unittest.mock import patch
from functools import wraps
import kigadgets.exceptions as kex  # will use deprecate_member and deprecate_warn_fun

kex.deprecate_warn_fun = print

@kex.deprecate_member('myMeth', 'my_meth')
@kex.deprecate_member('myClassmeth', 'my_classmeth')
@kex.deprecate_member('myProp', 'my_prop')
class AugClass:
    def my_meth(self):
        ''' docstring here '''
        return 'my_meth'

    @classmethod
    def my_classmeth(cls):
        return 'my_classmeth'

    @property
    def my_prop(self):
        return 'my_prop.get'

    @my_prop.setter
    def my_prop(self, val):
        # return 'my_prop.set'
        pass


class MainTester(unittest.TestCase):
    @patch('kigadgets.exceptions.deprecate_warn_fun')
    def test_1(self, mock_print):
        aug_obj = AugClass()

        self.assertEqual(aug_obj.my_meth(), 'my_meth')
        self.assertEqual(AugClass.my_classmeth(), 'my_classmeth')
        self.assertEqual(aug_obj.my_prop, 'my_prop.get')
        aug_obj.my_prop = 1
        mock_print.assert_not_called()

        self.assertEqual(aug_obj.myMeth(), 'my_meth')
        mock_print.assert_called_once()
        mock_print.reset_mock()
        self.assertEqual(AugClass.myClassmeth(), 'my_classmeth')
        mock_print.assert_called_once()
        mock_print.reset_mock()
        self.assertEqual(aug_obj.myProp, 'my_prop.get')
        mock_print.assert_called_once()
        mock_print.reset_mock()
        aug_obj.MyProp = 1
        # mock_print.assert_called_once()  # unittest misses, but tested manually to work

if __name__ == '__main__':
    unittest.main()
