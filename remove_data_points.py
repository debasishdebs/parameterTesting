__author__ = 'Debasish'
import collections, datetime, sys
from balanceIt import connect_db
from balanceDataset import push_to_db
from randomForest_1 import start

'''
Deletion of data points will be done using 2 separate process.
    1) Between any 2 consecutive errors, if hour diff == x+6 (x any), then delete x/2 number of points n x points but
       leave 6hr of data before error occurs.
    2) Between any 2 consecutive errors, if hour diff > 6, lets say tomorrow's error occurs after 0600 hrs, then delete
       all data points for that day except 6hrs of data just succeeding that.

Results : Method 1 : 24k rows final.
Method 2: 48k rows final.
Method 1 : Settings of 6hr, 9hr, 12hr. Find best model of 4 models.
'''

def get_data(db, table):
    sql = "SELECT * FROM {}".format(table)
    c = db.cursor()
    c.execute(sql)
    rows = [list(i) for i in list(c.fetchall())]
    dataset = {}
    for i in range(len(rows)):
        dataset[rows[i][0]] = rows[i][1:]
    return dataset

def method1(start_time, end_time, dataset):
    print("Total data worth {} hours will be removed".format(end_time-start_time - datetime.timedelta(hours=6)))
    data_removal_start = start_time + datetime.timedelta(hours=1)
    data_removal_end = end_time - datetime.timedelta(hours=6)
    print(len(dataset))
    b_dataset = dataset
    for key in dataset.keys():
        if data_removal_start <= key <= data_removal_end and key.date() < datetime.datetime.strptime('29-04-2015',
                                                                                                   '%d-%m-%Y').date() :
            del b_dataset[key]
    print(len(b_dataset))
    return b_dataset

def method2(ts, dataset):
    print "Today is {} and type : {}".format(ts.date(), type(ts.date()))
    midnight = datetime.datetime.combine(ts.date(), datetime.datetime.min.time())
    # print(type(midnight))
    print "Total {} hours after midnight, error occurs".format(ts - midnight)
    timeDiff = ts - midnight
    print "Total hours of data which can be removed : {}".format(timeDiff - datetime.timedelta(hours=6))
    print(len(dataset))
    b_dataset = dataset
    if (timeDiff - datetime.timedelta(hours=6)).seconds/3600 >= 1:
        data_removal_start = midnight
        data_removal_end = ts - datetime.timedelta(hours=6)
        for key in dataset.keys():
            if data_removal_start <= key <= data_removal_end and key.date() <= datetime.datetime.strptime('29-04-2015',
                                                                                                   '%d-%m-%Y').date():
                del b_dataset[key]
    print(len(b_dataset))
    return b_dataset

def dict_to_list(dd={}, index=0):
    print type(dd.keys())
    keys = dd.keys()
    values = dd.values()
    print(type(dd.values()))
    print(len(dd.values()))
    print(len(dd.values()[0]))
    print(len(keys))
    ll = [[None] for k in range(len(keys))]
    for i in range(len(keys)):
        ll[i] = [[None] for k in range(len(values[i])+1)]
        for j in range(len(values[i])+1):
            if j == index:
                ll[i][j] = keys[i]
            else:
                ll[i][j] = values[i][j-1]
    print "Length of list :",len(ll)
    print "Number of columns :", len(ll[0])
    return ll


def remove_points(table):
    f = open('output.txt', 'a')
    #sys.stdout = f    
    error = {}
    start_time = ''
    end_time = ''
    ts_list = []
    sql = "SELECT timestamp, error from {}".format(table)
    print(sql)
    db = connect_db()
    c = db.cursor()
    c.execute(sql)
    rows = [list(i) for i in list(c.fetchall())]
    # print(type(rows[0][0]))
    indeces = []
    for i in range(len(rows)):
        if rows[i][1] == 1:
            indeces.append(i)
            error[rows[i][0]] = rows[i][1]
    #print(sorted(error.items()))

    error_sorted = collections.OrderedDict(sorted(error.items()))
    for key, value in error_sorted.iteritems():
        ts_list.append(key)
    print(ts_list)
    dataset = get_data(db, table)
    for i in range(len(ts_list)-1):
        j = i+1
        timeDiff = ts_list[j] - ts_list[i]
        # print("Time before next error occurs : {} days : {} hours : {} minutes".format(timeDiff.days,
        # timeDiff.seconds/3600, (timeDiff.seconds/60)%60))
        hours = timeDiff.seconds/3600
        if hours >= 7:
            print("Time before next error occurs : {} days : {} hours : {} minutes".format(timeDiff.days,
                                                                                           timeDiff.seconds/3600,
                                                                                           (timeDiff.seconds/60)%60))
            print("Next error occurs at : {} and today's date : {}".format(ts_list[j], ts_list[i].date()))
            print("Conserving 6hr of data before an error occurs, we can remove {} hours of data points".format(timeDiff
                                                                                        - datetime.timedelta(hours=6)))
            print("\n")
            # choice = raw_input("Enter choice of method (1/2)")
            choice = '1'
            if choice == '1':
                dataset = method1(ts_list[i], ts_list[j], dataset)
                print("Final length of dataset is : ",len(dataset))
                table = 'balanced_manual_new_small_ds1_tse_temporal_lookback4_m1_29_04'
            elif choice == '2':
                dataset = method2(ts_list[i], dataset)
                print("Final length of dataset is : ",len(dataset))
                table = 'balanced_manual_new_small_ds1_tse_temporal_lookback4_method2'
    print type(dataset)
    ll_dataset = dict_to_list(dataset)
    ts = []
    for i in range(len(ll_dataset)):
        ts.append(ll_dataset[i][0].date())
    print "Length of ts list :",len(set(ts))
    push_to_db(ll_dataset, table)
    ds = list(set(ts))
    start(table, ds)
    #f.close()


if __name__ == '__main__':
    remove_points('new_small_ds1_tse_temporal_lookback4')
