from __future__ import division
from sklearn.ensemble import RandomForestClassifier
import pymysql
import datetime
import csv

finalData = []
prediction_dict = {}

def connect_PA_db():
    db = pymysql.connect(host = "11.120.36.241", db = "predictiveAnalytics", user = "internship", passwd = "Pr3dict!v@")
    return db


def main(table,lookahead,interval,criterion,num_trees,filename):

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

    for i in range(len(response_index_list)):

        response = response_index_list[i]
        col = response_cols[i]
        print col
                
        predictors,responses = split_predictors_and_responses(data,response,error_index)

        start_date = datetime.datetime(2015,5,1,0,0)
        stop_date = datetime.datetime(2015,5,2,0,0)
        
        start_index = ts_list.index(start_date)
        stop_index = ts_list.index(stop_date)

        print '\tInitializing simulation of the following time interval:'
        print '\tstart date: {}'.format(start_date)
        print '\tend date: {}'.format(stop_date)
        
        
        #while start_index < len(data) and stop_index < len(data):
        while start_index < len(data)-1 and stop_index < len(data)-1 and start_date < max_ts and stop_date < max_ts:
            train_predictors,test_predictors,train_responses,test_responses,ts_interval = split_train_test(predictors,responses,ts_list,start_index,stop_index)
            
            rf = create_and_train_rf(criterion,num_trees,train_predictors,train_responses)    
            create_predictions(rf,test_predictors,ts_interval,col)
                
            start_index,stop_index = find_next_date_indexes(start_date,stop_date,ts_list)
            start_date = ts_list[start_index]
            stop_date = ts_list[stop_index]

            if start_date >= max_ts or stop_date >= max_ts:
                break
            
            
    print '\nExperiment completed'
    print 'Creating output csv file'
    output_list = create_output_list(response_cols)
    write_output_list(output_list,filename)
    


def create_output_list(response_cols):

    global prediction_dict
    ts_list = sorted(prediction_dict.keys())
    output_list = [['timestamp','error']+response_cols]

        
    for ts in ts_list:
        error = prediction_dict[ts]['error']
        temp = [ts,error]
        for col in response_cols:
            try:
                prediction = prediction_dict[ts][col]
                temp.append(prediction)
                
            except:
                print ts,col
                continue
        if len(temp) != len(response_cols)+2:
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

    print '\t\tstarting predictions'
    error_dict = {}
    for i in range(len(test_predictors)):
        row = test_predictors[i]
        ts = ts_interval[i]
        prediction = rf.predict(row)[0]
        prediction_dict[ts][col] = prediction
    print '\t\tpredictions completed'

    return error_dict


def create_and_train_rf(criterion,num_trees,train_predictors,train_responses):

    print '\t\tcreating random forest'
    rf = RandomForestClassifier(n_estimators = num_trees,criterion=criterion)
    print '\t\trandom forest created successfully'

    print '\t\ttraining random forest'
    rf.fit(train_predictors,train_responses)
    print '\t\trandom forest successfully trained'

    return rf
    
        
def find_next_date_indexes(start_date,stop_date,ts_list):

    start_date_next = start_date.replace(minute=0) + datetime.timedelta(days = 1)
    stop_date_next = stop_date.replace(minute=0) + datetime.timedelta(days = 1)

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
        
main('small_ds1_tse_temporal_lookback2',30,5,'entropy',200,'small_ds1_tse_temporal_lookback2_predictions.csv')
