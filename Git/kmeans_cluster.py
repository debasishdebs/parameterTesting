import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D


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

def kmeans_cluster(init_ds,num_cluster = 3,ts_flag=False):
    '''
    Parameters: init_ds (list)- 2D list of metrics
                num_cluster (int)- number of clusters to use in the K-Means clustering algorithm
                ts_flag (bool) - True if init_ds has a timestamp/datetime column as first column

    Returns: 2D list of init_ds data with an additional column denoting the cluster each row is in
    '''
    
    if ts_flag:
        init_ds = [i[1:] for i in init_ds]

    kmeans = KMeans(n_clusters=num_cluster)
    labels = kmeans.fit_predict(init_ds)

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
    

def plot3D(data):
    '''
    Parameters: data - 2D list with 3 columns: val1,val2,cluster
    Returns: none

    '''

    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    x1_vals = [i[0] for i in data]
    x2_vals = [i[1] for i in data]
    y_vals = [i for i in range(len(data))]

    categories = np.array([i[-1] for i in data])

    colormap = np.array(list(set([i[-1] for i in data])))

    ax.scatter(y_vals,x2_vals,x1_vals,s=50,c=colormap[categories])
    ax.set_xlabel("time")
    ax.set_ylabel("Unblocked")
    ax.set_zlabel("RCMPL")

    plt.show()    
    

    

