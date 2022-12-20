# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 23:40:17 2020

@author: ASUS
"""


import pandas as pd
import numpy as np

s = './80_01_paper/'

logs = pd.read_csv(s+'2020log_0.csv')
for i in range(2,85): # how many ldap log
    tmp = s + '2020log_' + str(i) + '.csv'
    print(tmp)
    try:
        logg = pd.read_csv(tmp)
    except:
        print('error',tmp)
    logs = pd.concat([logs,logg],axis=0)

arr = logs['log'].to_numpy()


with open('2020_3mlogs.txt', 'w') as f:
    for conn in arr:
        f.write(conn)
        f.write('--new_conn--\n')
    
