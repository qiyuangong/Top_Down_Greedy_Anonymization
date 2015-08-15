import unittest

from top_down_greedy_anonymization import Top_Down_Greedy_Anonymization, Partition
from utils.read_data import read_data, read_tree
from models.gentree import GenTree
from models.numrange import NumRange
from utils.utility import cmp_str, get_num_list_from_str
import random

GL_K = 10
ROUNDS = 3
QI_LEN = 5
QI_RANGE = [10, 10, 10, 10, 9]
# Build a GenTree object
TREE_TEMP = {}
tree = GenTree('*')
TREE_TEMP['*'] = tree
lt = GenTree('1,5', tree)
TREE_TEMP['1,5'] = lt
rt = GenTree('6,10', tree)
TREE_TEMP['6,10'] = rt
for i in range(1, 11):
    if i <= 5:
        t = GenTree(str(i), lt, True)
    else:
        t = GenTree(str(i), rt, True)
    TREE_TEMP[str(i)] = t
ATT_TREES = [TREE_TEMP, TREE_TEMP, TREE_TEMP, TREE_TEMP, NumRange([str(t) for t in range(1, 11)], dict())]
IS_CAT = [True, True, True, True, False]


def NCP(record):
    """
    compute Certainlty Penalty of records
    """
    record_ncp = 0.0
    for i in range(QI_LEN):
        if IS_CAT[i] is False:
            temp = 0
            try:
                float(record[i])
            except ValueError:
                stemp = record[i].split(',')
                temp = float(stemp[1]) - float(stemp[0])
            record_ncp += temp * 1.0 / QI_RANGE[i]
        else:
            record_ncp += ATT_TREES[i][record[i]].support * 1.0 / QI_RANGE[i]
    return record_ncp


def NCP_dis(record1, record2):
    """
    use the NCP of generalization record1 and record2 as distance
    """
    mid = middle_record(record1, record2)
    return 2 * NCP(mid), mid


def NCP_dis_merge(partition, addition_set):
    """
    merge addition_set to current partition,
    update current partion.middle
    """
    ls = len(addition_set)
    mid = partition.middle
    for i in range(ls):
        mid = middle_record(mid, addition_set[i])
    return (ls + len(partition)) * NCP(mid), mid


def LCA(u, v, index):
    """
    get lowest common ancestor of u, v on generalization hierarchy (index)
    """
    tree_temp = ATT_TREES[index]
    # don't forget to add themselves (other the level will be higher)
    u_parent = list(tree_temp[u].parent)
    u_parent.insert(0, tree_temp[u])
    v_parent = list(tree_temp[v].parent)
    v_parent.insert(0, tree_temp[v])
    ls = min(len(u_parent), len(v_parent))
    if ls == 0:
        return '*'
    last = -1
    for i in range(ls):
        pos = - 1 - i
        if u_parent[pos] != v_parent[pos]:
            break
        last = pos
    return u_parent[last].value


def get_pair(member):
    """
    To get max distance pair in partition, we need O(n^2) running time.
    The author proposed a heuristic method: random pick u and get max_dis(u, v)
    with O(n) running tiem; then pick max(v, U2)...after run ROUNDS times.
    the dis(u, v) is nearly max.
    """
    ls = len(member)
    for i in range(ROUNDS):
        if i == 0:
            u = random.randrange(ls)
        else:
            u = v
        max_dis = 0
        max_index = 0
        for i in range(ls):
            if i != u:
                rncp, __ = NCP_dis(member[i], member[u])
                if rncp > max_dis:
                    max_dis = rncp
                    max_index = i
        v = max_index
    return (u, v)


def middle_record(record1, record2):
    """
    get the generalization result of record1 and record2
    """
    mid = []
    for i in range(QI_LEN):
        if IS_CAT[i] is False:
            temp = []
            temp.extend(get_num_list_from_str(record1[i]))
            temp.extend(get_num_list_from_str(record2[i]))
            temp.sort(cmp=cmp_str)
            if temp[0] == temp[-1]:
                mid.append(temp[0])
            else:
                mid.append(temp[0] + ',' + temp[-1])
        else:
            mid.append(LCA(record1[i], record2[i], i))
    return mid


def middle_group(group_set):
    """
    get the generalization result of the group
    """
    ls = len(group_set)
    mid = group_set[0]
    for i in range(1, ls):
        mid = middle_record(mid, group_set[i])
    return mid


class functionTest(unittest.TestCase):
    def test_LCA_equal(self):
        v1 = '1'
        v2 = '1'
        self.assertEqual(LCA(v1, v2, 1), '1')

    def test_LCA_not_equal(self):
        v1 = '1'
        v2 = '6'
        self.assertEqual(LCA(v1, v2, 1), '*')

    def test_LCA_with_top(self):
        v1 = '*'
        v2 = '6'
        self.assertEqual(LCA(v1, v2, 1), '*')

    def test_middle(self):
        r1 = ['1', '1', '1', '1', '2,4']
        r2 = ['2', '6', '1', '1', '1,5']
        self.assertEqual(middle_record(r1, r2), ['1,5', '*', '1', '1', '1,5'])

    def test_NCP_with_top_value(self):
        nothing = ['*', '*', '*', '*', '1,10']
        self.assertEqual(NCP(nothing), 5.0)

    def test_NCP_with_examples(self):
        ex1 = ['1', '1', '1', '1', '1']
        ex2 = ['1,5', '6,10', '2', '2', '2']
        self.assertEqual(NCP(ex1), 0)
        self.assertEqual(NCP(ex2), 1.0)

    def test_middle_group_equal(self):
        group = [['2', '2', '2', '2', '2'],
                 ['2', '2', '2', '2', '2'],
                 ['2', '2', '2', '2', '2'],
                 ['2', '2', '2', '2', '2'],
                 ['2', '2', '2', '2', '2']]
        self.assertEqual(middle_group(group), ['2', '2', '2', '2', '2'])

    def test_middle_group_different(self):
        group = [['2', '2', '1', '2', '2'],
                 ['2', '2', '2', '2', '2'],
                 ['2', '2', '2', '2', '2'],
                 ['6', '2', '2', '2', '2'],
                 ['2', '2', '2', '2', '2']]
        self.assertEqual(middle_group(group), ['*', '2', '1,5', '2', '2'])

    def test_get_pair(self):
        member = [['1', '1', '10', '10', '1'],
                  ['1', '3', '4', '2', '1'],
                  ['2', '2', '2', '2', '2'],
                  ['2', '2', '2', '2', '2'],
                  ['2', '2', '2', '2', '2'],
                  ['2', '2', '2', '2', '2'],
                  ['10', '10', '10', '10', '10']]
        print get_pair(member), '==(6, 1)'


if __name__ == '__main__':
    unittest.main()
