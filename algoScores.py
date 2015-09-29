__author__ = 'Debasish'

import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ggplot import *
from sklearn.metrics import *
import sys
from dateutil.parser import parse
from datetime import timedelta
from balanceIt import connect_db

##f = open('output.txt', 'w')
##sys.stdout = f

''' Todo : Form pairs. (Error & e_5), (error & e_10), (error & e_15) and so on. Total 6 pairs will be formed of different length. Each pair ll have length same as its e_x value.
    Pass each list of pair together (error & e_5), (error & e_10) to pd.crosstab function after converting them to Pandas Series & Numpy.ndarray.
    Save each crasstab result in different list thus giving f-table for each possible case.
    Use each crosstab to plot ROC curve. (Part of skitlearn package) and find area under curve of each parameter. Once done, select the most optimized one.'''

def plotROC(fpr, tpr, preds_auc):
    plt.figure()
    plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)'%preds_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

def getPredClsScore(dataset):
    e5PredCls = []
    e10PredCls = []
    e15PredCls = []
    e20PredCls = []
    e25PredCls = []
    e30PredCls = []

    error_list = []

    for j in range(1,len(dataset[0])):
        e5PredCls.append(float(dataset[0][j][8]))
        e10PredCls.append(float(dataset[0][j][9]))
        e15PredCls.append(float(dataset[0][j][10]))
        e20PredCls.append(float(dataset[0][j][11]))
        e25PredCls.append(float(dataset[0][j][12]))
        e30PredCls.append(float(dataset[0][j][13]))
        error_list.append(float(dataset[0][j][1]))

    pred_pos_cls = {}
    pred_pos_cls['e_5'] = e5PredCls
    pred_pos_cls['e_10'] = e10PredCls
    pred_pos_cls['e_15'] = e15PredCls
    pred_pos_cls['e_20'] = e20PredCls
    pred_pos_cls['e_25'] = e25PredCls
    pred_pos_cls['e_30'] = e30PredCls

    return error_list, pred_pos_cls



def get_algo_scores(filename):

    print "In Here"
    dataset = [None]*1
    for i in range(1):
        fname = filename
        lines = csv.reader(open(fname, "rt"))
        #lines = csv.reader(open(fname, "rt"))
        dataset[i] = list(lines)

    error_list, predsPosClsScore = getPredClsScore(dataset)
    dictionaries = []

    for i in range(1):
        dictionaries = create_dicts(dataset[i])                             #Dictionary[i] stores all the data in i_th.csv file
        #print len(dictionaries)
    dictL = [None]*7

    for i in range(len(dictL)):
        #print (dictionaries[i])
        #print "Length of dictionary passed ", len(dictionaries[0])
        dictL[i] = dict_to_list(dictionaries[i])                            #Each row of dictL holds errors for the whole day. Either error column or e_5 column or e_10 & so on..

        #print dictL[5][1]
        #print (dictL[1][0])

    for i in range(1,len(dictL)):
        if i == 1:
            err_e5 = merge_lists(dictL[i], i, dictL[0])
        elif i == 2:
            err_e10 = merge_lists(dictL[i], i, dictL[0])
        elif i == 3:
            err_e15 = merge_lists(dictL[i], i, dictL[0])
        elif i == 4:
            err_e20 = merge_lists(dictL[i], i, dictL[0])
        elif i == 5:
            err_e25 = merge_lists(dictL[i], i, dictL[0])
        elif i == 6:
            err_e30 = merge_lists(dictL[i], i, dictL[0])
    #print err_e10
    auc = {}
    for i in range(1, len(dictL)):
        if i == 1:
            err_list, ftr_err_list = data_crosstab(err_e5, i)
            print err_list
            print ftr_err_list
            preds_auc = roc_auc_score(error_list, predsPosClsScore['e_5'])
            auc['e_5'] = preds_auc
            print "AUC for e_5 :", preds_auc
            fpr, tpr, threshold = roc_curve(error_list, predsPosClsScore['e_5'])
            df = pd.DataFrame(dict(fpr=fpr,tpr=tpr))
            plt = ggplot(df, aes(x='fpr',y='tpr')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(preds_auc))
            ggsave(filename='auc_e5.png', plot=plt)
            #plotROC(fpr, tpr, preds_auc)
            crosstab(err_list, ftr_err_list)
        elif i == 2:
            err_list, ftr_err_list = data_crosstab(err_e10, i)
            print "AUC for e_10 :", roc_auc_score(error_list, predsPosClsScore['e_10'])
            auc['e_10'] = roc_auc_score(error_list, predsPosClsScore['e_10'])
            fpr, tpr, threshold = roc_curve(error_list, predsPosClsScore['e_10'])
            df = pd.DataFrame(dict(fpr=fpr,tpr=tpr))
            plt = ggplot(df, aes(x='fpr',y='tpr')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(auc['e_10']))
            ggsave(filename='auc_e10.png', plot=plt)
            #plotROC(fpr, tpr, preds_auc)
            crosstab(err_list, ftr_err_list)
        elif i == 3:
            err_list, ftr_err_list = data_crosstab(err_e15, i)
            print "AUC for e_15 :", roc_auc_score(error_list, predsPosClsScore['e_15'])
            auc['e_15'] = roc_auc_score(error_list, predsPosClsScore['e_15'])
            fpr, tpr, threshold = roc_curve(error_list, predsPosClsScore['e_15'])
            df = pd.DataFrame(dict(fpr=fpr,tpr=tpr))
            plt = ggplot(df, aes(x='fpr',y='tpr')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(auc['e_15']))
            ggsave(filename='auc_e15.png', plot=plt)
            #plotROC(fpr, tpr, preds_auc)
            crosstab(err_list, ftr_err_list)
        elif i == 4:
            err_list, ftr_err_list = data_crosstab(err_e20, i)
            print "AUC for e_20 :", roc_auc_score(error_list, predsPosClsScore['e_20'])
            auc['e_20'] = roc_auc_score(error_list, predsPosClsScore['e_20'])
            fpr, tpr, threshold = roc_curve(error_list, predsPosClsScore['e_20'])
            df = pd.DataFrame(dict(fpr=fpr,tpr=tpr))
            plt = ggplot(df, aes(x='fpr',y='tpr')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(auc['e_20']))
            ggsave(filename='auc_e20.png', plot=plt)
            crosstab(err_list, ftr_err_list)
        elif i == 5:
            err_list, ftr_err_list = data_crosstab(err_e25, i)
            print "AUC for e_25 :", roc_auc_score(error_list, predsPosClsScore['e_25'])
            auc['e_25'] = roc_auc_score(error_list, predsPosClsScore['e_25'])
            fpr, tpr, threshold = roc_curve(error_list, predsPosClsScore['e_25'])
            df = pd.DataFrame(dict(fpr=fpr,tpr=tpr))
            plt = ggplot(df, aes(x='fpr',y='tpr')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(auc['e_25']))
            ggsave(filename='auc_e25.png', plot=plt)
            crosstab(err_list, ftr_err_list)
        elif i == 6:
            err_list, ftr_err_list = data_crosstab(err_e30, i)
            print "AUC for e_30 :", roc_auc_score(error_list, predsPosClsScore['e_30'])
            auc['e_30'] = roc_auc_score(error_list, predsPosClsScore['e_30'])
            fpr, tpr, threshold = roc_curve(error_list, predsPosClsScore['e_30'])
            df = pd.DataFrame(dict(fpr=fpr,tpr=tpr))
            plt = ggplot(df, aes(x='fpr',y='tpr')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(auc['e_30']))
            ggsave(filename='auc_e30.png', plot=plt)
            crosstab(err_list, ftr_err_list)
    # with open ('auc.txt', 'w') as fp:
    #     for p in auc.items():
    #         fp.write("%s:%s\n" % p)

##    f.close()

def crosstab(err_list, ftr_err_list):
    plt.plot(err_list, ftr_err_list)
    tpr, fpr, tp, fp = precision_recall(err_list, ftr_err_list)
    #print "TPR : {}, FPR : {} ".format(tpr, fpr)
    #print "TP : {}, FP : {}".format(tp,fp)
    #plt.show()
    #print np.trapz(err_list, ftr_err_list)
    #print set(ftr_err_list)
    for i in range(len(err_list)):
        err_list[i] = int(err_list[i])
        ftr_err_list[i] = int(ftr_err_list[i])
    print "Precision Score : ",precision_score(err_list, ftr_err_list, average='binary')
    err_list = pd.Series(err_list)
    ftr_err_list = np.array(ftr_err_list)
    ct = pd.crosstab(err_list, ftr_err_list,rownames = ['actual'], colnames=['preds'])
    print "Confusion Matrix"
    print ct
    print "\n"

def precision_recall(y_actual, y_pred):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for i in range(len(y_actual)):
        if int(y_actual[i]) == int(y_pred[i]) == 1:
            tp+=1
        elif int(y_actual[i]) == 1 and int(y_pred[i]) == 0:
            fn+=1
        elif int(y_actual[i]) == 0 and int(y_pred[i]) == 1:
            fp+=1
        elif int(y_actual[i]) == 0 and int(y_pred[i]) == 0:
            tn+=1
    print "Total TP : {0}, Total TN : {1}".format(tp,tn)
    print "Total FP : {0}, Total FN : {1}".format(fp,fn)
    tpr = float(tp)/float(tp+fn)
    fpr = float(fp)/float(tn+fp)
    print "True Positive Rate : {0}, False Positive Rate : {1}.".format(tpr, fpr)
    return tpr, fpr, tp, fp

def get_resp_db(ts, x):
    db = connect_db()
    c = db.cursor()
    table = 'new_small_ds1_tse_temporal_lookback4'
    print table, ts
    sql = "SELECT e_{0} FROM {1} WHERE timestamp >= '{2}'".format(str(5*x), table, ts)
    print sql
    c.execute(sql)
    print ts, c.fetchone()
    return c.fetchone()[0]

def data_crosstab(data, x):
    err_list = []
    future_err_list = []
    print type(data), len(data)
    print data[0]
    for i in range(len(data)):
        if (i-x) < 0:
            ts = data[i]['ts']
            ts = parse(ts)
            new_ts = ts - timedelta(minutes = 5*(x))
            new_ts_str = new_ts.strftime("%Y-%m-%d %H:%M:%S")
            resp = get_resp_db(new_ts_str, x)
            future_err_list.append(resp)
            err_list.append(data[i]['err'])
        else:
            err_list.append(data[i]['err'])
            future_err_list.append(data[i-x]['e_{}'.format(5*x)])
    return err_list, future_err_list

def merge_lists(dicts, x, dict_err):
    #print "Merge_lists"
    print len(dicts[0]), len(dicts), len(dict_err)

    err_e = [dict() for p in range(len(dicts[0]))]
    k = 0
    for i in range(len(dicts[0])):
        for j in range(len(dict_err[0])):
            if dict_err[0][j] == dicts[0][i]:                   #Comparing time stamps
                err_e[k] = {'ts' : dicts[0][i], 'err' : dict_err[1][j], 'e_{}'.format(str(x*5)) : dicts[1][i] }
                k +=1
                break
    #print err_e
    return err_e

def dict_to_list(dictionary):                                           #Converts each list of dictionary into list where only Values are stored and keys are skipped.
    lDict = [[] for x in range(2)]
    flag = 0
    for j in range(len(dictionary)):
        #print "length : ", len(dictionary[i][j])
        for key, value in dictionary[j].iteritems():
            if value!= 'timestamp' and "e" not in value:
                if len(value) == 1:
                    lDict[1].append(value)
                else:
                    lDict[0].append(value)
    #print(len(lDict[0]))

    return lDict

def create_dicts(dataset):
    lDicts = [None]*7
    print "Length of DS from create_dict func : ", len(dataset)
    for i in range(len(lDicts)):
        lDicts[i] = getDict(dataset, i)                                 #lDict[i] stores either only {ts->error} dictionary, or {ts->e_5} or {ts->e_10} and so on depending on value of 'i'..
        #print "lDict : ",len(lDicts[i])
    return lDicts

def getDict(dataset, x):                                                #Returns a dictionary of ts->error against 'x' specified. x=0(error), x=1(e_5), x=2(e_10) & so on for a particular file.
    if x==0:
        inp_dict = [dict() for i in range(len(dataset))]
        for i in range(len(dataset)):
            if dataset[i][1] == 1:
                print "Actual error at ts : {0} is {1} and predicted at e5 : {2}, and e10 :{3}".format(dataset[i][0], dataset[i-0][1], dataset[i-1][2], dataset[i-2][3])
            inp_dict[i] = {'ts' : dataset[i][0], 'error' : dataset[i][x+1]}

        return inp_dict
    if x==1:
        inp_dict = [dict() for i in range(len(dataset))]
        for i in range(len(dataset)):
            try:
                inp_dict[i] = {'ts' : dataset[i][0], 'e_5' : dataset[i][x+1]}
            except:
                continue

        return inp_dict
    if x==2:
        inp_dict = [dict() for i in range(len(dataset))]
        for i in range(len(dataset)):
            try:
                inp_dict[i] = {'ts' : dataset[i][0], 'e_10' : dataset[i][x+1]}
            except:
                continue

        return inp_dict
    if x==3:
        inp_dict = [dict() for i in range(len(dataset))]
        for i in range(len(dataset)):
            try:
                inp_dict[i] = {'ts' : dataset[i][0], 'e_15' : dataset[i][x+1]}
            except:
                continue

        return inp_dict
    if x==4:
        inp_dict = [dict() for i in range(len(dataset))]
        for i in range(len(dataset)):
            try:
                inp_dict[i] = {'ts' : dataset[i][0], 'e_20' : dataset[i][x+1]}
            except:
                continue

        return inp_dict
    if x==5:
        inp_dict = [dict() for i in range(len(dataset))]
        for i in range(len(dataset)):
            try:
                inp_dict[i] = {'ts' : dataset[i][0], 'e_25' : dataset[i][x+1]}
            except:
                continue

        return inp_dict
    if x==6:
        inp_dict = [dict() for i in range(len(dataset))]
        for i in range(len(dataset)):
            try:
                inp_dict[i] = {'ts' : dataset[i][0], 'e_30' : dataset[i][x+1]}
            except:
                continue

        return inp_dict


filename = 'small_ds1_tse_temporal_lookback4_predictions_' + str(0+20) + '.csv'
#get_algo_scores(filename)
