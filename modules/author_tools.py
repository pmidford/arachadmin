#!/usr/bin/env python
# coding: utf8
from gluon import *

def build_groups(authors):
    groups = []
    for row in authors:
        for group in groups:
            group_head = group[0]
            if (row_match(row,group_head)):
                group.append(row)
                break;
        else:
            groups.append([row])
    for g in groups:
        quality_sort(g)
    return groups

def row_match(current_row,group_head):
    current_last = current_row['last_name']
    current_given = current_row['given_names'][0]
    group_last = group_head['last_name']
    group_given = group_head['given_names'][0]
    return possible_match(current_last,current_given,group_last,group_given)

def possible_match(last1,given1,last2,given2):
    if (last1 != last2):
        return False
    else:
        return (given1[0] == given2[0])

def quality_sort(group):
    group.sort(key=row_key,reverse=True)

def row_key(row):
    return len(row['given_names'])
    

def more_complete_name(last1,given1,last2,given2):
    return (len(given1) > len(given2))
