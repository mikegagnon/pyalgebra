#!/usr/bin/env python
#
# This is free and unencumbered software released into the public domain.
#
# Inspiration from https://github.com/twitter/algebird
#
# Example usage:
#   
#   plus(1, 2) == 3
#   plus({"a": 1}, {"a": 2}) == {"a": 3}
#
#   More complex usage examples in "__main__"
#

__MONOIDS__ = {}

def getMonoid(x, y = None, monoids = __MONOIDS__):
    if y == None:
        typ = type(x)
        if typ not in monoids:
            raise ValueError("%s does not have an associated monoid" % x)
        return monoids[typ]
    else:
        xMonoid = getMonoid(x, None, monoids)
        yMonoid = getMonoid(y, None, monoids)
        if xMonoid != yMonoid:
            xMonStr = str(x)[:80]
            yMonStr = str(y)[:80]
            raise ValueError(("Cannot get monoid for \n%s\n---and---\n%s\n" +
                "because they don't have the same monoid") % (xMonStr, yMonStr))
        return xMonoid

class Monoid(object):
    def isNonZero(self, v):
        return self.zero() != v

class IntMonoid(Monoid):
    def zero(self): return 0
    def plus(self, x, y, monoids = None): return x + y
__MONOIDS__[int] = IntMonoid()

# Warning: plus modifies either x or y (whichever is bigger)
class DictMonoid(Monoid):
    def zero(self): return {}
    def plus(self, x, y, monoids = __MONOIDS__):
        if len(x) > len(y):
            bigger, smaller = x, y
            bigOnLeft = True
        else:
            bigger, smaller = y, x
            bigOnLeft = False
        for k, v in smaller.iteritems():
            if k not in bigger:
                bigger[k] = v
            else:
                if bigOnLeft:
                    left = bigger[k]
                    right = v
                else:
                    left = v
                    right = bigger[k]

                subMonoid = getMonoid(left, right, monoids)
                newV = subMonoid.plus(left, right, monoids)
                if subMonoid.isNonZero(newV):
                    bigger[k] = newV
                else:
                    del bigger[k]
        return bigger
__MONOIDS__[dict] = DictMonoid()

class ListMonoid(Monoid):
    def zero(self): return []
    def plus(self, x, y, monoids = None): return x + y
__MONOIDS__[list] = ListMonoid()

class SetMonoid(Monoid):
    def zero(self): return set()
    def plus(self, x, y, monoids = None): return x | y
__MONOIDS__[set] = SetMonoid()

def plus(x, y, monoids = __MONOIDS__):
    monoid = getMonoid(x, y, monoids)
    return monoid.plus(x, y, monoids)

def total(items, monoids = __MONOIDS__):
    if len(items) == 0:
        return None
    else:
        total = items[0]
        for item in items[1:]:
            total = plus(total, item, monoids)
        return total

    
if __name__ == "__main__":
    assert 3 == plus(1, 2)
    assert [1,2,3] == plus([1], [2, 3])
    assert set([1,2,3]) == plus(set([1, 2]), set([2, 3]))
    assert {"a": 3} == plus({"a": 1}, {"a": 2})
    assert {"a": 3, 0:1} == plus({"a": 1, 0:1}, {"a": 2})
    assert {"a": 3, 0:1} == plus({"a": 1}, {"a": 2, 0:1})
    assert {"a": [1,2,3], "b": 1} == plus(
        {
            "a": [1,2],
            "b": 1
        },
        {
            "a": [3]
        })
    assert {"a": [1,2,3], "b": 1} == plus(
        {
            "a": [1],
        },
        {
            "a": [2,3],
            "b": 1
        })

    left = {
        "a": 1,
        "b": ["x", "y", "z"],
        "c": {
            "a": set([1,2,3]),
            "b": 1
        },
        "q": 3,
        "x": 5
    }

    right = {
        "a": 3,
        "b": [1,2,3],
        "c": {
            "a": set([1,2,5,6]),
            "b": 7,
            "d": 3
        },
        "p": 5,
        "x": -5
    }

    combined = {
        "a": 4,
        "b": ["x", "y", "z", 1, 2, 3],
        "c": {
            "a": set([1,2,3,5,6]),
            "b": 8,
            "d": 3
        },
        "q": 3,
        "p": 5
    }

    assert plus(left, right) == combined

    assert None == total([])
    assert 1 == total([1])
    assert [1,2,3,4,5] == total([[1], [2,3], [4,5]])

    import copy
    monoids = copy.deepcopy(__MONOIDS__)
    class MockIntMonoid(Monoid):
        def zero(self): return 0
        def plus(self, x, y, monoids = None): return x - y
    monoids[int] = MockIntMonoid()
    assert {"a": 3} == plus({"a": 1}, {"a": 2})
    assert {"a": -1} == plus({"a": 1}, {"a": 2}, monoids)
