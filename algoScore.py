__author__ = 'Debasish'

import csv
import datetime
import sys, os

from dateutil import parser
from collections import Counter
import pandas as pd
import numpy as np
from sklearn.metrics import *
from ggplot import *

from balanceIt import connect_db

def transform_col(col1, col2, diff_val):
    print len(col1), len(col2), "Transform COl"
    print type(col1[0])
    err_ind = []
    col1 = [int(i) for i in col1]
    for i in range(len(col1)):
        if col1[i] == 1:
            if col1[i+1] == 1:
                print "Skipped"
                if col1[i-1] == 0:
                    print col1[i]
                    err_ind.append(i)
                continue
            else:
                if col1[i-1] == 0:
                    err_ind.append(i)
        else:
            err_ind.append(i)
        #print i, col1[i]
    err_col = []
    pred_col = []
    for j in range(len(err_ind)):
        err_col.append(col1[err_ind[j]])
        pred_col.append(col2[err_ind[j]])
    print "Length of modified columns :",len(err_col), len(pred_col)
    print set(err_col), set(pred_col)
    return err_col, pred_col

def create_file(file):
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))


def get_value(date, shift_value, col_name,table):
    db = connect_db()
    end_time = date
    e_time = parser.parse(end_time)
    s_time = e_time - datetime.timedelta(minutes=5*shift_value)
    start_time = "'"+s_time.strftime("%Y-%m-%d %H:%M:%S")+"'"
    end_time = "'"+e_time.strftime("%Y-%m-%d %H:%M:%S")+"'"
    sql = 'SELECT {} FROM {} WHERE `timestamp` >= {} AND `timestamp` < {}'.format(col_name, table, start_time, end_time)
    c = db.cursor()
    c.execute(sql)
    values = c.fetchall()
    # print values
    # print sql
    return values

class fileReader:

    def __init__(self, fname, date, table):
        self.file = fname
        self.dataset = self.read_file()
        self.table = table
        self.date = date
        #return self.dataset

    def file_buffer(self):
        lines = csv.reader(open(self.file, "rt"))
        return lines

    def read_file(self):
        dataset = list(self.file_buffer())
        return dataset

    def get_columns(self):
        tse_col = []
        error_col = []
        fut_err = {}
        fut_err_prob = {}
        e5 = []
        e10 = []
        e15 = []
        e20 = []
        e25 = []
        e30 = []
        p_e5 = []
        p_e10 = []
        p_e15 = []
        p_e20 = []
        p_e25 = []
        p_e30 = []
        for i in range(1,len(self.dataset)):
            if self.dataset[i][0] >= self.date:
                tse_col.append(self.dataset[i][0])
                error_col.append(self.dataset[i][1])
                e5.append(self.dataset[i][2])
                e10.append(self.dataset[i][3])
                e15.append(self.dataset[i][4])
                e20.append(self.dataset[i][5])
                e25.append(self.dataset[i][6])
                e30.append(self.dataset[i][7])
                p_e5.append(self.dataset[i][8])
                p_e10.append(self.dataset[i][9])
                p_e15.append(self.dataset[i][10])
                p_e20.append(self.dataset[i][11])
                p_e25.append(self.dataset[i][12])
                p_e30.append(self.dataset[i][13])

        fut_err['e_5'] = e5
        fut_err['e_10'] = e10
        fut_err['e_15'] = e15
        fut_err['e_20'] = e20
        fut_err['e_25'] = e25
        fut_err['e_30'] = e30

        fut_err_prob['e_5'] = p_e5
        fut_err_prob['e_10'] = p_e10
        fut_err_prob['e_15'] = p_e15
        fut_err_prob['e_20'] = p_e20
        fut_err_prob['e_25'] = p_e25
        fut_err_prob['e_30'] = p_e30

        return tse_col, error_col, fut_err, fut_err_prob

    def get_rows(self, row_num = -1):
        if row_num == -1:
            return self.dataset
        elif row_num>=0:
            return self.dataset[row_num]

    def transform_col(self, col1, col2, col2_name, shift_value = 0,col='err'):
        if shift_value == 0:
            return col1, col2
        elif 'p' not in col:
            val = []
            new_col2 = []
            values = get_value(self.date, shift_value, col2_name, self.table)
            # print col1
            # print values
            for value in values:
                val.append(value[0])
            print len(val)
            #for i in range(len(val)):
                #new_col2.append(val[i])
            #print new_col2
            for i in range(len(col2)):
                new_col2.append(col2[i])
            print "Length of newcol2",len(new_col2)
            col2 = new_col2[:-1*len(val)]
            print "Length of col2",len(col2)
            val1 = col1
            print "Length of val``",len(val1)
            col1 = val1[shift_value:]
            print "Length of col1",len(col1)
            # print "Column 2 :",col2
            # print "Values ",val
            return col1, col2
        elif 'p' in col:
            val = []
            new_col2 = []
            col_dict = {'e_5':8,'e_10': 9, 'e_15': 10,'e_20' : 11, 'e_25': 12,'e_30': 13}
            for key, value in col_dict.iteritems():
                if key == col2_name:
                    col_num = value
            data = self.dataset
            start_date = self.date
            tse_col, error_col, fut_err, fut_err_prob = self.get_columns()
            err_prob = fut_err_prob[col2_name]
            for i in range(1,len(tse_col)-shift_value):
                if tse_col[i+shift_value] >= start_date:
                    new_col2.append(data[i][col_num])
            #col2 = new_col2[:-1*shift_value]
            #print col2
            return col2


def algo_score(fname, date, table):

    fileName = os.getcwd() + '\\oob\\31_05\\max_feature_sqrt\\manual_balance_class\\output_100tree.txt'
    print(fileName)
    create_file(fileName)
    f = open(fileName, 'w')
    print "11"
    #sys.stdout = f
    print "File name for data : ", fname
    file = fileReader(fname, date, table)
    dataset = file.read_file()
    print("Length of dataset", len(dataset))
    e_col = []
    auc = {}
    err = ['e_5', 'e_10', 'e_15', 'e_20', 'e_25', 'e_30']

    tse_col, error_col, fut_err, fut_err_prob = file.get_columns()
    # print len(error_col), len(fut_err['e_5'])
    err_col_e5, n_e5 = file.transform_col(error_col, fut_err['e_5'], 'e_5', 1)
    # print n_e5
    err_col_e10, n_e10 = file.transform_col(error_col, fut_err['e_10'], 'e_10', 2)
    err_col_e15, n_e15 = file.transform_col(error_col, fut_err['e_15'], 'e_15', 3)
    err_col_e20, n_e20 = file.transform_col(error_col, fut_err['e_20'], 'e_20', 4)
    err_col_e25, n_e25 = file.transform_col(error_col, fut_err['e_25'], 'e_25', 5)
    err_col_e30, n_e30 = file.transform_col(error_col, fut_err['e_30'], 'e_30', 6)
    
    n_pe5 = file.transform_col(error_col, fut_err_prob['e_5'], 'e_5', 1,'prob')
    n_pe10 = file.transform_col(error_col, fut_err_prob['e_10'], 'e_10', 2,'prob')
    n_pe15 = file.transform_col(error_col, fut_err_prob['e_15'], 'e_15', 3,'prob')
    n_pe20 = file.transform_col(error_col, fut_err_prob['e_20'], 'e_20', 4,'prob')
    n_pe25 = file.transform_col(error_col, fut_err_prob['e_25'], 'e_25', 5,'prob')
    n_pe30 = file.transform_col(error_col, fut_err_prob['e_30'], 'e_30', 6,'prob')
    print len(n_e5), len(n_pe30), len(error_col)
    
    for i in range(len(n_pe5)):
        e_col.append(int(error_col[i]))
        # print len(n_pe5)
        #print(n_pe5[i])
        n_pe5[i] = float(n_pe5[i])
        n_pe10[i] = float(n_pe10[i])
        n_pe15[i] = float(n_pe15[i])
        n_pe20[i] = float(n_pe20[i])
        n_pe25[i] = float(n_pe25[i])
        n_pe30[i] = float(n_pe30[i])

        #n_e5[i] = str(n_e5[i])
        #n_e10[i] = str(n_e10[i])
        #n_e15[i] = str(n_e15[i])
        #n_e20[i] = str(n_e20[i])
        #n_e25[i] = str(n_e25[i])
        #n_e30[i] = str(n_e30[i])
    for e_val in err:
        if e_val == 'e_5':
            pred_prob_col = n_pe5
            err_col, pred_col = transform_col(err_col_e5, n_e5, diff_val=1)
        elif e_val == 'e_10':
            pred_prob_col = n_pe10
            pred_col = n_e10
            err_col = err_col_e10
        elif e_val == 'e_15':
            pred_prob_col = n_pe15
            pred_col = n_e15
            err_col = err_col_e15
            print "Length Pred_col",len(pred_col), "Length err_col",len(err_col)
        elif e_val == 'e_20':
            pred_prob_col = n_pe20
            pred_col = n_e20
            err_col = err_col_e20
            print "Length Pred_col",len(pred_col), "Length err_col",len(err_col)
        elif e_val == 'e_25':
            pred_prob_col = n_pe25
            pred_col = n_e25
            err_col = err_col_e25
        elif e_val == 'e_30':
            pred_prob_col = n_pe30
            pred_col = n_e30
            err_col = err_col_e30

        auc[e_val] = roc_auc_score(e_col, pred_prob_col)
        pred_col = [np.string_(x) for x in pred_col]
        err_col = [np.string_(x) for x in err_col]
        pred_col = pd.Series(data=pred_col)
        err_col = pd.Series(data=err_col)

        fpr, tpr, threshold = roc_curve(e_col, pred_prob_col)
        # df = pd.DataFrame(dict(fpr=fpr,tpr=tpr))
        p = Counter(error_col)['1']
        n = Counter(error_col)['0']
        tp = tpr*p
        fp = fpr*n
        df = pd.DataFrame(dict(fp=fp, tp=tp))
        plt = ggplot(df, aes(x='fp',y='tp')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(auc[e_val]))
        ggsave(filename=os.getcwd() + '\\oob\\31_05\\max_feature_sqrt\\manual_balance_class\\auc_{}.png'.format(e_val), plot=plt)
        print "AUC for {} column is {}".format(e_val,auc[e_val])
        print "Precision Score for {} column : ".format(e_val),precision_score(err_col, pred_col, pos_label='1', average='binary')
        error_col = pd.Series(error_col)
        pred_col = np.array(pred_col)
        print len(err_col), len(pred_col)
        ct = pd.crosstab(err_col, pred_col,rownames=['actual'], colnames=['preds'])
        print "Confusion Matrix for {} column :\n".format(e_val), ct
    #f.close()
    

def main():
    fname = 'e_30-20-07_balanced' + '.csv'
    date = '2015-07-15 00:00:00'
    algo_score(fname, date, table="balanced_manual_new_small_ds1_tse_temporal_lookback4_m1_15_07")

if __name__ == '__main__':
    print "Hello"
    main()
