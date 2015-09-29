import MySQLdb, csv

def dbReturnDataSet(dbCred):
    #Saves the whole Dataset into csv file and returns name of csv file.
    db = MySQLdb.connect(dbCred['ip'],dbCred['user'],dbCred['pass'],dbCred['db'])
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM test7")
    rows = cursor.fetchone()
    numOfRows = rows[0]

    trainRow = cursor.execute("SELECT COUNT(*) FROM test7 WHERE DATE(timestamp) BETWEEN '2014-02-19' AND '2015-02-18'")
    trainNumOfRows = cursor.fetchone()
    #print(trainNumOfRows[0])

    testRow = cursor.execute("SELECT COUNT(*) FROM test7 WHERE DATE(timestamp) >= '2015-02-18'")
    testNumOfRows = cursor.fetchone()
    #print(testNumOfRows)
    
    trainSet = [[0 for x in range(4)] for x in range(trainNumOfRows[0])]
    testSet = [[0 for x in range(3)] for x in range(testNumOfRows[0])]
    
    trainSQL = "SELECT RCMPL, unblocked, blocked, error FROM test7 WHERE timestamp BETWEEN '2014-02-19 00:00:00' AND '2015-02-18 00:00:00'"
    testSQL = "SELECT RCMPL, unblocked, blocked FROM test7 WHERE timestamp >= '2015-02-18 00:00:00'"

    cursor.execute(trainSQL)
    trainData = cursor.fetchall()
    
    i = 0
    for trainRow in trainData:
        trainSet[i][0] = list(trainRow)[0]
        trainSet[i][1] = list(trainRow)[1]
        trainSet[i][2] = list(trainRow)[2]
        trainSet[i][3] = list(trainRow)[3]
        if i%10000 == 0:
            print(trainSet[i])
        i = i+1

    cursor.execute(testSQL)
    testData = cursor.fetchall()
    
    i = 0
    for testRow in testData:
        testSet[i][0] = list(testRow)[0]
        testSet[i][1] = list(testRow)[1]
        testSet[i][2] = list(testRow)[2]
        if i%5000 == 0:
            print(testSet[i])
        i = i+1
        
    return [trainSet, testSet]

def dbReturnError():
    db = MySQLdb.connect("11.120.36.241","internship","Pr3dict!v@","predictiveAnalytics")

    cursor = db.cursor()
    try:
        cursor.execute("SELECT VERSION()")
        result = cursor.fetchone()
    except:
        print("Error in Conn")

    cursor.execute("SELECT COUNT(*) from `test7`")
    count = cursor.fetchone()
    numOfRows = count[0]

    sql = """SELECT error FROM `test7`"""
    cursor.execute(sql)
    errorsList = [dict() for x in range(numOfRows)]
    i=0

    try:
        results = cursor.fetchall()
    
        for row in results:
            errorsList[i]['error'] = row[0]
            i = i+1
    except:
        print("Unable to fetch data")            

    db.close()
    return errorsList

def csvToDB(file):
    print("Step 2:Saving to DB")
    db = MySQLdb.connect("11.120.36.241","internship","Pr3dict!v@","predictiveAnalytics")
    cursor = db.cursor()
    try:
        cursor.execute("SELECT VERSION()")
        result = cursor.fetchone()
    except:
        print("Error in Conn")
    #cursor.execute("DROP TABLE IF EXISTS `temp_table`")
    try:
        sql = "CREATE TEMPORARY TABLE IF NOT EXISTS `temp_table` (`RCMPL` int(11) DEFAULT NULL,`unblocked` int(11) DEFAULT NULL,`blocked` int(11) DEFAULT NULL,`e_b` int(11) NOT NULL,KEY `param_index`(`RCMPL`,`unblocked`,`blocked`))"
        cursor.execute(sql)
    except:
        print("Error is creating temporary table")
        
    sql = "LOAD DATA LOCAL INFILE '{0}' INTO TABLE temp_table FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n' (RCMPL, unblocked, blocked, e_b) ".format(file)
    
    try:
        cursor.execute(sql)
        print("CSV File Loaded to DB successfully")
        flag = 0
    except:
        print("Error in loading csv file into DB")
        return
    if flag == 0:
        flag = 1
        sql = "UPDATE test7 INNER JOIN temp_table ON temp_table.RCMPL = test7.RCMPL AND temp_table.unblocked = test7.unblocked AND temp_table.blocked = test7.blocked SET test7.e_b = temp_table.e_b"
        try:
            #print("11111")
            cursor.execute(sql)
            print("Inner Join of Tables Success")
        except:
            print("Error in Joining tables")
            return
        print("Success")
    db.commit()
    db.close()
    return
        
def dbReturnPredictors():
    db = MySQLdb.connect("11.120.36.241","internship","Pr3dict!v@","predictiveAnalytics")

    cursor = db.cursor()
    try:
        cursor.execute("SELECT VERSION()")
        result = cursor.fetchone()
    except:
        print("Error in Conn")
    
    cursor.execute("SELECT COUNT(*) from `test7`")
    count = cursor.fetchone()
    numOfRows = count[0]
    
    sql = """SELECT * FROM `learning_set2`"""
    cursor.execute(sql)
    print(cursor.rowcount)
    #print(numOfRows)
    predictorsList = [dict() for x in range(cursor.rowcount)]
    i=0
    results = cursor.fetchall()
    #print(len(results))
    #print(numOfRows)
    for row in results:
        #print("123")
        predictorsList[i]['time'] = row[0]
        predictorsList[i]['RCMPL'] = row[1]
        predictorsList[i]['unblocked'] = row[2]
        predictorsList[i]['blocked'] = row[3]
        i = i+1            
    #print(predictorsList[len(results)-1]," 15")
    db.close()
    return predictorsList, ['time','RCMPL','unblocked','blocked']

def savePredictions(predictions,predictionSet,csvColumn):
    print("Saving Predictions")
    predictionList = [dict() for x in range(len(predictions))]
    for i in range(len(predictions)):
        #if i%1000 == 0:
            #print(predictions[i],type(i))
        predictionList[i]['RCMPL'] = predictionSet[i][0]
        predictionList[i]['unblocked'] = predictionSet[i][1]
        predictionList[i]['e_b'] = predictions[i]
    csvColumn[2] = 'e_b'

    '''for i in range(len(predictions)):
        if i%1000 == 0:
            print(predictions[i])'''
    
    file = 'temp_predictions.csv'
    print("Step 1: Saving to CSV")
    try:
        with open(file,'w',newline='') as csvFile:
            writer = csv.DictWriter(csvFile,fieldnames = csvColumn, lineterminator = '\n')
            #writer.writeheader()
            for row in predictionList:
                writer.writerow(row)
    except IOError as xxx_todo_changeme:
        (errno, strerror) = xxx_todo_changeme.args
        print(("I/O error({0}):{1}".format(errno, strerror)))

    '''sql = "UPDATE test7 SET `e_b` = {0} FORCE INDEX(ts_index,param_index) WHERE `RCMPL` = {1} AND `unblocked` = {2} AND `blocked` = {3}".format(predictions[i],predictor[0],predictor[1],predictor[2])
        try:
            cursor.execute(sql)
            if i%1000 == 0:
                print("Successful entry {0}".format(i))
        except:
            print("Error in Insertion")
        i+=1'''
    csvToDB(file)
    return
    

'''def dbJVMsStatus():
    db = MySQLdb.connect("11.120.36.241","internship","Pr3dict!v@","predictiveAnalytics")

    cursor = db.cursor()
    try:
        cursor.execute("SELECT VERSION()")
        result = cursor.fetchone()
    except:
        print("Error in Conn")

    cursor.execute("SELECT ( SELECT COUNT(*) FROM dt_jvm ) AS count1, ( SELECT COUNT(*) FROM dt_jvm_archive ) AS count2, (SELECT COUNT(*) FROM dt_jvm_hist) AS count3 FROM dual")
    count = cursor.fetchone()
    numOfRows = count[0] + count[1] + count[2]
    #print(numOfRows)

    sql = """SELECT * FROM `dt_jvm`,`dt_jvm_archive`,`dt_jvm_hist`"""
    cursor.execute(sql)
    jvmStatsList = [dict() for x in range(numOfRows)]
    i=0

    try:
        results = cursor.fetchall()
    
        for row in results:
            jvmStatsList[i]['id'] = row[0]
            jvmStatsList[i]['timestamp'] = row[1]
            jvmStatsList[i]['server'] = row[2]
            jvmStatsList[i]['jvm'] = row[3]
            jvmStatsList[i]['cpu'] = row[4]
            jvmStatsList[i]['mem'] = row[5]
            jvmStatsList[i]['transCount'] = row[6]
            jvmStatsList[i]['respTime'] = row[7]
            jvmStatsList[i]['GC'] = row[8]
            i = i+1
    except:
        print("Unable to fetch data")            

    db.close()
    return jvmStatsList    

def main():
    errorsList = dbJVMsStatus()
    #print(errorsList)

main()'''

def main():
    predictors, csvColumns = dbReturnPredictors()

main()
#Testify table from Predictiveanalytics results server
#June 3 2014-Apr 3 2015 Training data
#Predictive column from April 1st to June 2015 Testing data
#Populate predictive column with tested data
