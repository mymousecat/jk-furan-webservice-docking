#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/21 17:24


def get_next_id(cur_id,test_array):
    test = [x for x in test_array if x > (cur_id if cur_id is not None else 0)]
    test.sort()
    print(test)
    l0 = len(test) - 1
    if l0 == 0:
        return  test[0]
    while l0 > 0:
        if test[l0] - test[0] == l0:
            return test[l0]
        l0 = l0 -1
    return test[0]


if __name__ == '__main__':
    #test_array = [101,35,103,33,102,34,105,100,106,104]
    test_array = [30]
    next_id = get_next_id(30,test_array)
    print(next_id)