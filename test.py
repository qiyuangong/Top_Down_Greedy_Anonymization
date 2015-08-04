import unittest

from top_down_greedy_anonymization import Top_Down_Greedy_Anonymization, Partition
from utils.read_data import read_data, read_tree
from models.gentree import GenTree
from models.numrange import NumRange
from utils.utility import cmp_str
import random

gl_K = 10
gl_rounds = 3
gl_QI_len = 5
gl_QI_range = [10, 10, 10, 10, 9]
# Build a GenTree object
gl_tree_temp = {}
tree = GenTree('*')
gl_tree_temp['*'] = tree
lt = GenTree('1,5', tree)
gl_tree_temp['1,5'] = lt
rt = GenTree('6,10', tree)
gl_tree_temp['6,10'] = rt
for i in range(1, 11):
    if i <= 5:
        t = GenTree(str(i), lt, True)
    else:
        t = GenTree(str(i), rt, True)
    gl_tree_temp[str(i)] = t
gl_att_trees = [gl_tree_temp, gl_tree_temp, gl_tree_temp, gl_tree_temp, NumRange([str(t) for t in range(1, 11)], dict())]
gl_is_cat = [True, True, True, True, False]


def NCP(record):
    r_NCP = 0.0
    for i in range(gl_QI_len):
        if gl_is_cat[i] is False:
            temp = 0
            try:
                float(record[i])
            except:
                stemp = record[i].split(',')
                temp = float(stemp[1]) - float(stemp[0])
            r_NCP += temp * 1.0 / gl_QI_range[i]
        else:
            r_NCP += gl_att_trees[i][record[i]].support * 1.0 / gl_QI_range[i]
    r_NCP /= gl_QI_len
    return r_NCP


def LCA(u, v, index):
    """
    get lowest common ancestor of u, v on generalization hierarchy (index)
    """
    tree_temp = gl_att_trees[index]
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
    with O(n) running tiem; then pick max(v, U2)...after run gl_rounds times.
    the dis(u, v) is nearly max.
    """
    ls = len(member)
    for i in range(gl_rounds):
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


def NCP_dis(record1, record2):
    mid = middle_record(record1, record2)
    return NCP(mid), mid


def middle_record(record1, record2):
    """
    get the generalization result of record1 and record2
    """
    mid = []
    for i in range(gl_QI_len):
        if gl_is_cat[i] is False:
            temp = []
            try:
                float(record1[i])
                temp.append(record1[i])
            except:
                temp.extend(record1[i].split(','))
            try:
                float(record2[i])
                temp.append(record2[i])
            except:
                temp.extend(record2[i].split(','))
            temp.sort(cmp=cmp_str)
            mid.append(temp[0] + ',' + temp[-1])
        else:
            mid.append(LCA(record1[i], record2[i], i))
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

    def test_NCP_with_top_value(self):
        nothing = ['*', '*', '*', '*', '1,10']
        self.assertEqual(NCP(nothing), 1)

    def test_NCP_with_examples(self):
        ex1 = ['1', '1', '1', '1', '1']
        ex2 = ['1,5', '6,10', '2', '2', '2']
        self.assertEqual(NCP(ex1), 0)
        self.assertEqual(NCP(ex2), 0.2)

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
