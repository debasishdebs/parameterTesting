from __future__ import division
import datetime
import csv
from operator import itemgetter
import sys
from random import randint

from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
import pymysql

from algoScore import algo_score

f = open('output.txt', 'a')
#sys.stdout = f

finalData = []
prediction_dict = {}
prob_pos = []
pred_prob = {}

def push_to_pred_table(ts, col, attempt = 1):
    db = connect_PA_db()
    c = db.cursor()
    table = 'predicted_errors'
    
    if attempt == 1:    
        #c.execute("DROP TABLE IF EXISTS {}".format(table))
    
        sql_create = "CREATE TABLE IF NOT EXISTS `{}` (`id` int(11) NOT NULL AUTO_INCREMENT,`prediction_time` \
        timestamp NULL DEFAULT NULL,`predicted_error_time` timestamp NULL DEFAULT NULL, `col_name` varchar(6) NOT NULL,\
        PRIMARY KEY (`id`), UNIQUE KEY `unique` (`prediction_time`,`predicted_error_time`)) \
        ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;".format(table)

        c.execute(sql_create)
    
    col_val = {'e_5' : 5, 'e_10' : 10, 'e_15' : 15, 'e_20' : 20, 'e_25' : 25, 'e_30' : 30}
    minutes = col_val[col]
    
    # print type(ts)
    pred_ts = ts + datetime.timedelta(minutes = minutes)
    # print pred_ts, type(pred_ts)
    sql = "INSERT INTO {0} ({1}, {2}, {3}) VALUES ('{4}', '{5}', '{6}')".format(table, 'prediction_time', 
                                                                              'predicted_error_time', 'col_name', ts, pred_ts, col)
    # print sql
    c.execute(sql)
    db.commit()
    #print "Inserted"
    
def get_train_test_data(train_indx, test_indx, predictors, target):
    train_data = []
    test_data = []
    train_labels = []
    test_labels = []
    for i in range(len(train_indx)):
        train_data.append(predictors[int(train_indx[i])])
        train_labels.append(target[int(train_indx[i])])
    for j in range(len(test_indx)):
        test_data.append(predictors[int(test_indx[j])])
        test_labels.append(target[int(test_indx[j])])
    return train_data, test_data, train_labels, test_labels


def cross_validator(dataset, response_cols):
    print "This function does K-Fold CV (Stratified & Unstratified) with 3, 5 & 10 folds"
    KFolds = [3]
    target = [dataset[i][47] for i in range(len(dataset))]
    predictors = [dataset[i][0:46] for i in range(len(dataset))]
    rf = RandomForestClassifier(n_estimators = 50,criterion='gini', oob_score=True, max_features=0.6, n_jobs=4)
    print("RF trained successfully")
    train_test_cv = {}
    train_test_scv = {}
    for k in KFolds:
        now = datetime.datetime.now()
        skf_total = cross_validation.StratifiedKFold(target, n_folds = k, shuffle = False, random_state = randint(1,10))
        print("Stratified KFold done successfully")
        kf_total = cross_validation.KFold(len(predictors), n_folds = k, shuffle = True, random_state = randint(1,10))
        print "KFold done successfully"
        scores = cross_validation.cross_val_score(rf, predictors, target, cv = kf_total, n_jobs = 4)
        print "Cross Validation scores calculated successfully"
        stratified_scores = cross_validation.cross_val_score(rf, predictors, target, cv = skf_total, n_jobs = 4)
        print "UnStratified KFold. Optimized model after doing {}-Folds achieved. Indeces of its train & test set are stored in {} index of kf_total" \
        .format(k, list(scores).index(max(scores)))
        score_max = list(scores).index(max(scores))
        print "Stratified KFold. Optimized model after doing {}-Folds achieved. Indeces of its train & test set are stored in {} index of skf_total" \
        .format(k, list(stratified_scores).index(max(stratified_scores)))
        stratified_scores_max = list(stratified_scores).index(max(stratified_scores))
        i = 0
        for train, test in kf_total:
            if i == score_max:
                print "Train Set : {}, Test Set : {}\nCombination has the best cross validation score".format(train, test)
                train_data, test_data, train_labels, test_labels = get_train_test_data(train, test, predictors, target)
            i +=1
        train_test_cv[str(k) +'fold'] = {'train_data': train_data, 'test_data': test_data, 'train_label': train_labels,
                                        'test_label': test_labels, 'train_index': train}
        i = 0
        for train, test in skf_total:
            if i == stratified_scores_max:
                print "Train Set : {}, Test Set : {}\nCombination has the best stratified cross validation score"\
                    .format(train, test)
                train_data, test_data, train_labels, test_labels = get_train_test_data(train, test, predictors, target)
            i += 1
        train_test_scv[str(k) + 'fold'] = {'train_data': train_data, 'test_data': test_data, 'train_label': train_labels,
                                           'test_label': test_labels, 'train_index': train}
        print("Time taken for {}-Fold : ", datetime.datetime.now() - now)
    return train_test_cv, train_test_scv

def connect_PA_db():
    db = pymysql.connect(host = "127.0.0.1", db = "predictiveanalytics", user = "root", passwd = "")
    return db


def write_feature_imp(featureImportance):
    f = open('feature_importance.csv','w')
    writer = csv.writer(f,lineterminator = "\n")
    writer.writerows(featureImportance)

    f.close()
    
def out_list(col):
    print "Writing {} row to file".format(col)

    global prediction_dict
    global prob_pos

    prob_pred = sorted(prob_pos, key=itemgetter('ts'))

    ts_list = sorted(prediction_dict.keys())
    output_list = [['timestamp','error'] + [col] + ['p_col']]

    pred_prob_cols = ['p_e5', 'p_e10', 'p_e15', 'p_e20', 'p_e25', 'p_e30']

    for ts in ts_list:
        try:
            error = prediction_dict[ts]['error']
            temp = [ts,error]
        except:
            # print "Exception thrown. no prediction[ts][error] found.", ts
            continue
        try:
            prediction = prediction_dict[ts][col]
        except:
            # print "Exception thrown. no prediction[ts][col] found.", ts
            # print ts, col
            continue
        temp.append(prediction)
        for i in range(len(prob_pred)):
            if prob_pred[i]['ts'] == ts and prob_pred[i]['col'] == col:
                prediction = prob_pred[i]['pred']
                posClsProb = prob_pred[i]['prob'][:,int(prediction)][0] if (prediction == 1) else \
                        (1-prob_pred[i]['prob'][:,int(prediction)][0])
                temp.append(posClsProb)

        if len(temp) != 4:
            continue
        else:
            output_list.append(temp)

    return output_list

def main(table,lookahead,interval,criterion,num_trees,filename,start_date, stop_date,dt_len,ds):

    global finalData

    db = connect_PA_db()
    c = db.cursor()

    sql = "SELECT * FROM {} ORDER BY timestamp".format(table)

    #fetches data, parses to list format, and sorts data by reverse
    print 'Start data extraction'
    c.execute(sql)
    data = [list(i) for i in list(c.fetchall())]
    ts_list = [i[0] for i in data]
    data = [i[1:] for i in data]
    max_ts = max(ts_list)
    max_ts = max_ts - datetime.timedelta(minutes = 5)
    print 'Max timestamp: {}'.format(max_ts)
    print 'Data extraction complete'
    db.close()

    print 'Length of dataset: {}'.format(len(data))
    print 'Length of rows: {}'.format(len(data[0]))
    response_index_list,error_index,response_cols = find_responses(table)
    print "Calling Cross-Validation on generated dataset"
    # train_test_cv, train_test_scv = cross_validator(data, response_cols)
    print 'Start initial population of prediction dictionary'
    init_prediction_dict_population(table)
    print 'Initial population complete'

    global prediction_dict
    global pred_prob

    start = start_date
    stop = stop_date
    date = start_date.strftime("%Y-%m-%d %H:%M:%S")
    score = [[] for i in range(6)]
    feature_imp = []
    attempt = 1
    for i in range(len(response_index_list)):

        response = response_index_list[i]
        col = response_cols[i]
        print col

        predictors,responses = split_predictors_and_responses(data,response,error_index)

        start_date = start
        stop_date = stop

        start_index = ts_list.index(start_date)
        stop_index = ts_list.index(stop_date)
        print start_index, stop_index

        print '\tInitializing simulation of the following time interval:'
        print '\tstart date: {}'.format(start_date)
        print '\tend date: {}'.format(stop_date)

        #print train_test_scv['3fold']['train_index']
        if 'train_test_scv' in locals():
            scv_trn_indx = train_test_scv['3fold']['train_index']
        else:
            scv_trn_indx = [x for x in range(len(data)) if x < start_index]

        print "Start Index acc to TS : ", start_index
        new_indeces = [scv_trn_indx[i] for i in range(len(scv_trn_indx)) if scv_trn_indx[i] > start_index]
        print "Indeces which are greater than start_index of tS", new_indeces
        while start_index < len(data)-1 and stop_index < len(data) - 1 and start_date < max_ts and stop_date < max_ts:
            new_indeces = [scv_trn_indx[i] for i in range(len(scv_trn_indx)) if scv_trn_indx[i] > start_index]

            train_predictors,test_predictors,train_responses,test_responses,ts_interval = split_train_test(predictors,
                                                                responses,ts_list,start_index,stop_index, new_indeces)

            rf = create_and_train_rf(criterion,num_trees,train_predictors,train_responses, test_predictors)
            feature_imp.append(create_predictions(rf,test_predictors,ts_interval,col, attempt))

            start_index,stop_index = find_next_date_indexes(start_date,stop_date,ts_list,dt_len,ds)
            start_date = ts_list[start_index]
            stop_date = ts_list[stop_index]

            if start_date >= max_ts or stop_date >= max_ts:
                break
        out = out_list(col)
        print "Prediction dict is :\n",prediction_dict  
        print "Output list is :\n",out_list
        fname = '{}-20-07_unbalanced.csv'.format(col)
        write_output_list(out,fname)

    pred_prob = getPredScore()

    print '\nExperiment completed'
    print 'Creating output csv file'
    output_list = create_output_list(response_cols)
    print len(prediction_dict), type(prediction_dict)
    write_output_list(output_list,filename)

    write_feature_imp(feature_imp)
    algo_score(filename, date, table)
    #f.close()

def getPredScore():
    global prob_pos
    print len(prob_pos)

    prob_preds = {}

    prob_preds_e5 = [[] for x in range(2)]
    prob_preds_e10 = [[] for x in range(2)]
    prob_preds_e15 = [[] for x in range(2)]
    prob_preds_e20 = [[] for x in range(2)]
    prob_preds_e25 = [[] for x in range(2)]
    prob_preds_e30 = [[] for x in range(2)]

    prob_pred = sorted(prob_pos, key=itemgetter('ts'))

    for i in range(len(prob_pred)):
        if prob_pred[i]['col'] == 'e_5':
            prediction = prob_pred[i]['pred']
            prediction_prob_cl = prob_pred[i]['prob'] if (prediction == 1) else (1-prob_pred[i]['prob'])
            prob_preds_e5[0].append(prediction)
            prob_preds_e5[1].append(float(prediction_prob_cl[:,int(prediction)][0]))
        if prob_pred[i]['col'] == 'e_10':
            prediction = prob_pred[i]['pred']
            prediction_prob_cl = prob_pred[i]['prob'] if (prediction == 1) else (1-prob_pred[i]['prob'])
            prob_preds_e10[0].append(prediction)
            prob_preds_e10[1].append(float(prediction_prob_cl[:,int(prediction)][0]))
        if prob_pred[i]['col'] == 'e_15':
            prediction = prob_pred[i]['pred']
            prediction_prob_cl = prob_pred[i]['prob'] if (prediction == 1) else (1-prob_pred[i]['prob'])
            prob_preds_e15[0].append(prediction)
            prob_preds_e15[1].append(float(prediction_prob_cl[:,int(prediction)][0]))
        if prob_pred[i]['col'] == 'e_20':
            prediction = prob_pred[i]['pred']
            prediction_prob_cl = prob_pred[i]['prob'] if (prediction == 1) else (1-prob_pred[i]['prob'])
            prob_preds_e20[0].append(prediction)
            prob_preds_e20[1].append(float(prediction_prob_cl[:,int(prediction)][0]))
        if prob_pred[i]['col'] == 'e_25':
            prediction = prob_pred[i]['pred']
            prediction_prob_cl = prob_pred[i]['prob'] if (prediction == 1) else (1-prob_pred[i]['prob'])
            prob_preds_e25[0].append(prediction)
            prob_preds_e25[1].append(float(prediction_prob_cl[:,int(prediction)][0]))
        if prob_pred[i]['col'] == 'e_30':
            prediction = prob_pred[i]['pred']
            prediction_prob_cl = prob_pred[i]['prob'] if (prediction == 1) else (1-prob_pred[i]['prob'])
            prob_preds_e30[0].append(prediction)
            prob_preds_e30[1].append(float(prediction_prob_cl[:,int(prediction)][0]))

    prob_preds['e_5'] = prob_preds_e5
    prob_preds['e_10'] = prob_preds_e10
    prob_preds['e_15'] = prob_preds_e15
    prob_preds['e_20'] = prob_preds_e20
    prob_preds['e_25'] = prob_preds_e25
    prob_preds['e_30'] = prob_preds_e30

    return prob_preds

def create_output_list(response_cols):

    global prediction_dict
    global prob_pos

    prob_pred = sorted(prob_pos, key=itemgetter('ts'))

    ts_list = sorted(prediction_dict.keys())
    output_list = [['timestamp','error'] + response_cols + ['p_e5', 'p_e10', 'p_e15', 'p_e20', 'p_e25', 'p_e30']]

    pred_prob_cols = ['p_e5', 'p_e10', 'p_e15', 'p_e20', 'p_e25', 'p_e30']

    for ts in ts_list:
        try:
            error = prediction_dict[ts]['error']
            temp = [ts,error]
        except:
            continue
        for col in response_cols:
            try:
                prediction = prediction_dict[ts][col]
            except:
                # print ts, col
                continue
            temp.append(prediction)
        for pCol in response_cols:
            for i in range(len(prob_pred)):
                if prob_pred[i]['ts'] == ts and prob_pred[i]['col'] == pCol:
                    prediction = prob_pred[i]['pred']
                    posClsProb = prob_pred[i]['prob'][:,int(prediction)][0] if (prediction == 1) else \
                        (1-prob_pred[i]['prob'][:,int(prediction)][0])
                    temp.append(posClsProb)

        if len(temp) != len(response_cols) + 8:
            continue
        else:
            output_list.append(temp)

    return output_list

def write_output_list(output_list,filename):

    f = open(filename,'w')
    writer = csv.writer(f,lineterminator = "\n")
    writer.writerows(output_list)
    f.close()

def init_prediction_dict_population(table):

    global prediction_dict

    db = connect_PA_db()
    c = db.cursor()

    sql = "SELECT timestamp,error FROM {} WHERE timestamp >= '2015-04-30 00:00' ORDER BY timestamp".format(table)
    c.execute(sql)

    results = [list(i) for i in c.fetchall()]

    for row in results:
        ts = row[0]
        error = row[1]
        prediction_dict[ts] = {'error':error}
    #print "Timestamps in Prediction dictionart is :\n",set(prediction_dict)
    print "Number of elements in prediction dict ",len(prediction_dict)
    


def extract_timestamp_and_errors(table):

    db = connect_PA_db()
    c = db.cursor()

    sql = "SELECT timestamp,error FROM {} WHERE timestamp >= '2015-04-30 00:00' ORDER BY timestamp".format(table)
    c.execute(sql)

    results = [list(i) for i in list(c.fetchall())]
    return results

def create_predictions(rf,test_predictors,ts_interval,col, attempt):

    global prediction_dict
    global prob_pos

    print '\t\tstarting predictions'
    pred_list = []
    prob_list = []
    now = datetime.datetime.now()
    for i in range(len(test_predictors)):
        row = test_predictors[i]
        ts = ts_interval[i]
        prediction = rf.predict(row)[0]
        prob = rf.predict_proba(row)
        pred_list.append(prediction)
        prob_list.append(prob)
        prob_pos.append({'ts' : ts, 'col' : col, 'prob' : prob, 'pred' : prediction})
        if (col == 'e_5' or col == 'e_10' or col == 'e_15' or col == 'e_20' or col == 'e_25' or col == 'e_30') and prediction == 1:
            print prediction, ts, col
            push_to_pred_table(ts, col, attempt)
            attempt +=1                                                                             #attempt : Number of pos preds
        # prediction_dict[ts] = {}
        prediction_dict[ts][col] = prediction
    print '\t\tpredictions completed, Length of prediction set = {}\nTime took for predicting day = {}'\
        .format(len(prediction_dict), datetime.datetime.now() - now)

    return rf.feature_importances_


def create_and_train_rf(criterion,num_trees,train_predictors,train_responses, test_predictors):

    print '\t\tcreating random forest'
    rf = RandomForestClassifier(n_estimators = num_trees,criterion=criterion, max_depth=10, n_jobs=4)
    print '\t\trandom forest created successfully'

    print '\t\ttraining random forest'
    fit = rf.fit(train_predictors,train_responses)
    print "RF Fitted"
    #score = rf.score(train_predictors, train_responses)

    #prob_pos = rf.predict_proba(test_predictors)

    print '\t\trandom forest successfully trained'

    return rf


def find_next_date_indexes(start_date,stop_date,ts_list,dt_len,ds=[None]):
##    if ds == [None]:
##        print start_date, start_date.replace(minute=0)
##        start_date_next = start_date.replace(minute=0) + datetime.timedelta(days = dt_len)
##        stop_date_next = stop_date.replace(minute=0) + datetime.timedelta(days = dt_len)
##
##        start_index = ts_list.index(start_date)
##        stop_index = ts_list.index(stop_date)
##
##        while start_date < start_date_next and start_index < len(ts_list)-1:
##            start_date = ts_list[start_index]
##            start_index += 1
##        start_index -= 1
##        start_date = ts_list[start_index]
##
##        while stop_date < stop_date_next and stop_index < len(ts_list)-1:
##            stop_date = ts_list[stop_index]
##            stop_index += 1
##        stop_index -= 1
##        stop_date = ts_list[stop_index]
##
##        print '\tInitializing simulation of the following time interval:'
##        print '\tstart date: {}'.format(start_date)
##        print '\tend date: {}'.format(stop_date)
##
##        return start_index,stop_index
##    else:
##        start_date_next = start_date.replace(minute=0) + datetime.timedelta(days = dt_len)
##        stop_date_next = stop_date.replace(minute=0) + datetime.timedelta(days = dt_len)
##        strt_ind = get_dates(ds, start_date_next)
##        if strt_ind >= 0:
##            if ds[strt_ind] < stop_date_next.date():
##                stop_ind = get_dates(ds, stop_date_next)
##            elif ds[strt_ind] == stop_date_next.date():
##                stop_date_next = stop_date_next + datetime.timedelta(days=1)
##                stop_ind = get_dates(ds, stop_date_next)
##            elif ds[strt_ind] > stop_date_next.date():
##                midnight = datetime.datetime.combine(ds[strt_ind], datetime.datetime.min.time())
##                stop_date_next = midnight + datetime.timedelta(days=1)
##                stop_ind = get_dates(ds, stop_date_next)
##            if stop_ind >= 0:
##                start_date_next = datetime.datetime.combine(ds[strt_ind], datetime.datetime.min.time())
##                stop_date_next = datetime.datetime.combine(ds[stop_ind], datetime.datetime.min.time())
##                start_index = ts_list.index(start_date)
##                stop_index = ts_list.index(stop_date)
##
##                while start_date < start_date_next and start_index < len(ts_list)-1:
##                    start_date = ts_list[start_index]
##                    start_index += 1
##                start_index -= 1
##                start_date = ts_list[start_index]
##
##                while stop_date < stop_date_next and stop_index < len(ts_list)-1:
##                    stop_date = ts_list[stop_index]
##                    stop_index += 1
##                stop_index -= 1
##                stop_date = ts_list[stop_index]
##
##                print '\tInitializing simulation of the following time interval:'
##                print '\tstart date: {}'.format(start_date)
##                print '\tend date: {}'.format(stop_date)
##
##                return start_index,stop_index
    print start_date, start_date.replace(minute=0)
    start_date_next = start_date.replace(minute=0) + datetime.timedelta(days = dt_len)
    stop_date_next = stop_date.replace(minute=0) + datetime.timedelta(days = dt_len)

    start_index = ts_list.index(start_date)
    stop_index = ts_list.index(stop_date)

    while start_date < start_date_next and start_index < len(ts_list)-1:
        start_date = ts_list[start_index]
        start_index += 1
    start_index -= 1
    start_date = ts_list[start_index]

    while stop_date < stop_date_next and stop_index < len(ts_list)-1:
        stop_date = ts_list[stop_index]
        stop_index += 1
    stop_index -= 1
    stop_date = ts_list[stop_index]

    print '\tInitializing simulation of the following time interval:'
    print '\tstart date: {}'.format(start_date)
    print '\tend date: {}'.format(stop_date)

    return start_index,stop_index

def get_dates(ds, dt):
    try:
        ind = ds.index(dt)
        return ind
    except:
        dt = dt + datetime.timedelta(days=1)
        get_dates(ds, dt)


def split_train_test(predictors,responses,ts_list,start_index,stop_index, new_indeces):

    train_predictors = predictors[:start_index] + [predictors[new_indeces[i]] for i in range(len(new_indeces))]
    test_predictors = predictors[start_index:stop_index]

    train_responses = responses[:start_index] + [responses[new_indeces[i]] for i in range(len(new_indeces))]
    test_responses = responses[start_index:stop_index]

    ts_interval = ts_list[start_index:stop_index]

    return train_predictors,test_predictors,train_responses,test_responses,ts_interval


def split_predictors_and_responses(dataset,response_index,error_index):

    predictors = [i[:error_index] for i in dataset]
    responses = [i[response_index-1] for i in dataset]
    print response_index
    return predictors,responses


def find_responses(table):

    db = connect_PA_db()
    c = db.cursor()

    sql = "SHOW COLUMNS FROM {}".format(table)
    c.execute(sql)

    cols = [i[0] for i in c.fetchall()]
    print cols
    error_index = cols.index("error")

    num_responses = len(cols[error_index:])-1
    print 'Number of responses found: {}'.format(num_responses)

    response_cols = cols[error_index+1:]
    print 'Response columns: {}'.format(response_cols)

    response_index_list = []

    for col in response_cols:
        response_index_list.append(cols.index(col))
    print 'Response column indexes: {}'.format(response_index_list)

    return response_index_list,error_index,response_cols

def start(table,ds=[None]):
    print "Starts Here\n"
    start_date = datetime.datetime(2015, 4, 30, 0, 0)
    end_date = datetime.datetime(2015, 5, 1, 0, 0)
    for i in range(0,1):
        end_date = end_date + datetime.timedelta(days=i)
        fname = 'small_ds1_tse_temporal_lookback4_predictions_classBalance' + str('30_04') + '.csv'
        main(table,30,5,'gini',100,fname,start_date,end_date,i+1,ds)

#start(table='small_ds1_tse_temporal_lookback4')