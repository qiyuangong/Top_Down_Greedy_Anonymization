#!/usr/bin/env python
# coding=utf-8


import pdb
from models.numrange import NumRange
from models.gentree import GenTree


__DEBUG = True
gl_QI_len = 10
gl_K = 0
gl_result = []
gl_att_trees = []
gl_QI_range = []
gl_rounds = 3


class Partition:

    """Class for Group, which is used to keep records
    Store tree node in instances.
    self.member: records in group
    self.width: width of this partition on each domain
    self.middle: save the generalization result of this partition
    self.allow: 0 donate that not allow to split, 1 donate can be split
    """

    def __init__(self, data, width, middle):
        """
        initialize with data, width and middle
        """
        self.member = data[:]
        self.width = width[:]
        self.middle = middle[:]
        self.allow = [1] * gl_QI_len


def list_to_str(value_list, cmpfun=cmp, sep=';'):
    """covert sorted str list (sorted by cmpfun) to str
    value (splited by sep). This fuction is value safe, which means
    value_list will not be changed.
    return str list.
    """
    temp = value_list[:]
    temp.sort(cmp=cmpfun)
    return sep.join(temp)


def check_K_anonymity(partition):
    """check if partition satisfy l-diversity
    return True if satisfy, False if not.
    """
    sa_dict = {}
    if isinstance(partition, Partition):
        ltemp = partition.member
    else:
        ltemp = partition
    if len(ltemp) >= gl_K:
        return True
    return False


def NCP(record1, record2):
    pass


def middle(record1, record2):
    pass


def balance():
    pass


def get_pair():
    pass


def cmp_str(element1, element2):
    """compare number in str format correctley
    """
    return cmp(int(element1), int(element2))


def getNormalizedWidth(partition, index):
    """return Normalized width of partition
    similar to NCP
    """
    width = partition.width[index]
    return width * 1.0 / gl_QI_range[index]


def anonymize(partition):
    """
    Main procedure of top_down_greedy_anonymization.
    recursively partition groups until not allowable.
    """
    
    


def Top_Down_Greedy_Anonymization(att_trees, data, K):
    """Mondrian for l-diversity.
    This fuction support both numeric values and categoric values.
    For numeric values, each iterator is a mean split.
    For categoric values, each iterator is a split on GH.
    The final result is returned in 2-dimensional list.
    """
    print "K=%d" % K
    global gl_K, gl_result, gl_QI_len, gl_att_trees, gl_QI_range
    gl_att_trees = att_trees
    middle = []
    gl_QI_len = len(data[0]) - 1
    gl_K = K
    gl_result = []
    result = []
    gl_QI_range = []
    for i in range(gl_QI_len):
        if isinstance(gl_att_trees[i], NumRange):
            gl_QI_range.append(gl_att_trees[i].range)
            middle.append(gl_att_trees[i].value)
        else:
            gl_QI_range.append(gl_att_trees[i]['*'].support)
            middle.append(gl_att_trees[i]['*'].value)
    partition = Partition(data, gl_QI_range[:], middle)
    anonymize(partition)
    ncp = 0.0
    for p in gl_result:
        rncp = 0.0
        for i in range(gl_QI_len):
            rncp += getNormalizedWidth(p, i)
        temp = p.middle
        for i in range(len(p.member)):
            result.append(temp[:])
        rncp *= len(p.member)
        ncp += rncp
    ncp /= gl_QI_len
    ncp /= len(data)
    ncp *= 100
    if __DEBUG:
        print "size of partitions"
        print len(gl_result)
        # print [len(t.member) for t in gl_result]
        print "NCP = %.2f %%" % ncp
        # pdb.set_trace()
    return result
