<<<<<<< .merge_file_a12632
import smootheningUnblocked
import smootheningRCMPL
import HoltWinters
import BayesianClassifier_1
from datetime import datetime
from openpyxl import *

def main():
    print "Start Time : ", datetime.now()
    d1 = datetime.now()
    print("Running Holt Winters smoothening for forecasting")
    HoltWinters.HWmain()
    print "Time after HW() run : ", datetime.now() , " and total time taken = :" ,d1-datetime.now()
    d2 = datetime.now()
##    wb = load_workbook("resources/AvgSort.xlsx", data_only = True)
##    print "Load = True"
##    wb.save("resources/copyAvgSort.xlsx")
##    print "Save = true"
    forecastRCMPL, forecastDate, forecastTime = smootheningRCMPL.RCMPLmain()
    print(forecastDate.strftime('%d/%m/%Y'))
    print("Forecast for RCMPL \n",forecastRCMPL)
    print("\n")
    forecastUnblocked = smootheningUnblocked.unblockedMain()
=======
from smootheningUnblocked import unblockedMain
from smootheningRCMPL import RCMPLmain
#from HoltWinters import HWmain
from BayesianClassifier_1 import Bayes_main
from datetime import datetime

def main():
    #print("Running Holt Winters smoothening for forecasting")
    #HWmain()
    forecastRCMPL, forecastDate, forecastTime = RCMPLmain()
    print(forecastDate.strftime('%d/%m/%Y'))
    print("Forecast for RCMPL \n",forecastRCMPL)
    print("\n")
    forecastUnblocked = unblockedMain()
>>>>>>> .merge_file_a17084
    print("Forecast for Unblocked connections \n",forecastUnblocked)
    testMatrix = [[0 for x in range(5)] for x in range(len(forecastRCMPL))]
    #rint(len(testMatrix))
    for x in range(len(testMatrix)):
        d = datetime.strptime(forecastDate.strftime('%d/%m/%Y')+ " "+str(forecastTime[x]),'%d/%m/%Y %H:%M')
        #print(d.strftime('%d/%m/%Y %H:%M'))
        testMatrix[x][0] = d.strftime('%d/%m/%Y %H:%M')
        testMatrix[x][1] = forecastRCMPL[x]
        testMatrix[x][2] = forecastUnblocked[x]
        testMatrix[x][3] = 0
        testMatrix[x][4] = '?'
<<<<<<< .merge_file_a12632
    print "\n",testMatrix
    print "Time after forecasting metrices : ", datetime.now(), "Total time taken : ", d2-datetime.now()
    d3 = datetime.now()
    BayesianClassifier_1.Bayes_main(testMatrix)
    print "Time taken for Bayesian model to run :", datetime.now()-d3, " and present time is ", datetime.now()
    
=======
    print("\n",testMatrix)
    Bayes_main(testMatrix)
>>>>>>> .merge_file_a17084
main()


'''Comments :
Right now, Holt Winters trains using 4 days of data (15th-12th) and forecasts for 11th. Those forecasted matrices are then passed to Bayesian model where they are predicted weather
those metrics (Combination of RCMPL & Unblocked) will lead to error or not.
Accuraccy of those predictions if to be checked and the accuraccy which it displays is accuraccy of model in training.
Minimization function to be added to improve accuraccy of forecasts.'''
