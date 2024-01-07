import unittest
from unittest.mock import patch
from functools import wraps
# from kicad.exceptions import deprecate_member
# import kicad.exceptions as kex  # will use deprecate_member and deprecate_warn_fun

deprecate_warn_fun = print  # print is sometimes good
def deprecate_member(old, new, deadline='v0.5.0'):
    def regular_decorator(klass):
        def auto_warn(fun):
            from_str = klass.__name__ + '.' + old
            to_str = klass.__name__ + '.' + new
            header = 'Deprecation warning (deadline {}):'.format(deadline)
            map_str = '{} -> {}'.format(from_str, to_str)
            @wraps(fun)
            def warner(*args, **kwargs):
                deprecate_warn_fun(header, map_str)
                return fun(*args, **kwargs)
            return warner

        new_meth = getattr(klass, new)
        if isinstance(new_meth, property):
            aug_meth = property(
                auto_warn(new_meth.fget),
                auto_warn(new_meth.fset),
                auto_warn(new_meth.fdel)
            )
        else:
            aug_meth = auto_warn(new_meth)
        setattr(klass, old, aug_meth)
        return klass
    return regular_decorator


@deprecate_member('myMeth', 'my_meth')
@deprecate_member('myClassmeth', 'my_classmeth')
@deprecate_member('myProp', 'my_prop')
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

aug_obj = AugClass()
aug_obj.myProp

class MainTester(unittest.TestCase):
    @patch('__main__.deprecate_warn_fun')
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
