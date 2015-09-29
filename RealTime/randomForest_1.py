from __future__ import division
import datetime
import csv
import time
from operator import itemgetter

#import sys
from random import randint

from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
import pymysql, threading

'''f = open('output.txt', 'a')
sys.stdout = f'''

finalData = []
prediction_dict = {}
prob_pos = []
pred_prob = {}

class TimerThread(threading.Thread):
    def __init__(self, t, threadID):
        self.t = t
        self.threadID = threadID

    def run(self):
        countdown_timer(self.t)


'''Alert function. create_alert: Once an error has been predicted from new predictor row it sends over the corresponding
column from which it was predicted, i.e. how much time in future error will occur. Subsequently error message will be
displayed..
Extend : Create a countdown timer after alert to let users know exactly how much time left for error.
'''

def create_alert(col):
    if col == 'e_5':
        print("Error is going to occur in next 5min")
    elif col == 'e_10':
        print("Error will occur in next 10min")
    elif col == 'e_15':
        print("Error will occur in next 15min")
    elif col == 'e_20':
        print("Error will occur in next 20min")
    elif col == 'e_25':
        print("Error will occur in next 25min")
    elif col == 'e_30':
        print("Error will occur in next 30min")

'''Previously defined to start counter. The function calls itself every 5 min and then start() is called from inside
function thus achieving the Real Time Objective.
Recent modifications to start() made it depreciated and is no longer used in program.
'''

def countdown_timer(t):
    while t:
        mins, sec = divmod(t, 60)
        timeFormat = '{:02d}:{02d}'.format(mins, sec)
        print(timeFormat, " till next error occurs")
        time.sleep(1)
        t = t-1


def counter():
    # s = sched.scheduler(time.time, time.sleep)
    end_date = datetime.datetime(2015, 6, 1, 0, 0)
    # s.enter(300, 1, start(end_date, s), (s,))
    # s.run()
    start(end_date)

'''Splits predictors & response into test_data, test_labels. Also into test_data & test_labels for testing them model.
'''

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

'''
Cross validation function. Does Stratified & Unstratified 3, 5 & 10 Fold CV to find most optimal training set.
Extension : Include Grid Search CV in later stages to tune in various RF settings/ parameters.
Present Status : After recent updates, it was decided adding data points or using CV train set in dangerous and may lead
to over fitting. Hence no more in use. Will be used only to find optimised set of parameters.
'''

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

'''
Function to connect PA db.
'''

def connect_PA_db():
    db = pymysql.connect(host = "127.0.0.1", db = "predictiveanalytics", user = "root", passwd = "")
    return db

'''
Feature importance stored beforehand as 2-D matrix in featureImportance variable is writted to feature_importance.csv
'''

def write_feature_imp(featureImportance):
    f = open('feature_importance.csv','w')
    writer = csv.writer(f,lineterminator = "\n")
    writer.writerows(featureImportance)
    f.close()

'''
Main function for RF module/script.
Features : Creates dataset by extracting it from DB.
Initialize prediction dict.
Call Random forest functions iteratively for each response column to get response after 5, 10, 15.. 30min.
'''

def main(table,lookahead,interval,criterion,num_trees,filename,start_date, stop_date,dt_len, timestamp):

    global finalData
    print timestamp
    db = connect_PA_db()
    c = db.cursor()
    tID = 1
    sql = "SELECT * FROM {} ORDER BY timestamp".format(table)

    print 'Start data extraction'
    c.execute(sql)
    data = [list(i) for i in list(c.fetchall())]
    ts_list = [i[0] for i in data]
    data = [i[1:] for i in data]
    max_ts = max(ts_list)
    max_ts = max_ts - datetime.timedelta(minutes=5)
    print 'Max timestamp: {}'.format(max_ts)
    print 'Data extraction complete'
    db.close()

    print 'Length of dataset: {}'.format(len(data))
    print 'Length of rows: {}'.format(len(data[0]))
    response_index_list,error_index,response_cols = find_responses(table)
    print "Calling Cross-Validation on generated dataset"
    # train_test_cv, train_test_scv = cross_validator(data, response_cols)
    print 'Start initial population of prediction dictionary'
    init_prediction_dict_population(table, timestamp)
    print 'Initial population complete'

    global prediction_dict
    global pred_prob

    start = start_date
    stop = stop_date
    date = start_date.strftime("%Y-%m-%d %H:%M:%S")
    score = [[] for i in range(6)]
    feature_imp = []

    '''Loop to iterate through each response columns. i.e. Separate for e_5, e_10.. e_30 columns.'''
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

        if 'train_test_scv' in locals():
            scv_trn_indx = train_test_scv['3fold']['train_index']
        else:
            scv_trn_indx = [x for x in range(len(data)) if x < start_index]

        print "Start Index acc to TS : ", start_index
        new_indeces = [scv_trn_indx[i] for i in range(len(scv_trn_indx)) if scv_trn_indx[i] > start_index]
        print "Indeces which are greater than start_index of tS", new_indeces
        new_indeces = [scv_trn_indx[i] for i in range(len(scv_trn_indx)) if scv_trn_indx[i] > start_index]

        train_predictors,test_predictors,train_responses,test_responses,ts_interval = split_train_test(predictors,
                                                                responses,ts_list,start_index,stop_index, new_indeces)

        rf = create_and_train_rf(criterion,num_trees,train_predictors,train_responses, test_predictors)
        prediction = create_predictions(rf, test_predictors, ts_interval, col)
        print("Prediction for row {}\n is {}".format(test_predictors, prediction))

        if prediction == 1:
            if col == 'e_5':
                timer = TimerThread(300, tID)
                tID += 1
                timer.start()

        if start_date >= max_ts or stop_date >= max_ts:
            break

    pred_prob = getPredScore()

    print '\nExperiment completed'
    # print 'Creating output csv file'
    # output_list = create_output_list(response_cols)
    # print len(prediction_dict), type(prediction_dict)
    # write_output_list(output_list,filename)
    #
    # write_feature_imp(feature_imp)
    # algo_score(filename, date, table)
    # f.close()

'''
Function returns prediction probability of a class for each prediction against each response column.
The variable prob_pos stores probability for a test row belonging to its predicted class. It does an ETL of prob_pos
by reading it, and returning only probability towards positive class. i.e. probability to belong to only '1' class.
'''

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

'''Reads global variable prediction dictionary and using the predictions and probability towards positive class,
create a 2-D list where rows are timestamps and columns are error, ts, response columns (predictions) and probability
for positive class for each row of metrics and each response columns thus making it 6 + 6 + 2 = 14 columns.
'''

def create_output_list(response_cols):

    global prediction_dict
    global prob_pos

    prob_pred = sorted(prob_pos, key=itemgetter('ts'))

    ts_list = sorted(prediction_dict.keys())
    output_list = [['timestamp','error'] + response_cols + ['p_e5', 'p_e10', 'p_e15', 'p_e20', 'p_e25', 'p_e30']]

    pred_prob_cols = ['p_e5', 'p_e10', 'p_e15', 'p_e20', 'p_e25', 'p_e30']

    for ts in ts_list:
        error = prediction_dict[ts]['error']
        temp = [ts,error]
        for col in response_cols:
            try:
                prediction = prediction_dict[ts][col]
            except:
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

'''
Writes the output list created in previous function (create_output_list) to a csv file.
'''

def write_output_list(output_list, filename):

    f = open(filename, 'w')
    writer = csv.writer(f, lineterminator="\n")
    writer.writerows(output_list)
    f.close()

'''
Function to initialize prediction dictionary. It reads the whole dataset for timestamp and error columns and then saves
them to a 2-D attay
'''

def init_prediction_dict_population(table, timestamp):

    global prediction_dict

    db = connect_PA_db()
    c = db.cursor()

    sql = "SELECT timestamp,error FROM {} WHERE timestamp >= '{}'".format(table, timestamp)
    c.execute(sql)

    results = [list(i) for i in c.fetchall()]

    for row in results:
        ts = row[0]
        error = row[1]
        prediction_dict[ts] = {'error':error}


def extract_timestamp_and_errors(table):

    db = connect_PA_db()
    c = db.cursor()

    sql = "SELECT timestamp,error FROM {} WHERE timestamp >= '2015-05-31 00:00' ORDER BY timestamp".format(table)
    c.execute(sql)

    results = [list(i) for i in list(c.fetchall())]
    return results

'''
Function to create predictions.
Input : Fitted RF model, predictor row, timestamp interval for which prediction is being done and prediction's response column
Recieves a fitted RF object and metric row (predictor row) amd used the fitted object to predict error
'''

def create_predictions(rf,test_predictors,ts_interval,col):

    global prediction_dict
    global prob_pos

    print '\t\tstarting predictions'
    pred_list = []
    prob_list = []
    now = datetime.datetime.now()
    print(ts_interval)
    row = test_predictors
    ts = ts_interval
    prediction = rf.predict(row)[0]
    prob = rf.predict_proba(row)
    pred_list.append(prediction)
    prob_list.append(prob)
    prob_pos.append({'ts' : ts, 'col' : col, 'prob' : prob, 'pred' : prediction})
    if (col == 'e_5' or col == 'e_10' or col == 'e_15' or col == 'e_20' or col == 'e_25' or col == 'e_30') and prediction == 1:
        print prediction, ts, col

    print '\t\tpredictions completed, Length of prediction set = {}\nTime took for predicting day = {}'\
        .format(len(prediction_dict), datetime.datetime.now() - now)

    return prediction

'''
RF is trained in following function.
Parameters (Can be tuned) :
No. of trees : 100
Criterion : Entropy
oob_score : True. (Remember out of bag errors to increase prediction accuraccy)
n_jobs : Number of jobs to be done in parallel.
Extend : Play with the above mentioned parameters in GridCV as discussed in CV function's description
'''

def create_and_train_rf(criterion,num_trees,train_predictors,train_responses, test_predictors):

    print '\t\tcreating random forest'
    rf = RandomForestClassifier(n_estimators = num_trees,criterion=criterion, oob_score=True, max_depth=10, n_jobs=4)
    print '\t\trandom forest created successfully'

    print '\t\ttraining random forest'
    fit = rf.fit(train_predictors,train_responses)
    print "RF Fitted"
    # score = rf.score(train_predictors, train_responses)

    # prob_pos = rf.predict_proba(test_predictors)

    print '\t\trandom forest successfully trained'

    return rf

'''
Used at iterator for testing purposes. Finds next date indeces for which prediction is to be done and passes it back to
main where the passed index are stored as startt and end index and used as iterator
'''
def find_next_date_indexes(start_date,stop_date,ts_list,dt_len):

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

'''
Function splits dataset into train and test set.
All data points till start index (index of 1st day of iteration) is train set.
Data between start and stop index are labeled as test data
'''

def split_train_test(predictors,responses,ts_list,start_index,stop_index, new_indeces):

    train_predictors = predictors[:start_index] + [predictors[new_indeces[i]] for i in range(len(new_indeces))]
    test_predictors = predictors[start_index:stop_index]

    train_responses = responses[:start_index] + [responses[new_indeces[i]] for i in range(len(new_indeces))]
    test_responses = responses[start_index:stop_index]

    ts_interval = ts_list[start_index:stop_index]

    return train_predictors,test_predictors,train_responses,test_responses,ts_interval

'''
Split the whole dataset into predictors and responses
'''

def split_predictors_and_responses(dataset,response_index,error_index):

    predictors = [i[:error_index] for i in dataset]
    responses = [i[response_index-1] for i in dataset]
    print response_index
    return predictors,responses

'''
Connects to db. Extracts response columns.
'''

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

'''
Execution starts from here. A time.sleep() is used to pause the program executoion for 5 min.
5min time interval is decided because new data is updated in PA db every 5min.
At end of 5min, if no new row was added, it again waits for 1 min till new row is added. Once added, it takes in new row
and used that a predictor to predictor its class.
'''

def start(end):
    now = datetime.datetime.now()
    print "Starts Here\n"
    start_date = end
    end_date = end + datetime.timedelta(minutes=5)
    for i in range(0,1):
        end_date = end_date + datetime.timedelta(days=i)
        fname = 'small_ds1_tse_temporal_lookback4_predictions_classBalance' + str('01_06') + '.csv'
        main('new_small_ds1_tse_temporal_lookback4_balanced',30,5,'gini',100,fname,start_date,end_date,i+1,
             end_date.strftime("%Y-%m-%d %H:%M:%S"))
    timeS = (datetime.datetime.now()-now).total_seconds()
    print(time, "Seconds for executing 5min interval")
    print("Seconds left for next function call ",300-timeS)

    time.sleep(int(300-timeS))
    sql = "SELECT * FROM new_small_ds1_tse_temporal_lookback4_balanced WHERE timestamp > '{}'".\
        format(end_date.strftime("%Y-%m-%d %H:%M:%S"))
    db = connect_PA_db()
    c = db.cursor()
    c.execute(sql)
    if c.fetchone() is None:
        print("Data not yet updated. Waiting 1 min more for data to be updated.")
        time.sleep(60)
        start(start_date + datetime.timedelta(minutes=5))
    else:
        print("Data present")
        start(start_date + datetime.timedelta(minutes=5))
    # sc.enter(300, 1, start(start_date + datetime.timedelta(minutes=5), sc), (sc,))

if __name__ == '__main__':
    counter()
