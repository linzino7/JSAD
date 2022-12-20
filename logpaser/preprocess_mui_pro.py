# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:48:00 2020

@author: ASUS
"""


import time  
from multiprocessing import Pool     
import pandas as pd  
import re
def pro_str(string):
    if 'conn=' in string:
        #strs = string.split(' ')
        strs = re.findall(r"conn=[0-9]*",string)[0]
        conn = strs.split('=')[1]
        return conn
    else:
        return None


def run(i) :  
    sTime = time.time()  
    collect = {}
    conn = 0
    path = './80_01_paper/ldap.log.'+str(i)
    print('processing...', path)
     
    '''process'''
    with open(path) as f:
        #get first line
        line = f.readline()
        
        while line:
            conn = pro_str(line)
            # # collect log by conn
            if conn != None and conn in collect:

                collect[conn] = collect[conn]+ line

            elif conn != None:
                collect[conn] = line
            #else:
                #print('No conn:'+line)
            line = f.readline()
    f.close()
    
    '''output'''
    a = pd.DataFrame({'id':list(collect.keys()),
                  'log':list(collect.values())})
    a.to_csv('80_01_paper/2020log_'+str(i)+'.csv',index=False)
    

    eTime = time.time()  
    print("one file time :",i, eTime - sTime)  
    
  
if __name__ == "__main__" :  
    startTime = time.time()  
    testFL = list(range(0,90)) # run function 的參數
    pool = Pool() # Pool() 不放參數則默認使用電腦核的數量
    pool.map(run,testFL) 
    pool.close()  
    pool.join()     
    endTime = time.time()  
    print("time :", endTime - startTime)  
