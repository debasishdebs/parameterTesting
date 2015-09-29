
from sklearn.ensemble import RandomForestClassifier
import pymysql
import datetime
import csv

global data 

def connect_PA_db():
    db = pymysql.connect(host = "11.120.36.241", db = "predictiveAnalytics", user = "internship", passwd = "Pr3dict!v@")
    return db

"""
    Creates Random Forest that cases will be tested on.
    Input:
        train_set_x: Metrics at given time intervals
        train_set_y: Known responses/answers to the metrics
    Output:
        model_fit: Created forest of the random trees trained off
        training sets
"""
def trainRandomForest(train_set_x, train_set_y, chosenCriterion, numberOfTrees):
    #maybe change number of trees
    model = RandomForestClassifier(n_estimators=numberOfTrees, criterion = chosenCriterion) #creates RF
    model_fit = model.fit(train_set_x, train_set_y) #trains it to given data
    #transform = model.fit_transform(train_set_x, train_set_y)
    #model_fit_transform = model.fit(transform, train_set_y)
    return model_fit

"""
    Creates Prediciton off of given random forest and test set
    Input:
        randomForest: Random forest created in trainRandomForest()
        test_set: what you want to know the answer to
    Output:
        Nested Array: Contains the array of prediction result(1 or 0) and the
        array of probabilty that this is acurate
"""
def randomForestPrediction(randomForest,test_set):
    prediction = randomForest.predict(test_set) #creates array of predictions
    probability = randomForest.predict_proba(test_set) #creats array of the probabilty of those predictions
    return [prediction, probability]

"""
    Calculates the accuracy of the results on a test set the anwsers
    are know to. Additionaly inputs the prediciton result in to a database.
    USED FOR TESTING PURPOSES ONLY
    Input:
        randomForest: Random forest created in trainRandomForest()
        testing_set: set that predictions will be made off of, actual answers
        should be know to get accuracy
        current_run: which error run it is on
    Output:
        Array: Contains accuracy results
"""
def randomForestAccuracy(randomForest, testing_set, current_run, timeSpan, table):
	global data
	print ('Getting Accuracy')
	#db = connect_PA_db() #connects to Predictive analytics database
	#c = db.cursor()
	#passes over every row in testing set
	for row in testing_set:
	    # print row[1:]
	    predicted_result = randomForest.predict(row[1:]) #gets prediction for given row
	    probability = randomForest.predict_proba(row[1:])

	    error_column = (timeSpan + 5)  + current_run*5 				#calculates error column
	    col = "p_" + str(error_column)
		#creates, executes, and commits sql statements
		#sql = "UPDATE {} SET {} = {} WHERE timestamp = %s".format(table, col, predicted_result[0])
		#print(sql)
		#print(row[0])
		#c.execute(sql,(row[0]))
		#db.commit()
		#average_time += time.time()-start_time
        if len(finalData) == 0:
			subdata = []
			subdata.append(row[0])
			subdata.append(predicted_result[0])
			finalData.append(subdata)
	    else:
			i = 0
			found = False
			while i < len(finalData) and not found:
				if finalData[i][0] == row[0]:
					finalData[i].append(predicted_result[0])
					found = True
				i += 1
			if not found:
				subdata = []
				subdata.append(row[0])
				subdata.append(predicted_result[0])
				finalData.append(subdata)


"""
    Tests all known data by spliting it into sections and using that
     to test it against itself
     Input:
         data_set: This is all data being tested
         num_of_splits: how many sections the data will be split into
         current_run: Which error run it is on
    Output:
        results_list: list of list holding all the accuracy ratings
"""
def test(data_set, num_of_splits, current_run, timeSpan, table, chosenCriterion, numberOfTrees):
	print ('Testing Data')
	results_list = []
	test_set_len = int(len(data_set)/num_of_splits) #gets lenght of testing set
	train_set_len = len(data_set) - test_set_len #gets lenght of training set

	for i in range(70): #range is how many days we want to go backwards and test
	        print i
	        test_set = data_set[test_set_len*i:test_set_len*(i+1)]
	        train_set = []
	        #grabs the rows from the data set that will be trained on
	        for row in data_set:
	                if row not in test_set:
	                        train_set.append(row)
	        #splits into factors and answers
	        train_set_x = [i[1:-2] for i in train_set]
	        
	        train_set_y = [i[-1] for i in train_set]

	        test_set = [i[0:-2] for i in test_set]
	        #calls random forrest
	        print("Creating Random Forest")
	        rf = trainRandomForest(train_set_x, train_set_y, chosenCriterion, numberOfTrees)


	        #gets accuracy for test_set with created RF
	        randomForestAccuracy(rf, test_set, current_run, timeSpan, table)
"""
    Splits dataset so one error set is seen at a time
    Input:
        dataset: the whole dataset pulled from database
        index: which error we are on
    Output:
        new_data: array of dataset with only one error in it
"""
def init_split(dataset, index, responseNumber):
	print("Splitting Data")
	new_data = []
	index -=responseNumber
	print(index)
	predictors = [row[:index] for row in dataset]
	response = [row[index] for row in dataset]
	for j in range(len(dataset)):
	        temp = list(predictors[j]) + [response[j]]
	        new_data.append(temp)
	return new_data

"""
    main method to run it all.
"""
def main():
	global finalData

	finalData = []

	db = connect_PA_db() #connects to database
	c = db.cursor()
	#creates and executes SQL

	table = raw_input("Enter Table Name: ")
	sql = ("SELECT * FROM {} ORDER BY timestamp DESC").format(table)
	c.execute(sql)
	timeSpan = raw_input("How far out do you want predictions in minutes? ")
	timeSpan = int(timeSpan)
	timeInterval = raw_input("How large is the time interval? ")
	timeInterval = int(timeInterval)
	chosenCriterion = raw_input("What type of criterion do you want? ")
	numberOfTrees = int(raw_input("How many trees do you want? "))
	csvFileName = raw_input("What do you want to name the CSV file? ")

	timeSpan = int(timeSpan)
	timeInterval = int(timeInterval)
	numberOfTrees = int(numberOfTrees)
        
	#fetches data, parses to list format, and sorts data by reverse
	data = list(c.fetchall())
	data.sort(reverse = True)
	print len(data)
	number_of_responses = timeSpan/timeInterval
	print (number_of_responses)
	num_splits = len(data)/288
	#calls methods and prints results
	for i in range(-number_of_responses, 0, 1):
	        print i
	        test(init_split(data, i, number_of_responses), num_splits, i, timeSpan, table, chosenCriterion, numberOfTrees)

	f = open(csvFileName,'w')
	writer = csv.writer(f,lineterminator = "\n")
	writer.writerows(finalData)
	f.close()


main()

