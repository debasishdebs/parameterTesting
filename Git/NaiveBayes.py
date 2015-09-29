import numpy as np
from sklearn.naive_bayes import GaussianNB
import pymysql
import datetime
import copy



class NaiveBayes:
	def __init__(self):
		self.nb5 = GaussianNB()
		self.nb10 = GaussianNB()
		self.nb15 = GaussianNB()
		self.nb20 = GaussianNB()
		self.nb30 = GaussianNB()
		self.nb35 = GaussianNB()
		self.nb40 = GaussianNB()
		self.nb45 = GaussianNB()
		self.nb50 = GaussianNB()
		self.nb55 = GaussianNB()
		self.nb60 = GaussianNB()
		self.true_positive = 0
		self.false_positive = 0
		self.true_negative = 0
		self.false_negative = 0
		self.length = 0
		self.completeData = []
		self.main()
		

	def connect_PA_db(self):
	    db = pymysql.connect(host = "11.120.36.241", db = "predictiveAnalytics", user = "internship", passwd = "Pr3dict!v@")
	    return db
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
	def accuracy(self, predicted_result, acutal_result):
		predictedResult = predicted_result
		self.length += 1
		if predictedResult == 1 and acutal_result == 1:
		        self.true_positive += 1
		if predictedResult == 1 and acutal_result == 0:
		        self.false_positive += 1
		if predictedResult == 0 and acutal_result == 0:
		        self.true_negative += 1
		if predictedResult == 0 and acutal_result == 1:
		        self.false_negative += 1
	  
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
	def test(self, gaussianNB, dataset):
		data = []
		x = [i[0:4] for i in dataset]
		y = [i[-1] for i in dataset]
		k = 1
		i = 0
		print (len(y))
		while i < len(y):
			current = x[i][0] + datetime.timedelta(days = 365)
			print (x[i][0])
			print (current)
			
			while x[k][0] < current:
				trainX = []
				trainY = []

				trainX.append(x[k][1:])
				trainY.append(y[k])
				k += 1

			if x[k][0] == current:
				trainX.append(x[k][1:])
				trainY.append(y[k])
				k += 1
				print("PREDICTING DATA")
				nbFitted = gaussianNB.partial_fit(trainX,trainY, [0,1])
				j = 1
				while j <= 288:
					prediction = nbFitted.predict(x[k+j][1:])

					print (prediction[0])
					if self.completeData[k+j][0] == x[k+j][0]:
						self.completeData[k+j].append(prediction[0])
						accuracy(prediction[0], x[k+j][-1])
					else:
						for l in self.completeData:
							if l[0] == x[k+j][0]:
								self.completeData[k+j].append(prediction[0])
								accuracy(prediction[0], x[k+j][-1])
							else:
								print("Could not find match on: ")
								print(x[k+j][0])
				i += 288
				print("DONE PREDICTING")
	
			elif x[k][0] > current:
				i += 1
			print(i)
		return dataset
	"""
	    Splits dataset so one error set is seen at a time
	    Input:
	        dataset: the whole dataset pulled from database
	        index: which error we are on
	    Output:
	        new_data: array of dataset with only one error in it
	"""
	def init_split(self, dataset, index):
	    new_data = []
	    index -= 12
	    predictors = [row[:index] for row in dataset]
	    response = [row[index] for row in dataset]
	    for j in range(len(dataset)):
	            temp = list(predictors[j]) + [response[j]]
	            new_data.append(temp)
	    return new_data

	"""
	    main method to run it all.
	"""
	def main(self):
		print ('here')
	
		db = self.connect_PA_db() #connects to database
		c = db.cursor()
		#creates and executes SQL
		sql = ("SELECT * FROM learning_set1 ORDER BY timestamp")
		c.execute(sql)
		#fetches data, parses to list format, and sorts data by reverse
		data = list(c.fetchall())
		self.completeData = copy.deepcopy(data)
		#data.sort(reverse = True)
		print len(data)
		number_of_responses = 12
		total_results_list = []
		print
		nb5Results = self.test(self.nb5,self.init_split(data,-12))
		nb10Results = self.test(self.nb10,self.init_split(data,-11))
		nb15Results = self.test(self.nb15,self.init_split(data,-10))
		nb20Results = self.test(self.nb20,self.init_split(data,-9))
		nb25Results = self.test(self.nb25,self.init_split(data,-8))
		nb30Results = self.test(self.nb30,self.init_split(data,-7))
		nb35Results = self.test(self.nb35,self.init_split(data,-6))
		nb40Results = self.test(self.nb40,self.init_split(data,-5))
		nb45Results = self.test(self.nb45,self.init_split(data,-4))
		nb50Results = self.test(self.nb50,self.init_split(data,-3))
		nb55Results = self.test(self.nb55,self.init_split(data,-2))
		nb60Results = self.test(self.nb60,self.init_split(data,-1))
		f = open("GaussianNBResults.csv",'a')
		writer = csv.writer(f,lineterminator = "\n")
		writer.writerows(self.completeData)
		f.close()
		 
		print ("True Positive:")
		print (true_positive/float(length))
		print ("False Positive:")
		print (false_positive/float(length))
		print ("True Negative:")
		print (true_negative/float(length))
		print ("False Negative:")
		print (false_negative/float(length))



NaiveBayes()