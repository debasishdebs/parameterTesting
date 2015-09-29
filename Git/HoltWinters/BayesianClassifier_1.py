import csv, os
import random
<<<<<<< .merge_file_a16188
import math
=======
import math, pymysql
>>>>>>> .merge_file_a08344
import datetime
import copy
from dateutil.parser import parse
#from dbCon import dbReturnError, dbReturnPredictors, savePredictions

#Load CSV file in Workspace
def loadCsv(filename):
    lines = csv.reader(open(filename, "rt"))
    dataset = list(lines)
    #for i in range(len(dataset)):
    #	dataset[i] = [float(x) for x in dataset[i]]
    return dataset

def writeToCSV(csvColumns, datas):
    try:
        with open('resources\predictors.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = csvColumns, lineterminator='\n')
            #writer.writeheader()
            for data in datas:
                writer.writerow(data)
    except IOError as xxx_todo_changeme:
        (errno, strerror) = xxx_todo_changeme.args
        print(("I/O error({0}):{1}".format(errno, strerror)))
    return

#SplitDataset with pre defined ratio into training set & testing set.
def splitDataset(dataset,splitRatio):
    
    trainSize = int(len(dataset)*splitRatio)
    trainSet = []
    c = copy.deepcopy(dataset)
    i = len(c)-1
    while len(trainSet) < trainSize:
        #print (c[i])
        trainSet.append(c.pop(i))
        
        i -= 1
    return trainSet,c

def separateByClass(dataset):
    separated = {}
    for i in range(len(dataset)-1):
        vector = dataset[i]
        if (vector[-1] not in separated):
            separated[vector[-1]] = []
        separated[vector[-1]].append(vector)
    return separated

def mean(numbers):
    sumOfNum = 0
    for number in numbers:
        sumOfNum += float(number)
    return sumOfNum/float(len(numbers))

#Standard Deviation function
def stdev(numbers):
    avg = mean(numbers)   
    variance = sum([pow(float(x)-avg,2) for x in numbers])/float(len(numbers)-1)
    return math.sqrt(variance)

def summarize(dataset):
    set2 = copy.deepcopy(dataset)
    set2 = [i[1:-1] for i in set2]
    summaries = [(mean(attribute),stdev(attribute)) for attribute in zip(*set2)]
   # del summaries[-1]
    return summaries

#Summarize the whole dataset according to their respective classes, i.e. Error or No error
def summarizeByClass(dataset):
    separated = separateByClass(dataset)
    summaries = {}
    for classValue, instances in list(separated.items()):
        summaries[classValue] = summarize(instances[1:])
    return summaries

#Gaussian Probability function
def calculateProbability(x,mean,stdev):
    numerator = pow(int(x)-mean,2)
    denominator= int((2*math.pow(stdev,2)))                     
    exponent = math.exp(-int(numerator/denominator))
    return (1/(math.sqrt(2*math.pi)*stdev))*exponent

#For specific input vector(particular set/row of metrics) find the probability of it belonging to all Classes specified
def calculateClassProbabilities(summaries, inputMatrix):
    probabilities = {}
    for classValue, classSummaries in list(summaries.items()):
        probabilities[classValue] = 1
        for j in range(0, len(classSummaries)):
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
                x = inputMatrix[i][j+1]
                probabilities[i][classValue] *= calculateProbability(x,mean,stdev)
    return probabilities

#Predict a particulat testSet row to belong to which class
def predict(summaries, testVector, typeOfDay):
    probabilities = calculateClassProbabilities(summaries, testVector)
    #bestLabel, bestProb = None, -1
    prediction, mathlog, prob = -1, 10, 0
    for classValue, probability in list(probabilities.items()):
        #if bestLabel is None or probability > bestProb:
        if classValue == typeOfDay:
            mathlog = math.log(probability)
            prob = probability
            if mathlog < -100:
                prediction = 1
            else:
                prediction = 0
    #return bestLabel
    return prediction, mathlog, prob



def getPredictions(summaries, testSet):
    predictions = []
    logLikelihood = []
    predictionSet = []
    probability = []
    for i in range(len(testSet)):
        typeOfDay = testSet[i][-2]
        result, likelihood, prob = predict(summaries, testSet[i][1:-2], typeOfDay)
        predictions.append(result)
        logLikelihood.append(likelihood)
        predictionSet.append(testSet[i])
        probability.append(prob)
    return predictions, predictionSet, logLikelihood, probability

#Get accuraccy of Predictions
def getAccuracy(testSet, predictions):
    correct = 0
    for x in range(len(testSet)):
        if testSet[x][-1] == predictions[x]:
            correct +=1
    return (correct/float(len(testSet)))*100.0

def testForecast(forecastedSet, summary):
    inputMatrix = forecastedSet
    for i in inputMatrix:
        i += ['?']
    probabilities = calculateClassProb(summary, inputMatrix)
    predictions, predictionSet, likelihood, probability = getPredictions(summary,inputMatrix)
    for i in range(len(predictions)):
        predictionSet[i].append(predictions[i])
        predictionSet[i].append(likelihood[i])
        predictionSet[i].append(probability[i])
    print(predictionSet)

    
def Bayes_main(forecastedSet):
    #predictors, csvColumn = dbReturnPredictors()
    #print(csvColumn)
    filename = 'resources\predictors.csv'
    #writeToCSV(csvColumn, predictors)
    dataset = loadCsv(filename)
<<<<<<< .merge_file_a16188
    #print(dataset[1][0])
    print "Loading datasets"
    typeOfDays = loadCsv('resources\orders_summary.csv')
    print("Loading oders summary")
    #dataset.append([])
    dIni = datetime.datetime.now()
=======
    print(dataset[1][0])
    typeOfDays = loadCsv('resources\orders_summary.csv')
    #dataset.append([])
>>>>>>> .merge_file_a08344
    for i in range(len(dataset)):
        flag = False
        for j in range(len(typeOfDays)):
            date = dataset[i][0].split()
            date[0] = datetime.datetime.strptime(date[0],'%d-%m-%y').strftime('%d/%m/%Y')
            #print(typeOfDays[j][0])
            typeOfDays[j][0] = parse(typeOfDays[j][0])
            #print(type(typeOfDays[j][0]),typeOfDays[j][0])
            typeOfDays[j][0] = typeOfDays[j][0].strftime('%d/%m/%Y')
            if date[0] == typeOfDays[j][0]:
                dataset[i].append(typeOfDays[j][1])
                flag = True
                break
        if flag != True:
            dataset[i].append('NULL')
<<<<<<< .merge_file_a16188
            #print "abc"
    print "Time to format dates properly", datetime.datetime.now()-dIni           
=======
                
>>>>>>> .merge_file_a08344
    #for i in dataset:
     #   print i
    #f = open("typeOfDays.csv",'w')
    #writer = csv.writer(f,lineterminator = "\n")
    #writer.writerows(dataset)

    #f.close()

    print(('Loaded data file {0} with {1} rows'.format(filename, len(dataset))))
    splitRatio = 0.8
    train, test = splitDataset(dataset,splitRatio)
##    test[1][0]
    print(('Split {0} rows into train with {1} and test with {2}'.format(len(dataset),len(train),len(test))))
    inputMatrix = test
    #inputMatrix.append(['?'])
##    print(inputMatrix[10], inputMatrix[20])
    for i in inputMatrix:
        i += ['?']    
    
    separated = separateByClass(train)
    #attrSummary = summarize(dataset)
    #print(('Attribute summaries: {0}'.format(attrSummary)))
    summary = summarizeByClass(train)
    print(('Summary by class value: {0}'.format(summary)))
    probabilities = calculateClassProb(summary, inputMatrix)
    #print('Probabilities for each class: {0}'.format(len(probabilities)))
    predictions, predictionSet, likelihood, probability = getPredictions(summary,inputMatrix)
    
    for i in range(len(predictions)):
        predictionSet[i].append(predictions[i])
        predictionSet[i].append(likelihood[i])
        predictionSet[i].append(probability[i])
    #print("123")
    f = open("resources\init_dataset3.csv",'w')
    writer = csv.writer(f,lineterminator = "\n")
    writer.writerows(predictionSet)
    #print(predictionSet)

    f.close()
    print("---------------")
    testForecast(forecastedSet, summary)
    #savePredictions(predictions, predictionSet)
    #accuracy = getAccuracy(test,predictions)
    #print(('Accuracy: {0}'.format(accuracy)))

#Bayes_main()
