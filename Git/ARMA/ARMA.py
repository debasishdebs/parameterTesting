import numpy as np
import statsmodels.api as sm
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import pylab, time, datetime, warnings
from dateutil.parser import parse
from sympy import *

warnings.filterwarnings('ignore')

def readFile(file, head, sheet):
    df = pd.read_excel(file, headers=head, sheetname=sheet)
    df.index = df.timestamp
    del df['timestamp']
    return df


def plot(data):
    choice = raw_input("Enter your choice. y/Y/yes/Yes to see plot, else no : ")
    confirmed = ['y', 'Y', 'yes', 'Yes', 'YES', 'YeS', 'yEs']
    if choice in confirmed:
        data.plot(figsize=(12,8))
        pylab.show()
    else:
        return

    
def acf_pacf(data, choice = 1):
    fig = plt.figure(figsize=(12,8))
    ax1 = fig.add_subplot(211)
    fig = sm.graphics.tsa.plot_acf(data.values.squeeze(), lags=40, ax=ax1)
    ax2 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_pacf(data, lags = 40, ax=ax2)
    if choice == 1:
        print "Displaying plots for Autocorelaion & Partial AutoCorrelation. Estimate orders from plot."
        time.sleep(1)
        pylab.show()
        choice = raw_input("Is time series stationary? (y/n) : ")
        if choice == 'y' or choice == 'Y':
            #print data
            return data
        else:
            blockedDiff = np.ediff1d(data.blocked)
            df = data.ix[:-1]
            #print(type(data), df, len(data.ix[:-1]))
            df.blocked = blockedDiff
            acf_pacf(df)
            return df
    elif choice == 2:
        pylab.show()

def durbin_watson(results):
    dw = sm.stats.durbin_watson(results.resid.values)
    return dw

def normaltest(resid):
    return stats.normaltest(resid)

def qqplot(resid):
    from statsmodels.graphics.api import qqplot
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(111)
    fig = qqplot(resid, line='q', ax = ax, fit = True)
    pylab.show()

def get_acf(resid):
    r, q, p = sm.tsa.acf(resid.values.squeeze(), qstat=True)
    data = np.c_[range(1,41), r[1:], q, p]
    table = pd.DataFrame(data, columns=['lag', 'AC', 'Q', 'Prob(>Q)'])
    table.set_index('lag')
    return r,q, p

def predict(results, start, end):
    predict_metric = results.predict(start, end, dynamic = True)
    return predict_metric

def getStartEnd(data):
    print "Start date of Dataset : {0} , and End date is : {1}". format(data.index[0], data.index[-1])
    start = raw_input("Enter start date from when you want to start forecasting : ")
    end = raw_input("Enter end date till when you want the forecasting : ")
    start = parse(start)
    end = parse(end)
    start = datetime.datetime.strftime(start, '%m-%d-%Y')
    end = datetime.datetime.strftime(end, '%m-%d-%Y')
    return start, end

def meanForecastErr(subArr, forecast):
    return subArr.sub(forecast).mean()

def getEqn(A, B):
    for i in range(len(A)):
        A[i] = Symbol('A['+str(i)+']')

    equations = [None]*(len(B)-1)
    for i in range(len(equations)):
        equations[i] = Eq(A[i]-A[i+1], B[i])
    return equations, A

def solver(predictions):
    lenPredictions = len(predictions)
    A = [None]*lenPredictions
    for i in range(lenPredictions):
        A[i] = Symbol('A['+str(i)+']')
    equations, variables = getEqn(A, predictions)
    for i in range(lenPredictions-1):
        res = solve(equations, variables)
    return res

def main():
    file = 'E:\\IntegrationTesting\\Predictive-Analytics\\ARMA\datasets\\dataset3.xlsx'
    head = 0
    sheet = 1
    df = readFile(file, head, sheet)
    print "Want to plot for blocked connections? : "
    plot(df)
    df = acf_pacf(df)
    #print df
    p = raw_input("Enter order of AR model : ")
    q = raw_input("Enter order of MA model : ")
    #print df, len(df)
    arma_pq = sm.tsa.ARMA(df, (int(p),int(q))).fit()
    print arma_pq.params, " :Parameters"
    print "AIC : {0}, BIC : {1}, HQIC : {2} ".format(arma_pq.aic, arma_pq.bic, arma_pq.hqic)
    dw = durbin_watson(arma_pq)
    resid = arma_pq.resid
    normalTest = normaltest(resid)
    print "Printing Q-Q plot"
    qqplot(resid)
    print "Plotting acf & pacf for residual values"
    acf_pacf(resid, 2)
    r, q, p = get_acf(resid)
    start, end = getStartEnd(df)
    predictions = predict(arma_pq, start, end)
    mean = meanForecastErr(df.blocked, predictions)
    print "Mean error in forecasting : {0}. \nNote that this error is on 1st difference and not actual blocked connections".format(mean)
    res = solver(predictions)
    print res

main()
