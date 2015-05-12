#!/usr/bin/env python
# coding=utf-8
from Top_Down_Greedy_Anonymization import Top_Down_Greedy_Anonymization
from utils.read_data import read_data, read_tree
import sys
import pdb
# Poulis set k=25, m=2 as default!

if __name__ == '__main__':
    K = 10
    try:
        K = int(sys.argv[1])
    except:
        pass
    att_trees = read_tree()
    # read record
    data = read_data()
    # remove duplicate items
    print "Begin Partition"
    # anonymized dataset is stored in result
    result = Top_Down_Greedy_Anonymization(att_trees, data, K)
    print "Finish Partition!!"
