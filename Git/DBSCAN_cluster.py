from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import numpy as np
import csv
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

        dateInfo = dateInfo.split("-")
        year = int(dateInfo[0])
        month = int(dateInfo[1])
        day = int(dateInfo[2])

        timeInfo = timeInfo.split(":")
        hour = int(timeInfo[0])
        minute = int(timeInfo[1])

        dt = datetime.datetime(year,month,day,hour,minute)
        return dt


def DBSCAN_cluster(init_ds,ts_flag=False):
    '''
    Parameters: init_ds - 2D list of data
                ts_flag - boolean specifying if the first column of init_ds is a datetime object or not
    Returns: 2D list with additional column denoting which cluster said row falls into
    '''

    if ts_flag:
        init_ds = [i[1:] for i in init_ds]

    dbscn = DBSCAN()
    labels = dbscn.fit_predict(init_ds)

    return [init_ds[i]+[labels[i]] for i in range(len(init_ds))]

def plot(data):
    '''
    Paramters: data - 2D list with 2 columns: value,cluster
    Returns: None

    This function just plots the points of the data parameter all different colors based on cluster
    '''

    x_vals = [i for i in range(len(data))]
    y_vals = [i[0] for i in data]

    a = np.array([x_vals,y_vals])

    categories = np.array([i[-1] for i in data])

    colormap = np.array(list(set([i[-1] for i in data])))

    plt.scatter(a[0],a[1],s=50,c=colormap[categories])
    plt.show()


