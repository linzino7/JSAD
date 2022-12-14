#from curses import window
from torch.utils.data import Dataset
from tqdm import tqdm

import os
import torch




def read_file(path, rm_id = True):
  '''read hdfs files from disk 
  , split logs  ;=> split label,
  format is  
  22 5 5 5 11 9 11 9 26 26 11 9 26\t1

  return "22 5 5 5 11 9 11 9 26 26 11 9 26" , 1
  '''
  datas = []
  with open(path,'r') as f:
    for line in f:
      # LDAP remove id
      if rm_id:
        id = line.split()[0]
        line = line.replace(id+" ","",1)

      tmp = line.split("\t")

      # if don't give a label
      if len(tmp)<2:
          tmp.append(0)
      
      a = len(tmp[0].split(" "))
      datas.append((tmp[0],int(tmp[1])))
      

  return datas

def logkey_to_int_graph(logkey, JH_length, windows=64, JH=True, topN=True):
    '''
    preprocessing log key.
    P represent the probability by joint histogram.
    K′ represent the first n log keys of a log sequence with the length
    logkey: parsed log key sequences.
    JH: if true than return P and K'. Otherwise only return k'
    '''

    length = JH_length  #mean 32*32 #  HDFS 64 #BGL 128 
    #windows = 64

    tmp = logkey.strip().split(" ")
    getint = [int(i) for i in tmp]
    if topN:
        # K′:  the first n log keys of a log sequence with the length
        top_64_arr = []
        if len(getint) >= windows:
            top_64_arr = getint[0:windows]
        else:
            top_64_arr = getint.copy()
            while len(top_64_arr)< windows:
                top_64_arr.append(-1)

        top_64 = torch.tensor(top_64_arr, dtype=torch.float32)
    
    # P: probability by joint histogram
    if JH:
        # create 2d list by length
        tmp_arr = [[0 for i in range(length)] for i in range(length)]

        for i in range(len(getint)-2): # next 2 
            f = getint[i] 
            t1 = getint[i+1] # next 1
            if f > (length-2) or t1 > (length-2):
                continue

            if f<(length-1)   and t1< (length-1):
                tmp_arr[f-1][t1-1] +=1
            else:
                # print strange log key
                print('t1,f = ',t1,f,' longer than length')

        if getint[-1]< (length-2):
            tmp_arr[getint[-1]][length-1] +=1

        tensor_2d = torch.tensor(tmp_arr, dtype=torch.float32)
        tensor_2d = tensor_2d / len(getint)
        #tensor_2d = torch.log1p(tensor_2d / len(getint)) #meaN
        
        # tensor_2d = tensor_2d / len(getint) #meaN
        # #t = torch.log(torch.zeros(length, length, dtype=torch.float32)+0.5 )
        # #t = torch.zeros(length, length, dtype=torch.float32)+0.5
        #one = torch.tensor(1,dtype=torch.float32)
        #tensor_2d = torch.where(tensor_2d!=0.0, tensor_2d, one)
        # #tensor_2d = torch.log(tensor_2d)/t
        #tensor_2d = torch.log(tensor_2d)


    if JH and topN:
        return tensor_2d, top_64
    elif JH and not topN:
        return tensor_2d
    else:
        return top_64
    
     

    
        

class graphseqLogsDataset(Dataset):
    """
    LogDataset class for log dataset which preprocess by Drain3

    Dataset class with additional targets for the semi-supervised setting and modification of __getitem__ method
    to also return the semi-supervised target as well as the index of a data sample.
    """


    def __init__(self, root: str, dataset_name: str, net_name:str, train=True, random_state=None):
        super(Dataset, self).__init__()

        self.classes = [0, 1]

        self.root = root
        self.dataset_name = dataset_name
        self.train = train  # training set or test set
        
        if net_name==0: # user don't give the net_name in baseline method
            self.JH = False
        elif "MIMO" in net_name or "onlycon" in net_name:
            self.JH = True
        else:
            self.JH = False

        if net_name==0: # user don't give the net_name in baseline method
            self.topN = True
        elif "onlycon" in net_name:
            self.topN = False
        else:
            self.topN = True
        
        if net_name==0:
            self.windows = 64
        elif "_w32" in net_name:
            self.windows = 32
        elif "_w128" in net_name:
            self.windows = 128
        elif "_w512" in net_name:
            self.windows = 512
        elif "_w1024" in net_name:
            self.windows = 1024
        else:
            self.windows = 64
        
        train_files = {
            'LDAP':'ldap_train_label_id_0_1',
            'HDFS':'hdfs_train_labl',
            'BGL':'BGL_train_idx_lab_128'
        }

        test_files = {
            'LDAP':'ldap_test_id_0_1',
            #'LDAP':'logkeys_cross_1022add80_rmdate_with_id_0_1_RR_UP1024_random',
            #'LDAP':'logkeys_cross_1022add80_rmdate_with_id_0_1_RR_UP1024_random_0001',
            #'LDAP':'logkeys_cross_1022add80_rmdate_with_id_0_1_RR_UP1024_r_0001_1024added_3wad2',
            # 'LDAP' :'logkeys_cross_1022add80_rmdate_with_id_0_1_RR_r_0001_1024added_3wad2_U10W',
            'HDFS':'hdfs_test_labl',
            'BGL':'BGL_test_idx_lab_128',
            #'BGL':'BGL_test_idx_lab_128_up10k' 
        }
        
        JH_length = {
            'LDAP': 32,
            'HDFS': 64,
            'BGL': 128
        }

        rm_id = {
            'LDAP': True,
            'HDFS': False,
            'BGL': False
        }

        # load data  

        if self.train:
            train_file = read_file(root+'/'+dataset_name+'/'+train_files[dataset_name], rm_id[dataset_name])
            
            X_train = [ logkey_to_int_graph(X, JH_length[dataset_name], self.windows, self.JH, self.topN) for X, y in train_file]
            y_train = [ y for X, y in train_file]
            
            self.data = X_train
            self.targets = torch.tensor(y_train, dtype=torch.int64)
        else:
            test_file = read_file(root+'/'+dataset_name+'/'+test_files[dataset_name], rm_id[dataset_name])

            X_test = []
            for X, y in tqdm(test_file):
                X_test.append(logkey_to_int_graph(X, JH_length[dataset_name], self.windows, self.JH, self.topN))
            y_test = [y for X, y in test_file]
             
            self.data = X_test 
            self.targets = torch.tensor(y_test, dtype=torch.int64)

        self.semi_targets = torch.zeros_like(self.targets)

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target, semi_target, index)
        """
        sample, target, semi_target = self.data[index], int(self.targets[index]), self.semi_targets[index]

        return sample, target, semi_target, index

    def __len__(self):
        return len(self.data)

    def _check_exists(self):
        return os.path.exists(self.data_file)

    def replace_target(self, normal):
        tmp_arr = []
        for i in self.targets:
            if i in normal:
                tmp_arr.append(0)
            else:
                tmp_arr.append(1)
        self.targets = tmp_arr
        
