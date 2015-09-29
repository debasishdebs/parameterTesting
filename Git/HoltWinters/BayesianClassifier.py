import csv, os
import random
import math, MySQLdb
from dbCon import dbReturnError, dbReturnPredictors, savePredictions, dbReturnDataSet
global dbCred
dbCred = {'ip': '11.120.36.241', 'user': 'internship', 'pass': 'Pr3dict!v@', 'db': 'predictiveAnalytics'}

#Load CSV file in Workspace
def loadCsv(filename):
    lines = csv.reader(open(filename, "rt"))
    dataset = list(lines)
    #data = [0]*len(dataset)
    for i in range(len(dataset)):
    	dataset[i] = [float(x) for x in dataset[i]]
##    	data[i][0] = dataset[i][0]
##    	data[i][1] = dataset[i][1]
##    	data[i][2] = dataset[i][3]
    	#print(dataset[i])
    return dataset

def writeToCSV(csvColumns, datas):
    print(datas[10])
    try:
        with open('resources\predictors.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = csvColumns, lineterminator='\n')
            #writer.writeheader()
            for data in datas:
                #print(data)
                writer.writerow(data)
    except IOError as xxx_todo_changeme:
        (errno, strerror) = xxx_todo_changeme.args
        print(("I/O error({0}):{1}".format(errno, strerror)))
    return

#SplitDataset with pre defined ratio into training set & testing set.
def splitDataset(dataset,splitRatio):
    trainSize = int(len(dataset)*splitRatio)
    trainSet = []
    testSet = list(dataset)
    #file = dbReturnDataSet()
    while len(trainSet) < trainSize:
        index = random.randrange(len(testSet))
        trainSet.append(testSet.pop(index))
    return [trainSet, testSet]

def separateByClass(dataset):
    separated = {}
    for i in range(len(dataset)):
        vector = dataset[i]
        if (vector[-1] not in separated):
            separated[vector[-1]] = []
        separated[vector[-1]].append(vector)
    return separated

def mean(numbers):
    return sum(numbers)/float(len(numbers))

#Standard Deviation function
def stdev(numbers):
    avg = mean(numbers)   
    variance = sum([pow(x-avg,2) for x in numbers])/float(len(numbers)-1)
    return math.sqrt(variance)

def summarize(dataset):
    summaries = [(mean(attribute),stdev(attribute)) for attribute in zip(*dataset)]
    del summaries[-1]
    return summaries

#Summarize the whole dataset according to their respective classes, i.e. Error or No error
def summarizeByClass(dataset):
    separated = separateByClass(dataset)
    summaries = {}
    for classValue, instances in list(separated.items()):
        summaries[classValue] = summarize(instances)
    return summaries

#Gaussian Probability function
def calculateProbability(x,mean,stdev):
    exponent = math.exp(-(math.pow(x-mean,2)/(2*math.pow(stdev,2))))
    return (1/(math.sqrt(2*math.pi)*stdev))*exponent

#For specific input vector(particular set/row of metrics) find the probability of it belonging to all Classes specified
def calculateClassProbabilities(summaries, inputMatrix):
    probabilities = {}
    for classValue, classSummaries in list(summaries.items()):
        probabilities[classValue] = 1
        for j in range(len(classSummaries)):
                mean, stdev = classSummaries[j]
                x = inputMatrix[j]
                probabilities[classValue] *= calculateProbability(x,mean,stdev)
    return probabilities

def calculateClassProb(summaries, inputMatrix):
    probabilities = [dict() for x in range(len(inputMatrix))]
    for classValue, classSummaries in list(summaries.items()):
        for i in range(len(inputMatrix)):
            probabilities[i][classValue] = 1
            for j in range(len(classSummaries)):
                mean, stdev = classSummaries[j]
                x = inputMatrix[i][j]
                probabilities[i][classValue] *= calculateProbability(x,mean,stdev)
    return probabilities

#Predict a particulat testSet row to belong to which class
def predict(summaries, testVector):
    probabilities = calculateClassProbabilities(summaries, testVector)
    bestLabel, bestProb = None, -1
    for classValue, probability in list(probabilities.items()):
        if bestLabel is None or probability > bestProb:
            bestProb = probability
            bestLabel = classValue
    return bestLabel

def getPredictions(summaries, testSet):
    predictions = []
    predictionSet = []
    for i in range(len(testSet)):
        result = predict(summaries, testSet[i])
        predictions.append(result)
        predictionSet.append(testSet[i])
    return predictions, predictionSet

#Get accuraccy of Predictions
def getAccuracy(testSet, predictions):
    correct = 0
    for x in range(len(testSet)):
        if testSet[x][-1] == predictions[x]:
            correct +=1
    print(correct)
    return (correct/float(len(testSet)))*100.0

def Bayesian_main():
    predictors, csvColumn = dbReturnPredictors()
    print(csvColumn)
    print(predictors[10])
    filename = 'resources\predictors.csv'
    writeToCSV(csvColumn, predictors)
    print("Saved to DB")
    dataset = loadCsv(filename)
    print(('Loaded data file {0} with {1} rows'.format(filename, len(dataset))))
    splitRatio = 0.75
    #print(type(train),type(test))
    train, test = splitDataset(dataset, splitRatio)
    #train = splitDataset(train,splitRatio)
    #train, test = dbReturnDataSet(dbCred)
    print(('Split {0} rows into train with {1} and test with {2}'.format(len(dataset),len(train),len(test))))
    inputMatrix = [[0 for x in range(3)] for x in range(len(test))]
    #print(train[2],test[4])
    #print(inputMatrix[1][0])
    #print(range(len(test)))
    for x in range(len(test)):
          inputMatrix[x][0] = test[x][0]
          inputMatrix[x][1] = test[x][1]
          inputMatrix[x][2] = '?'
    #print(inputMatrix[1])
    separated = separateByClass(dataset)
    attrSummary = summarize(dataset)
    print(('Attribute summaries: {0}'.format(attrSummary)))
    summary = summarizeByClass(dataset)
    print(('Summary by class value: {0}'.format(summary)))
    probabilities = calculateClassProb(summary, inputMatrix)
    #print('Probabilities for each class: {0}'.format(len(probabilities)))
    predictions, predictionSet = getPredictions(summary,inputMatrix)
    #print('Predictions: {0}'.format(predictions))
    savePredictions(predictions, predictionSet, csvColumn)
    accuracy = getAccuracy(test,predictions)
    print(('Accuracy: {0}'.format(accuracy)))
    print("Now Predicting with Forecasted Metrics")
    summary = summarizeByClass(dataset)
    probabilities = calculateClassProb(summary, forecastTest)
    predictions, predictionSet = getPredictions(summary,forecastTest)
    print("Predictions ", predictions)

Bayesian_main()
