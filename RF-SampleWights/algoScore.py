__author__ = 'Debasish'

import csv
import datetime
import sys, os

from dateutil import parser
import pandas as pd
import numpy as np
from sklearn.metrics import *
from ggplot import *
from collections import Counter
from balanceIt import connect_db

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

    def transform_col(self, col1, col2, col2_name, shift_value = 0):
        if shift_value == 0:
            return col1, col2
        elif 'p' not in col2_name:
            val = []
            new_col2 = []
            values = get_value(self.date, shift_value, col2_name, self.table)
            for value in values:
                val.append(value[0])
            for i in range(len(val)):
                new_col2.append(val[i])
            for i in range(len(col2)):
                new_col2.append(col2[i])
            col2 = new_col2[:-1*len(val)]
            return col2
        elif 'p' in col2_name:
            val = []
            new_col2 = []
            col_dict = {'p_e5':8,'p_e10': 9, 'p_e15': 10,'p_e20' : 11, 'p_e25': 12,'p_e30': 13}
            for key, value in col_dict.iteritems():
                if key == col2_name:
                    col_num = value
            data = self.dataset
            start_date = self.date
            tse_col, error_col, fut_err, fut_err_prob = self.get_columns()
            err_prob = fut_err_prob[col2_name]
            for i in range(len(tse_col)):
                if tse_col[i+shift_value] >= start_date:
                    new_col2.append(data[i][col_num])
            col2 = new_col2[:-1*shift_value]
            return col2


def algo_score(fname, date, table):

    fileName = os.getcwd() + '\\oobF\\max_feature_sqrt\\sample_wt_output_100tree.txt'
    print(fileName)
    create_file(fileName)
    f = open(fileName, 'w')
    sys.stdout = f
    print "File name for data : ", fname
    file = fileReader(fname, date, table)
    dataset = file.read_file()
    print("Length of dataset", len(dataset))
    e_col = []
    auc = {}
    err = ['e_5', 'e_10', 'e_15', 'e_20', 'e_25', 'e_30']

    tse_col, error_col, fut_err, fut_err_prob = file.get_columns()
    print len(error_col), len(fut_err['e_5'])
    n_e5 = file.transform_col(error_col, fut_err['e_5'], 'e_5', 1)

    n_e10 = file.transform_col(error_col, fut_err['e_10'], 'e_10', 2)
    n_e15 = file.transform_col(error_col, fut_err['e_15'], 'e_15', 3)
    n_e20 = file.transform_col(error_col, fut_err['e_20'], 'e_20', 4)
    n_e25 = file.transform_col(error_col, fut_err['e_25'], 'e_25', 5)
    n_e30 = file.transform_col(error_col, fut_err['e_30'], 'e_30', 6)

    n_pe5 = file.transform_col(error_col, fut_err_prob['e_5'], 'e_5', 1)
    n_pe10 = file.transform_col(error_col, fut_err_prob['e_10'], 'e_10', 2)
    n_pe15 = file.transform_col(error_col, fut_err_prob['e_15'], 'e_15', 3)
    n_pe20 = file.transform_col(error_col, fut_err_prob['e_20'], 'e_20', 4)
    n_pe25 = file.transform_col(error_col, fut_err_prob['e_25'], 'e_25', 5)
    n_pe30 = file.transform_col(error_col, fut_err_prob['e_30'], 'e_30', 6)

    for i in range(len(error_col)):
        e_col.append(int(error_col[i]))

        n_pe5[i] = float(n_pe5[i])
        n_pe10[i] = float(n_pe10[i])
        n_pe15[i] = float(n_pe15[i])
        n_pe20[i] = float(n_pe20[i])
        n_pe25[i] = float(n_pe25[i])
        n_pe30[i] = float(n_pe30[i])

        n_e5[i] = str(n_e5[i])
        n_e10[i] = str(n_e10[i])
        n_e15[i] = str(n_e15[i])
        n_e20[i] = str(n_e20[i])
        n_e25[i] = str(n_e25[i])
        n_e30[i] = str(n_e30[i])
    for e_val in err:
        if e_val == 'e_5':
            pred_prob_col = n_pe5
            pred_col = n_e5
        elif e_val == 'e_10':
            pred_prob_col = n_pe10
            pred_col = n_e10
        elif e_val == 'e_15':
            pred_prob_col = n_pe15
            pred_col = n_e15
        elif e_val == 'e_20':
            pred_prob_col = n_pe20
            pred_col = n_e20
        elif e_val == 'e_25':
            pred_prob_col = n_pe25
            pred_col = n_e25
        elif e_val == 'e_30':
            pred_prob_col = n_pe30
            pred_col = n_e30

        auc[e_val] = roc_auc_score(e_col, pred_prob_col)

        fpr, tpr, threshold = roc_curve(e_col, pred_prob_col)
        # df = pd.DataFrame(dict(fpr=fpr,tpr=tpr))
        p = Counter(error_col)['1']
        n = Counter(error_col)['0']
        tp = tpr*p
        fp = fpr*n
        df = pd.DataFrame(dict(fp=fp, tp=tp))
        plt = ggplot(df, aes(x='fp',y='tp')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(auc[e_val]))
        ggsave(filename=os.getcwd() + '\\oobF\\max_feature_sqrt\\auc_{}.png'.format(e_val), plot=plt)
        print "AUC for {} column is {}".format(e_val,auc[e_val])
        print "Precision Score for {} column : ".format(e_val),precision_score(error_col, pred_col, pos_label='1', average='binary')
        error_col = pd.Series(error_col)
        pred_col = np.array(pred_col)
        print "Confusion Matrix for {} column :\n".format(e_val), pd.crosstab(error_col, pred_col,rownames = ['actual'], colnames=['preds'])


    f.close()

def main():
    fname = 'small_ds1_tse_temporal_lookback4_predictions_classBalance' + str('10_07') + '.csv'
    date = '2015-07-10 00:00:00'
    algo_score(fname, date, table="new_small_ds1_tse_temporal_lookback4_balanced")

if __name__ == '__main__':
    print "Hello"
    main()
