#!/usr/bin/env python
# coding=utf-8

# @Article{Xu2006a,
#   Title                    = {Utility-based Anonymization for Privacy Preservation with Less Information Loss},
#   Author                   = {Xu, Jian and Wang, Wei and Pei, Jian and Wang, Xiaoyuan and Shi, Baile and Fu, Ada Wai-Chee},
#   Journal                  = {SIGKDD Explor. Newsl.},
#   Year                     = {2006},
#   Month                    = dec,
#   Number                   = {2},
#   Pages                    = {21--30},
#   Volume                   = {8},
#   Acmid                    = {1233324},
#   Address                  = {New York, NY, USA},
#   Doi                      = {10.1145/1233321.1233324},
#   File                     = {Utility-based Anonymization for Privacy Preservation with Less Information Loss.pdf:All paper\\Utility-based Anonymization for Privacy Preservation with Less Information Loss.pdf:PDF},
#   ISSN                     = {1931-0145},
#   Issue_date               = {December 2006},
#   Keywords                 = {data mining, k-anonymity, local recoding, privacy preservation, utility},
#   Numpages                 = {10},
#   Publisher                = {ACM},
#   Url                      = {http://doi.acm.org/10.1145/1233321.1233324}
# }

import pdb
from models.numrange import NumRange
from models.gentree import GenTree
import operator
import random
import time


__DEBUG = False
gl_QI_len = 5
gl_K = 0
gl_result = []
gl_att_trees = []
gl_QI_range = []
gl_rounds = 3


class Partition:

    """Class for Group, which is used to keep records
    Store tree node in instances.
    self.member: records in group
    self.middle: save the generalization result of this partition
    self.allow: 0 donate that not allow to split, 1 donate can be split
    """

    def __init__(self, data, middle):
        """
        initialize with data and middle
        """
        self.can_split = True
        self.member = data[:]
        self.middle = middle[:]
        self.allow = [1] * gl_QI_len


def NCP(record):
    r_NCP = 0.0
    for i in range(gl_QI_len):
        r_NCP += gl_att_trees[i][record[i]].support * 1.0 / gl_QI_range[i]
    r_NCP /= gl_QI_len
    return r_NCP


def NCP_dis(record1, record2):
    mid = middle_record(record1, record2)
    return NCP(mid), mid


def NCP_dis_merge(partition, addition_set):
    ls = len(addition_set)
    mid = partition.middle
    for i in range(ls):
        mid = middle_record(mid, addition_set[i])
    return NCP(mid), mid


def NCP_dis_group(record, partition):
    """
    compute the NCP of record and partition
    """
    mid = middle_record(record, partition.middle)
    ncp = NCP(mid)
    return (1 + len(partition.member)) * ncp


def middle_record(record1, record2):
    """
    get the generalization result of record1 and record2
    """
    mid = []
    for i in range(gl_QI_len):
        mid.append(LCA(record1[i], record2[i], i))
    return mid


def middle_group(group_set):
    ls = len(group_set)
    mid = group_set[0]
    for i in range(1, ls):
        mid = middle_record(mid, group_set[i])
    return mid


def LCA(u, v, index):
    tree_temp = gl_att_trees[index]
    # don't forget to add themselves (other the level will be higher)
    u_parent = list(tree_temp[u].parent)
    u_parent.insert(0, tree_temp[u])
    v_parent = list(tree_temp[v].parent)
    v_parent.insert(0, tree_temp[v])
    ls = min(len(u_parent), len(v_parent))
    if ls == 0:
        return '*'
    for i in range(ls):
        pos = - 1 - i
        if u_parent[pos] != v_parent[pos]:
            break
        last = pos
    return u_parent[last].value


def get_pair(partition):
    """
    To get max distance pair in partition, we need O(n^2) running time.
    The author proposed a heuristic method: random pick u and get max_dis(u, v)
    with O(n) running tiem; then pick max(v, U2)...after run gl_rounds times.
    the dis(u, v) is nearly max.
    """
    ls = len(partition.member)
    for i in range(gl_rounds):
        if i == 0:
            u = random.randrange(ls)
        else:
            u = v
        max_dis = 0
        max_index = 0
        for i in range(ls):
            if i != u:
                rncp, __ = NCP_dis(partition.member[i], partition.member[u])
                if rncp > max_dis:
                    max_dis = rncp
                    max_index = i
        v = max_index
    return (u, v)


def cmp_str(element1, element2):
    """compare number in str format correctley
    """
    return cmp(int(element1), int(element2))


def distribute_record(u, v, partition):
    """
    Distribute records based on NCP distance.
    records will be assigned to nearer group.
    """
    r_u = partition.member[u][:]
    r_v = partition.member[v][:]
    u_partition = [r_u]
    v_partition = [r_v]
    temp = [item for index, item in enumerate(partition.member) if index not in set([u, v])]
    for t in temp:
        u_dis, __ = NCP_dis(r_u, t)
        v_dis, __ = NCP_dis(r_v, t)
        if u_dis > v_dis:
            v_partition.append(t)
        else:
            u_partition.append(t)
    return [Partition(u_partition, middle_group(u_partition)),
            Partition(v_partition, middle_group(v_partition))]


def balance(sub_partitions, index):
    """
    Two kinds of balance methods.
    1) Move some records from other groups
    2) Merge with nearest group
    The algorithm will choose one of them with minimal NCP
    index store the sub_partition with less than k records
    """
    less = sub_partitions.pop(index)
    more = sub_partitions.pop()
    all_length = len(less.member) + len(more.member)
    require = gl_K - len(less.member)
    # First method
    dist = {}
    for i, t in enumerate(more.member):
        dist[i], __ = NCP_dis(less.middle, t)
    sorted_dist = sorted(dist.iteritems(),
                         key=operator.itemgetter(1))
    nearest_index = [t[0] for t in sorted_dist]
    nearest_index = nearest_index[:require]
    addition_set = [t for i, t in enumerate(more.member) if i in set(nearest_index)]
    remain_set = [t for i, t in enumerate(more.member) if i not in set(nearest_index)]
    first_ncp, first_mid = NCP_dis_merge(less, addition_set)
    first_ncp *= len(addition_set) + len(less.member)
    # Second method
    second_nec, second_mid = NCP_dis(less.middle, more.middle)
    second_nec *= all_length
    if first_ncp < second_nec:
        less.member.extend(addition_set)
        less.middle = first_mid
        sub_partitions.append(less)
        more.member = remain_set
        sub_partitions.append(more)
    else:
        less.member.extend(more.member)
        less.middle = second_mid
        less.can_split = False
    sub_partitions.append(less)


def can_split(partition):
    """
    check if partition can be further splited.
    """
    if partition.can_split is False:
        return False
    if len(partition.member) < 2 * gl_K:
        return False
    return True


def anonymize(partition):
    """
    Main procedure of top_down_greedy_anonymization.
    recursively partition groups until not allowable.
    """
    if can_split(partition) is False:
        gl_result.append(partition)
        return
    u, v = get_pair(partition)
    sub_partitions = distribute_record(u, v, partition)
    if len(sub_partitions[0].member) < gl_K:
        balance(sub_partitions, 0)
    elif len(sub_partitions[1].member) < gl_K:
        balance(sub_partitions, 1)
    for t in sub_partitions:
        anonymize(t)


def Top_Down_Greedy_Anonymization(att_trees, data, K, QI_num=-1):
    """Mondrian for l-diversity.
    This fuction support both numeric values and categoric values.
    For numeric values, each iterator is a mean split.
    For categoric values, each iterator is a split on GH.
    The final result is returned in 2-dimensional list.
    """
    global gl_K, gl_result, gl_QI_len, gl_att_trees, gl_QI_range
    gl_att_trees = att_trees
    middle = []
    if gl_QI_len <= 0:
        gl_QI_len = len(data[0]) - 1
    else:
        gl_QI_len = QI_num
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
    partition = Partition(data, middle)
    start_time = time.time()
    anonymize(partition)
    rtime = float(time.time() - start_time)
    ncp = 0.0
    for p in gl_result:
        rncp = 0.0
        temp = p.middle
        rncp = NCP(temp)
        for i in range(len(p.member)):
            result.append(temp[:])
        rncp *= len(p.member)
        ncp += rncp
    ncp /= len(data)
    ncp *= 100
    if __DEBUG:
        print "K=%d" % K
        print "size of partitions"
        print len(gl_result)
        # print [len(t.member) for t in gl_result]
        print "NCP = %.2f %%" % ncp
        print "Total running time = %.2f" % rtime
        # pdb.set_trace()
    return (result, (ncp, rtime))
