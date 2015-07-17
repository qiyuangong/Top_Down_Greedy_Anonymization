import unittest

from top_down_greedy_anonymization import Top_Down_Greedy_Anonymization
from utils.read_data import read_data, read_tree


class SizeTest(unittest.TestCase):
    gl_K = 10
    att_trees = read_tree()
    data = read_data()

    def subSizeTest(self):
        # num = int(len(data) * scale * 1.0 / 100)
        with self.assertRaises(Exception):
            Top_Down_Greedy_Anonymization(att_trees, data[0:3000], gl_K)


if __name__ == '__main__':
    unittest.main()
