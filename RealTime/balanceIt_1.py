__author__ = 'Debasish'

import seaborn as sns
import pymysql
import MySQLdb

sns.set()

import numpy as np
from underSampling import underSampling
from overSampling import  overSampling

# f = open('output.txt', 'w')
# sys.stdout = f

# Save a nice dark grey as a variable
almost_black = '#262626'

########################################################################################################################

def split_dataset(dataset):
    x = []
    y = []
    ts_epoch = []
    response = []
    #print (dataset[0][48])
    for i in range(len(dataset)):
        x.append(dataset[i][1:48] + [int(i)])
        y.append(dataset[i][48])
        ts_epoch.append(dataset[i][0:2])
        response.append(dataset[i][49:55])

    return x,y, ts_epoch, response

########################################################################################################################

def connect_db(type = 'pymysql'):
    if type == 'pymysql':
        db = pymysql.connect(host = "127.0.0.1", db = "predictiveanalytics", user = "root", passwd = "")
        return db
    elif type == 'MySQLdb':
        db = MySQLdb.Connect(host="127.0.0.1", user = "root", passwd = "", db = "predictiveanalytics")
        return db

########################################################################################################################

def get_dataset():
    db = connect_db()
    c = db.cursor()

    sql = "SELECT * FROM `small_ds1_tse_temporal_lookback4` ORDER BY timestamp"

    c.execute(sql)
    data = [list(i) for i in list(c.fetchall())]

    return data

########################################################################################################################

def balanceIt(category, algorithm):

    dataset = get_dataset()

    x, y, ts_epoch, response = split_dataset(dataset)
    for i in range(len(x)):
        for j in range(len(x[i])):
            #print x[i][j]
            x[i][j] = np.float64(x[i][j])
        x[i] = np.array(x[i])

    for i in range(len(y)):
        y[i] = np.float64(y[i])

    x = np.array(x)
    y = np.array(y)

    under_balance = underSampling('False', x, y)
    over_balance = overSampling('False', x, y)

    # # Instanciate a PCA object for the sake of easy visualisation
    # pca = PCA(n_components = 2)
    #
    # # Fit and transform x to visualise inside a 2D feature space
    # x_vis = pca.fit_transform(x)
    #
    # print len(x_vis[y==0,0]), len(y)
    # #print x_vis
    #
    # # Plot the original data
    # # Plot the two classes
    # palette = sns.color_palette()
    # plt.scatter(x_vis[y==0, 0], x_vis[y==0, 1], label="Class #0", alpha=0.5,
    #             edgecolor=almost_black, facecolor=palette[0], linewidth=0.15)
    # plt.scatter(x_vis[y==1, 0], x_vis[y==1, 1], label="Class #1", alpha=0.5,
    #             edgecolor=almost_black, facecolor=palette[2], linewidth=0.15)
    #
    # plt.legend()
    # #plt.show()

    if category == 'over_sampling':
        #print hasattr(over_balance, algorithm)
        method = getattr(over_balance, algorithm)
        print "{} algorighm is followed to do {}".format(algorithm, category)
        ost_x, ost_y = method()
        return ost_x, ost_y, ts_epoch, response
    elif category == 'under_sampling':
        #print hasattr(under_balance, algorithm)
        method = getattr(under_balance, algorithm)
        print "{} algorighm is followed to do {}".format(algorithm, category)
        ust_x, ust_y = method()
        return ust_x, ust_y, ts_epoch, response

    # f.close()
