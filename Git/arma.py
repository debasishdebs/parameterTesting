from __future__ import print_function
import statsmodels.api as sm
import csv, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymysql
import datetime

def openCSV(filename):
	lines = csv.reader(open(filename, "rt"))
	dataset = list(lines)
	return dataset


def ARMA(data, datatimes, startTime):

	data = pd.TimeSeries(data, index = datatimes)

	arma_mod30 = sm.tsa.ARMA(data, (3,0)).fit(solver = 'bfgs', disp = 0)

	predict_dataset = arma_mod30.predict(startTime, (len(data) + 60), dynamic=True)
	#print(predict_dataset)
	predict_dataset.to_csv("predicted.csv")



	return(predict_dataset)

def detrend(armaForecast):
	print ("DETRENDING DATA")
	
	dataset = openCSV("original_data.csv")
	#armaForecast = openCSV("predict_dataset3.csv")

	detrendedData = []
	x = []
	y = []

	for j in armaForecast:
		for i in dataset:
			if i[0] == dataset[int(j[0])][0]:
				k = 1
				while k < len(armaForecast[0]):
					detrended = []
					detrended.append(i[0])
					x.append(i[0])
					y.append(int(i[k]) - float(j[k]))

					detrended.append(i[k])
					detrended.append(j[k])
					detrended.append(int(i[k]) - float(j[k]))
					k += 1
				detrendedData.append(detrended)
	print("DONE DETRENDING")
	data = pd.TimeSeries(y, index = x)
	#data.plot()

	f = open("deterendedData3.csv",'a')
	writer = csv.writer(f,lineterminator = "\n")
	writer.writerows(detrendedData)
	f.close()
	return detrendedData


def testARMA():
	
	db = pymysql.connect(host = "11.120.236.206", db = "mcom_metrics", user = "internship", passwd = "Pr3dict!v@")
	c = db.cursor()
	print('CONNECTED TO DATABASE')
	c.execute("SELECT timestamp,count FROM rt_orders_min_hist WHERE type = 'RCMPL' AND timestamp > %s ORDER BY timestamp", datetime.datetime(2013,12,1,0,0))
	results = c.fetchall()
	results = list(results)
	c.execute("SELECT timestamp,count FROM rt_orders_min WHERE type = 'RCMPL' ORDER BY timestamp")
	results2 = c.fetchall()
	results2 = list(results2)
	print('DONE GATHERING DATA')

	x1 = [i[1] for i in results]
	x2 = [i[1] for i in results2]
	y1 = [i[0] for i in results]
	y2 = [i[0] for i in results2]

	x = x1 + x2
	y = y1 + y2

	data = pd.TimeSeries(x, index = y)
	data.to_csv("original_data.csv")

	f = open("predict_dataset3.csv",'a')
	writer = csv.writer(f,lineterminator = "\n")

	k = 1
	i = 0
	testX = []
	testY = []
	print (len(y))
	while i < len(y):
		current = y[i] + datetime.timedelta(weeks = 4)
		#print (current)
		
		while y[k] < current:
			#print("while loop")
			#print(y[k])
			#print(current)

			testX.append(x[k])
			testY.append(y[k])
			k += 1

		if y[k] == current:
			testX.append(x[k])
			testY.append(y[k])
			k += 1
			print("PREDICTING DATA")
			predicted = ARMA(testX, testY, current)
			i += 32
			print("DONE PREDICTING")
			armaForecast = openCSV("predicted.csv")
			#writer.writerows(armaForecast)
			detrend(armaForecast)
			if i > 200:
				break

		elif y[k] > current:
			i += 1
		print(i)

	
	data = pd.TimeSeries(x, index = y)
	f.close()
	data.to_csv("original_data.csv")
	#detrend()

	#fig, ax = plt.subplots(figsize=(10,8))
	#fig = arma_mod30.plot_predict(datetime.datetime(2015,7,1,2,0), dynamic=True, ax=ax, plot_insample=False)
def predictARMA():
	time = datetime.datetime.now().replace(second = 0).replace(microsecond = 0) - datetime.timedelta(minutes = 2)
	print(time)
	db = pymysql.connect(host = "11.120.236.206", db = "mcom_metrics", user = "internship", passwd = "Pr3dict!v@")
	c = db.cursor()
	print('CONNECTED TO DATABASE')
	c.execute("SELECT timestamp,count FROM rt_orders_min_hist WHERE type = 'RCMPL' AND timestamp > %s ORDER BY timestamp", datetime.datetime(2013,12,1,0,0))
	results = c.fetchall()
	results = list(results)
	c.execute("SELECT timestamp,count FROM rt_orders_min WHERE type = 'RCMPL' ORDER BY timestamp")
	results2 = c.fetchall()
	results2 = list(results2)
	print('DONE GATHERING DATA')

	x1 = [i[1] for i in results]
	x2 = [i[1] for i in results2]
	y1 = [i[0] for i in results]
	y2 = [i[0] for i in results2]

	x = x1 + x2
	y = y1 + y2

	data = pd.TimeSeries(x, index = y)
	data.to_csv("original_data.csv")

	ARMA(x, y, time)


predictARMA()

