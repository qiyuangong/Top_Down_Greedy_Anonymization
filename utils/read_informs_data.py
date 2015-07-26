#!/usr/bin/env python
# coding=utf-8

# Read data and read tree fuctions for INFORMS data
# user att ['DUID', 'PID', 'DUPERSID', 'DOBMM', 'DOBYY', 'SEX', 'RACEX', 'RACEAX', 'RACEBX', 'RACEWX', 'RACETHNX', 'HISPANX', 'HISPCAT', 'EDUCYEAR', 'Year', 'marry', 'income', 'poverty']
# condition att ['DUID', 'DUPERSID', 'ICD9CODX', 'year']
from models.gentree import GenTree
from models.numrange import NumRange
import pickle
import pdb


__DEBUG = False
gl_user_att = ['DUID', 'PID', 'DUPERSID', 'DOBMM', 'DOBYY', 'SEX',
               'RACEX', 'RACEAX', 'RACEBX', 'RACEWX', 'RACETHNX',
               'HISPANX', 'HISPCAT', 'EDUCYEAR', 'Year', 'marry', 'income', 'poverty']
gl_condition_att = ['DUID', 'DUPERSID', 'ICD9CODX', 'year']
# Only 5 relational attributes and 1 transaction attribute are selected (according to Poulis's paper)
gl_att_list = [3, 4, 6, 13, 16]
gl_is_cat = [True, True, True, True, True]


def cmp_str(element1, element2):
    """compare number in str format correctley
    """
    return cmp(int(element1), int(element2))


def read_tree():
    """read tree from data/tree_*.txt, store them in att_tree
    """
    att_names = []
    att_trees = []
    for t in gl_att_list:
        att_names.append(gl_user_att[t])
    for i in range(len(att_names)):
        if gl_is_cat[i]:
            att_trees.append(read_tree_file(att_names[i]))
        else:
            att_trees.append(read_pickle_file(att_names[i]))
    return att_trees


def read_pickle_file(att_name):
    """
    read pickle file for numeric attributes
    return numrange object
    """
    try:
        static_file = open('data/adult_' + att_name + '_static.pickle', 'rb')
        (numeric_dict, sort_value) = pickle.load(static_file)
    except:
        print "Pickle file not exists!!"
    static_file.close()
    result = NumRange(sort_value, numeric_dict)
    return result


def read_tree_file(treename):
    """read tree data from treename
    """
    leaf_to_path = {}
    att_tree = {}
    prefix = 'data/informs_'
    postfix = ".txt"
    treefile = open(prefix + treename + postfix, 'rU')
    att_tree['*'] = GenTree('*')
    if __DEBUG:
        print "Reading Tree" + treename
    for line in treefile:
        # delete \n
        if len(line) <= 1:
            break
        line = line.strip()
        temp = line.split(';')
        # copy temp
        temp.reverse()
        for i, t in enumerate(temp):
            isleaf = False
            if i == len(temp) - 1:
                isleaf = True
            # try and except is more efficient than 'in'
            try:
                att_tree[t]
            except:
                att_tree[t] = GenTree(t, att_tree[temp[i - 1]], isleaf)
    if __DEBUG:
        print "Nodes No. = %d" % att_tree['*'].support
    treefile.close()
    return att_tree


def read_data(flag=0):
    """
    read microda for *.txt and return read data
    """
    data = []
    userfile = open('data/demographics.csv', 'rU')
    conditionfile = open('data/conditions.csv', 'rU')
    userdata = {}
    numeric_dict = []
    for i in range(gl_att_list):
        numeric_dict.append(dict())
    # We selet 3,4,5,6,13,15,15 att from demographics05, and 2 from condition05
    print "Reading Data..."
    for i, line in enumerate(userfile):
        line = line.strip()
        # ignore first line of csv
        if i == 0:
            continue
        row = line.split(',')
        row[2] = row[2][1:-1]
        try:
            userdata[row[2]].append(row)
        except:
            userdata[row[2]] = [row]
    conditiondata = {}
    for i, line in enumerate(conditionfile):
        line = line.strip()
        # ignore first line of csv
        if i == 0:
            continue
        row = line.split(',')
        row[1] = row[1][1:-1]
        row[2] = row[2][1:-1]
        try:
            conditiondata[row[1]].append(row)
        except:
            conditiondata[row[1]] = [row]
        for i in range(len(gl_att_list)):
            index = gl_att_list[i]
            if gl_is_cat[i] == False:
                try:
                    numeric_dict[i][row[index]] += 1
                except:
                    numeric_dict[i][row[index]] = 1
    hashdata = {}
    for k, v in userdata.iteritems():
        if __DEBUG and len(v) > 1:
            # check changes on QIDs excluding year(2003-2005)
            for i in range(len(gl_user_att)):
                # year index = 14
                if i == 14:
                    continue
                s = set()
                for j in range(len(v)):
                    s.add(v[j][i])
                if len(s) > 1:
                    print gl_user_att[i], s
                    # pdb.set_trace()
        if k in conditiondata:
            # ingnore duplicate values
            temp = set()
            for t in conditiondata[k]:
                temp.add(t[2])
            hashdata[k] = []
            for i in range(len(gl_att_list)):
                index = gl_att_list[i]
                # we assume that QIDs are not changed in dataset
                hashdata[k].append(v[0][index])
            stemp = list(temp)
            # sort values
            stemp.sort()
            hashdata[k].append(stemp[:])
    for k, v in hashdata.iteritems():
        data.append(v)
    for i in range(len(gl_att_list)):
        if gl_is_cat[i] == False:
            static_file = open('data/informs_' + gl_att_names[gl_att_list[i]] + '_static.pickle', 'wb')
            sort_value = list(numeric_dict[i].keys())
            pickle.dump((numeric_dict[i], sort_value), static_file)
            static_file.close()

    userfile.close()
    conditionfile.close()
    return data
