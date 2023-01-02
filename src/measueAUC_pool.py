import json
from tqdm import tqdm

import matplotlib.pyplot as plt

import sys

from multiprocessing import Pool, Value, Array

from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score,roc_curve
import time


def mesure(TP,FP,FN,TN):
    acc = (TP+TN)/(TP+FP+FN+TN)
    precision = (TP)/(TP+FP)
    recall = (TP)/(TP+FN)
    f1 = 2*precision*recall/(precision+recall)
    # print('======')
    # print('TP, FN', TP,FN)
    # print('FP, TN', FP,TN)
    # print('acc',acc)
    # print('precision',precision)
    # print('recall',recall)
    # print('f1',f1)
    return acc,precision,recall,f1



def plot_roc_curve(fper, tper):
    plt.plot(fper, tper, color='red', label='ROC')
    plt.plot([0, 1], [0, 1], color='green', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic Curve')
    plt.legend()
    plt.show()


macc = Value('d',-9999999)
max_f1 = Value('d',-999999)
m_precision = Value('d',-999999)
m_recell = Value('d',-999999)
threshod = Value('d',-999999)

mTN =Value('d',0)
mFP =Value('d',0)
mFN =Value('d',0)
mTP =Value('d',0)
test_scores = []

def eval_best(i):
    global macc,max_f1,m_precision,m_recell,threshod,mTN,mFP,mFN,mTP,test_scores,pbar

    y_pred = []
    y_sores = []
    for pre in test_scores:
        plabel = pre[1]
        scores = pre[2]
        y_sores.append(scores)
        if scores> i:
            y_pred.append(1)
        else:
            y_pred.append(0)

    TN, FP, FN, TP = confusion_matrix(y_true, y_pred).ravel()
    acc,precision,recall,f1 = mesure(TP,FP,FN,TN)
    if f1 > max_f1.value:
        with macc.get_lock():
            macc.value = acc
        with max_f1.get_lock():
            max_f1.value = f1
        with m_precision.get_lock():
            m_precision.value = precision
        with m_recell.get_lock():
            m_recell.value = recall
        with threshod.get_lock():
            threshod.value = i
        with mTN.get_lock():
            mTN.value = TN
        with mFP.get_lock():
            mFP.value = FP
        with mFN.get_lock():
            mFN.value = FN
        with mTP.get_lock():
            mTP.value = TP




if __name__ == '__main__':

    # path
    #rel_file = 'log/DeepSAD/BGL_Conv_graph_MLP_mean'
    #rel_file = 'log/DeepSAD/tbird_Conv_graph_MLP_mean_128_maxpool'

    rel_file = sys.argv[1]
    rel_file = rel_file + '/results.json'
    print(rel_file)

    res = ''
    with open(rel_file,'r') as f:
        res = f.read()
    f.close()

    rel_dic = json.loads(res)


    y_pred = []
    y_sores = []
    y_true = []
    for pre in rel_dic['test_scores']:
        idx = pre[0]
        plabel = pre[1]
        scores = pre[2]
        y_sores.append(scores)
        y_true.append(plabel)


    print(len(y_true))
    print(len(y_sores))

    print('roc_auc_score',roc_auc_score(y_true, y_sores))



    fper, tper, thresholds = roc_curve(y_true, y_sores)
    plot_roc_curve(fper, tper)


    test_scores = rel_dic['test_scores']
    
    
    print('starting eval')
    start = time.time()
    
    #with Pool(8) as p:
    #    r = p.map(eval_best, thresholds)
    
    pool = Pool(processes=8)
    mapped_values = list(tqdm(pool.imap_unordered(eval_best, thresholds), total=len(thresholds)))

    end = time.time()
    
    print('finish eval')
    print('eval time: ', end - start)
    print('roc_auc_score',roc_auc_score(y_true, y_sores)) 
    print('===best===')
    print('max_f1', max_f1.value)
    print('m_precision', m_precision.value)
    print('m_recell', m_recell.value)
    print('threshod', threshod.value)
    print('acc', macc.value)
    print('TN,FP,FN,TP=',mTN.value,mFP.value,mFN.value,mTP.value)
