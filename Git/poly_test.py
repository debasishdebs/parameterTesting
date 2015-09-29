import csv
import p_poly
import matplotlib.pyplot as plt
import numpy
import datetime


def convert_str_to_dt(aStr):
        '''
        Converts aStr to a datetime object
        Returns: datetime object
        Note: I know a method exists in the datetime module that does this, but I figured that out too late
        '''

        info = aStr.split(" ")
        dateInfo = info[0]
        timeInfo = info[1]

        dateInfo = dateInfo.split("/")
        #print dateInfo
        year = int(dateInfo[2])
        month = int(dateInfo[0])
        day = int(dateInfo[1])

        timeInfo = timeInfo.split(":")
        hour = int(timeInfo[0])
        minute = int(timeInfo[1])

        dt = datetime.datetime(year,month,day,hour,minute)
        return dt


def error_detect(data,mean,lag):
    '''
    Detects errors/anomalies of the inputted datastream
    Parameters: data (list) - 1D list of SEQUENTIAL, DETRENDED data points
                mean (int or float) - mean of inputted data
                lag (int) - number specifying how many data points to use to find initial std dev of data stream 
    Returns: output_list (list) - list of tuples of the form (index,value) containing all indices and corresponding data points of errors found
    '''
    
    output_list = []
    non_errors = []

    i = 0

    #loop over data
    while i < len(data):
        #allow lag number of iterations before attempting to identify anomalies
        if i < lag:
            non_errors.append(data[i])
            i+=1
            continue

        #calculate rolling std dev of all non-error datapoints
        temp_std = numpy.std(non_errors[0:i])
        
        #if data[i] > mean+3*temp_std or data[i] < mean-3*temp_std:

        #Check if datapoint is below 3 std deviations of the mean, if so, label as an error
        if data[i] < mean-3*temp_std:
            output_list.append((i,data[i],abs(float(data[i])/float(temp_std))))
        else:
            non_errors.append(data[i])

        i+= 1

    return output_list


def test(plot=True):
    '''
    Tests validity of error/anomaly identification algorithm
    Parameters: plot (bool) - True if you want to see a plot of the data, the fitted polynomial, the detrended stream, and error datapoints in 2 plots
    Returns: None
    '''

    #open file
    f = open("Error CSV Files/3.12.2015_error.csv")
    reader = csv.reader(f)
    data = []
    for i in reader:
        dt = convert_str_to_dt(i[0])
        for j in range(1,len(i)):
            i[j] = float(i[j])

        data.append([dt]+i[1:])
    f.close()

    #create different datasets
    date_data = [i[0] for i in data]
    rcmpl_data = [i[1] for i in data]
    blocked_data = [i[2] for i in data]
    unblocked_data = [i[3] for i in data]

    x_vals = [i for i in range(len(rcmpl_data))]

    #fit polynomial to RCMPL data
    y_vals,y_poly = p_poly.poly_detrend(x_vals,rcmpl_data,degree=6,d_type = "d")


    #detect "anomalies"
    error_vals = error_detect(y_vals,0,20)
        
    error_x = [i[0] for i in error_vals]
    error_y = [i[1] for i in error_vals]
    init_error_y = [rcmpl_data[i] for i in error_x]
    

    #plot results
    if plot:
        plt.figure(1)
        plt.subplot(211)
        plt.title("{}".format(date_data[0].date()))
        plt.plot(x_vals,rcmpl_data,"bo",x_vals,y_poly,"r-",init_error_y)

        plt.subplot(212)
        plt.plot(x_vals,y_vals,"b",error_x,error_y,"ro")
        
        plt.show()
    
    
