from __future__ import division
from sklearn.ensemble import RandomForestClassifier
import pymysql
import datetime
import csv
from operator import itemgetter
from sklearn.metrics import *
from algoScores import get_algo_scores
import sys

f = open('output.txt', 'w')
sys.stdout = f

finalData = []
prediction_dict = {}
prob_pos = []
pred_prob = {}

def connect_PA_db():
    db = pymysql.connect(host = "127.0.0.1", db = "predictiveanalytics", user = "root", passwd = "")
    return db


def main(table,lookahead,interval,criterion,num_trees,filename,start_date, stop_date,dt_len):

    global finalData

    db = connect_PA_db()
    c = db.cursor()

##    table = raw_input("Enter Table Name: ")
##    timeSpan = raw_input("How far out do you want predictions in minutes? ")
##    timeSpan = int(timeSpan)
##    timeInterval = raw_input("How large is the time interval? ")
##    timeInterval = int(timeInterval)
##    chosenCriterion = raw_input("What type of criterion do you want? ")
##    numberOfTrees = int(raw_input("How many trees do you want? "))
##    csvFileName = raw_input("What do you want to name the CSV file? ")
    
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

    print 'Start initial population of prediction dictionary'
    init_prediction_dict_population(table)
    print 'Initial population complete'

    global prediction_dict
    global pred_prob

    start = start_date
    stop = stop_date
    score = [[] for i in range(6)]
    
    for i in range(len(response_index_list)):

        response = response_index_list[i]
        col = response_cols[i]
        print col
                
        predictors,responses = split_predictors_and_responses(data,response,error_index)

##        start_date = datetime.datetime(2015,5,1,0,0)
##        stop_date = datetime.datetime(2015,5,2,0,0)

        start_date = start
        stop_date = stop
        
        start_index = ts_list.index(start_date)
        stop_index = ts_list.index(stop_date)

        print '\tInitializing simulation of the following time interval:'
        print '\tstart date: {}'.format(start_date)
        print '\tend date: {}'.format(stop_date)
        
        
        #while start_index < len(data) and stop_index < len(data):
        while start_index < len(data)-1 and stop_index < len(data)-1 and start_date < max_ts and stop_date < max_ts:
            train_predictors,test_predictors,train_responses,test_responses,ts_interval = split_train_test(predictors,responses,ts_list,start_index,stop_index)
            
            rf, scor, prob = create_and_train_rf(criterion,num_trees,train_predictors,train_responses, test_predictors)
            score[i].append(scor)
            #prob_pos[i][start_date] = {'date' : start_date, 'col' : col, 'prob' : prob}
            create_predictions(rf,test_predictors,ts_interval,col)
                
            start_index,stop_index = find_next_date_indexes(start_date,stop_date,ts_list,dt_len)
            start_date = ts_list[start_index]
            stop_date = ts_list[stop_index]

            if start_date >= max_ts or stop_date >= max_ts:
                break
    #print score
    #scores = getScores()
##    print len(scores), len(scores[0])
##    for i in range(len(scores[0])):
##        print scores[0][i], "- Score"
##    print len(prob_pos)

    pred_prob = getPredScore()

##    for i in range(len(pred_prob['e_5'])):
##        print "Prediction : {0}, Probability of Prediction class : {1} ".format(pred_prob['e_5'][i][0],pred_prob['e_5'][i][1])

    print '\nExperiment completed'
    print 'Creating output csv file'
    output_list = create_output_list(response_cols)
    print len(prediction_dict), type(prediction_dict)
    write_output_list(output_list,prediction_dict,filename)

    get_algo_scores(filename)
    f.close()

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

##    for i in range(2):
##        prob_preds_e5[i].append([])
##        prob_preds_e10[i].append([])
##        prob_preds_e15[i].append([])
##        prob_preds_e20[i].append([])
##        prob_preds_e25[i].append([])
##        prob_preds_e30[i].append([])
##        

    prob_pred = sorted(prob_pos, key=itemgetter('ts'))
    
    for i in range(len(prob_pred)):
        #print prob_pred[i]['col']
        if prob_pred[i]['col'] == 'e_5':
            prediction = prob_pred[i]['pred']
            prediction_prob_cl = prob_pred[i]['prob'] if (prediction == 1) else (1-prob_pred[i]['prob'])
            prob_preds_e5[0].append(prediction)
            prob_preds_e5[1].append(float(prediction_prob_cl[:,int(prediction)][0]))
            #print prob_preds_e5
        if prob_pred[i]['col'] == 'e_10':
            prediction = prob_pred[i]['pred']
            prediction_prob_cl = prob_pred[i]['prob'] if (prediction == 1) else (1-prob_pred[i]['prob'])
            prob_preds_e10[0].append(prediction)
            prob_preds_e10[1].append(float(prediction_prob_cl[:,int(prediction)][0]))
        if prob_pred[i]['col'] == 'e_15':
            prediction = prob_pred[i]['pred']
#            if prediction == 1:
#                print prediction
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

    #print prob_preds
    
    return prob_preds

def create_output_list(response_cols):

    global prediction_dict
    global prob_pos

    prob_pred = sorted(prob_pos, key=itemgetter('ts'))

    ts_list = sorted(prediction_dict.keys())
    output_list = [['timestamp','error']+response_cols+['p_e5', 'p_e10', 'p_e15', 'p_e20', 'p_e25', 'p_e30']]

    pred_prob_cols = ['p_e5', 'p_e10', 'p_e15', 'p_e20', 'p_e25', 'p_e30']

        
    for ts in ts_list:
        error = prediction_dict[ts]['error']
        temp = [ts,error]
        for col in response_cols:
            try:
                prediction = prediction_dict[ts][col]
                temp.append(prediction)
            except:
                continue
        for pCol in response_cols:
            for i in range(len(prob_pred)):
#                flag = 1
                if prob_pred[i]['ts'] == ts and prob_pred[i]['col'] == pCol:
                    prediction = prob_pred[i]['pred']
                    posClsProb = prob_pred[i]['prob'][:,int(prediction)][0] if (prediction == 1) else (1-prob_pred[i]['prob'][:,int(prediction)][0])
                    temp.append(posClsProb)
#            if flag == 1:
#                flag = 0
#                break

        if len(temp) != len(response_cols)+8:
            continue
        else:
            output_list.append(temp)
        

    return output_list

def write_output_list(output_list,prediction_dict,filename):

    f = open(filename,'w')
    writer = csv.writer(f,lineterminator = "\n")
    writer.writerows(output_list)
    f.close()

def init_prediction_dict_population(table):

    global prediction_dict

    db = connect_PA_db()
    c = db.cursor()

    sql = "SELECT timestamp,error FROM {} WHERE timestamp >= '2015-05-01 00:00' ORDER BY timestamp".format(table)
    c.execute(sql)

    results = [list(i) for i in c.fetchall()]

    for row in results:
        ts = row[0]
        error = row[1]
        prediction_dict[ts] = {'error':error}
            

def extract_timestamp_and_errors(table):

    db = connect_PA_db()
    c = db.cursor()

    sql = "SELECT timestamp,error FROM {} WHERE timestamp >= '2015-05-01 00:00' ORDER BY timestamp".format(table)
    c.execute(sql)

    results = [list(i) for i in list(c.fetchall())]
    return results

def create_predictions(rf,test_predictors,ts_interval,col):

    global prediction_dict
    global prob_pos

    print '\t\tstarting predictions'
    pred_list = []
    prob_list = []
    for i in range(len(test_predictors)):
        row = test_predictors[i]
        ts = ts_interval[i]
        prediction = rf.predict(row)[0]
        #print len(rf.predict_proba(row))
        #print prediction.size
        prob = rf.predict_proba(row)
        pred_list.append(prediction)
        prob_list.append(prob)
        prob_pos.append({'ts' : ts, 'col' : col, 'prob' : prob, 'pred' : prediction})
        if col == 'e_15' and prediction == 1:
            print prediction
        prediction_dict[ts][col] = prediction
    print '\t\tpredictions completed, Length of prediction set = {}'.format(len(prediction_dict))

    return pred_list, prob_list


def create_and_train_rf(criterion,num_trees,train_predictors,train_responses, test_predictors):

    print '\t\tcreating random forest'
    rf = RandomForestClassifier(n_estimators = num_trees,criterion=criterion)
    print '\t\trandom forest created successfully'

    print '\t\ttraining random forest'
    fit = rf.fit(train_predictors,train_responses)
    score = rf.score(train_predictors, train_responses)
##    prob_pos_0 = rf.predict_proba(test_predictors)[:,0]
##    prob_pos_1 = rf.predict_proba(test_predictors)[:,1]
    #print test_predictors
    prob_pos = rf.predict_proba(test_predictors)
##    print "Score - {0} , Length of Prob_pos : {1} , And its Type : {2} ".format(score, len(prob_pos), type(prob_pos))
##    print " prob_pos[0] : {0} ,  prob_pos_0[0] : {1},  prob_pos_1[0] : {2}".format( prob_pos[0], prob_pos_0[0], prob_pos_1[0])
##    print " prob_pos[1] : {0}, prob_pos_0[1] : {1}, prob_pos_1[1] : {2} ".format(prob_pos[1],prob_pos_0[1],prob_pos_1[1])
    
    print '\t\trandom forest successfully trained'

    return rf, score, prob_pos
    
        
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
        
        
def split_train_test(predictors,responses,ts_list,start_index,stop_index):

     train_predictors = predictors[:start_index]
     test_predictors = predictors[start_index:stop_index]

     train_responses = responses[:start_index]
     test_responses = responses[start_index:stop_index]

     ts_interval = ts_list[start_index:stop_index]
    
     return train_predictors,test_predictors,train_responses,test_responses,ts_interval
    
    
def split_predictors_and_responses(dataset,response_index,error_index):
    
    predictors = [i[:error_index] for i in dataset]
    responses = [i[response_index-1] for i in dataset]
    
    return predictors,responses
    
        
def find_responses(table):
    
    db = connect_PA_db()
    c = db.cursor()
    
    sql = "SHOW COLUMNS FROM {}".format(table)
    c.execute(sql)
    
    cols = [i[0] for i in c.fetchall()]
    print cols
    error_index = cols.index("error")
    #num_responses = (len(cols[error_index:])-1)//2
    num_responses = len(cols[error_index:])-1
    print 'Number of responses found: {}'.format(num_responses)
    #response_cols = cols[error_index+1:len(cols)-num_responses]
    response_cols = cols[error_index+1:]
    print 'Response columns: {}'.format(response_cols)

    response_index_list = []
    
    for col in response_cols:
        response_index_list.append(cols.index(col))
    print 'Response column indexes: {}'.format(response_index_list)
    
    return response_index_list,error_index,response_cols
        
def start():
    print "Starts Here\n"
    start_date = datetime.datetime(2015,5,1,0,0)
    end_date = datetime.datetime(2015,5,2,0,0)
    for i in range(0,1):
        end_date = end_date + datetime.timedelta(days=i)
        fname = 'small_ds1_tse_temporal_lookback4_predictions_' + str(i+20) + '.csv'
        main('new_small_ds1_tse_temporal_lookback4',30,5,'entropy',50,fname,start_date,end_date,i+1)

#start()