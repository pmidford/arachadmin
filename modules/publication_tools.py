#!/usr/bin/env python
# coding: utf8
from gluon import *


def citation(row):
    return '%s (%s)' % (row.author_list,row.publication_year)
