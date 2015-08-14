"""
run top_down_greedy_anonymization with given argv
"""

# !/usr/bin/env python
# coding=utf-8
from top_down_greedy_anonymization import Top_Down_Greedy_Anonymization
from utils.read_adult_data import read_data as read_adult
from utils.read_informs_data import read_data as read_informs
from utils.read_adult_data import read_tree as read_adult_tree
from utils.read_informs_data import read_tree as read_informs_tree
import sys, copy, random
import pdb

DATA_SELECT = 'a'


def get_result_one(att_trees, data, k=10):
    "run Top_Down_Greedy_Anonymization for one time, with k=10"
    print "K=%d" % k
    result, eval_result = Top_Down_Greedy_Anonymization(att_trees, data, k)
    print "NCP %0.2f" % eval_result[0] + "%"
    print "Running time %0.2f" % eval_result[1] + "seconds"


def get_result_k(att_trees, data):
    """
    change K, whle fixing QD and size of dataset
    """
    data_back = copy.deepcopy(data)
    # for K in range(5, 105, 5):
    for k in [2, 5, 10, 25, 50, 100]:
        print '#' * 30
        print "K=%d" % k
        result, eval_result = Top_Down_Greedy_Anonymization(att_trees, data, k)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        print "Running time %0.2f" % eval_result[1] + "seconds"


def get_result_dataset(att_trees, data, k=10, n=10):
    """
    fix k and QI, while changing size of dataset
    n is the proportion nubmber.
    """
    data_back = copy.deepcopy(data)
    length = len(data_back)
    print "K=%d" % k
    joint = 5000
    h = length / joint
    if length % joint == 0:
        h += 1
    for i in range(1, h + 1):
        pos = i * joint
        ncp = rtime = 0
        if pos > length:
            continue
        print '#' * 30
        print "size of dataset %d" % pos
        for j in range(n):
            temp = random.sample(data, pos)
            result, eval_result = Top_Down_Greedy_Anonymization(att_trees, temp, k)
            ncp += eval_result[0]
            rtime += eval_result[1]
            data = copy.deepcopy(data_back)
            # save_to_file((att_trees, temp, result, K, L))
        ncp /= n
        rtime /= n
        print "Average NCP %0.2f" % ncp + "%"
        print "Running time %0.2f" % rtime + "seconds"
        print '#' * 30


def get_result_qi(att_trees, data, k=10):
    """
    change nubmber of QI, whle fixing K and size of dataset
    """
    data_back = copy.deepcopy(data)
    ls = len(data[0])
    for i in reversed(range(1, ls)):
        print '#' * 30
        print "Number of QI=%d" % i
        result, eval_result = Top_Down_Greedy_Anonymization(att_trees, data, k, i)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        print "Running time %0.2f" % eval_result[1] + "seconds"


if __name__ == '__main__':
    FLAG = ''
    LEN_ARGV = len(sys.argv)
    try:
        DATA_SELECT = sys.argv[1]
        FLAG = sys.argv[2]
    except:
        pass
    INPUT_K = 10
    # read record
    if DATA_SELECT == 'i':
        print "INFORMS data"
        DATA = read_informs()
        ATT_TREES = read_informs_tree()
    else:
        print "Adult data"
        DATA = read_adult()
        ATT_TREES = read_adult_tree()
    if FLAG == 'k':
        get_result_k(ATT_TREES, DATA)
    elif FLAG == 'qi':
        get_result_qi(ATT_TREES, DATA)
    elif FLAG == 'data':
        get_result_dataset(ATT_TREES, DATA)
    elif FLAG == '':
        get_result_one(ATT_TREES, DATA)
    else:
        try:
            INPUT_K = int(FLAG)
            get_result_one(DATA, INPUT_K)
        except ValueError:
            print "Usage: python anonymizer [a | i] [k | qi | data]"
            print "a: adult dataset, i: INFORMS ataset"
            print "k: varying k"
            print "qi: varying qi numbers"
            print "data: varying size of dataset"
            print "example: python anonymizer a 10"
            print "example: python anonymizer a k"
    # anonymized dataset is stored in result
    print "Finish Top_Down_Greedy_Anonymization!!"
