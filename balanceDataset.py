__author__ = 'Debasish'

from balanceIt import balanceIt, connect_db
import csv, os
from randomForest_1 import start
import sys
from random import randint

# f = open('output.txt', 'w')
# sys.stdout = f

def write_temp_file(data):
    fileName = 'temp_data_1.csv'
    f = open(fileName,'w')
    writer = csv.writer(f,lineterminator="\n")
    writer.writerows(data)
    f.close()
    return fileName

def push_to_db(dataset, table):
    db = connect_db('MySQLdb')
    c = db.cursor()

    sql = "DROP TABLE IF EXISTS '{}'".format(table)
    print sql
    print "Table name", table
    c.execute("DROP TABLE IF EXISTS `{}`".format(table))
    

    print "Table doesn't exost. Creating new table"

    sql = "CREATE TABLE IF NOT EXISTS `{}` (`timestamp` datetime DEFAULT NULL,\
          `epoch` bigint(20) DEFAULT NULL, `RCMPL_0` float DEFAULT NULL, `dt_RCMPL_0` float DEFAULT NULL,\
          `n_stdev_0` float DEFAULT NULL, `msp_order_a_0` float DEFAULT NULL, `msp_order_b_0` float DEFAULT NULL,\
          `sdp_client_cpu_0` float DEFAULT NULL, `sdp_client_mem_0` float DEFAULT NULL, `navapp_cpu_0` float DEFAULT NULL,\
          `navapp_mem_0` float DEFAULT NULL, `RCMPL_1` float DEFAULT NULL, `dt_RCMPL_1` float DEFAULT NULL, `n_stdev_1` float DEFAULT NULL,\
          `msp_order_a_1` float DEFAULT NULL,  `msp_order_b_1` float DEFAULT NULL,  `sdp_client_cpu_1` float DEFAULT NULL,\
          `sdp_client_mem_1` float DEFAULT NULL, `navapp_cpu_1` float DEFAULT NULL, `navapp_mem_1` float DEFAULT NULL,\
          `RCMPL_2` float DEFAULT NULL, `dt_RCMPL_2` float DEFAULT NULL, `n_stdev_2` float DEFAULT NULL,\
          `msp_order_a_2` float DEFAULT NULL, `msp_order_b_2` float DEFAULT NULL, `sdp_client_cpu_2` float DEFAULT NULL,\
          `sdp_client_mem_2` float DEFAULT NULL, `navapp_cpu_2` float DEFAULT NULL, `navapp_mem_2` float DEFAULT NULL,\
          `RCMPL_3` float DEFAULT NULL, `dt_RCMPL_3` float DEFAULT NULL, `n_stdev_3` float DEFAULT NULL,\
          `msp_order_a_3` float DEFAULT NULL, `msp_order_b_3` float DEFAULT NULL, `sdp_client_cpu_3` float DEFAULT NULL,\
          `sdp_client_mem_3` float DEFAULT NULL, `navapp_cpu_3` float DEFAULT NULL, `navapp_mem_3` float DEFAULT NULL,\
          `RCMPL_4` float DEFAULT NULL, `dt_RCMPL_4` float DEFAULT NULL, `n_stdev_4` float DEFAULT NULL,\
          `msp_order_a_4` float DEFAULT NULL, `msp_order_b_4` float DEFAULT NULL, `sdp_client_cpu_4` float DEFAULT NULL,\
          `sdp_client_mem_4` float DEFAULT NULL, `navapp_cpu_4` float DEFAULT NULL, `navapp_mem_4` float DEFAULT NULL,\
          `tse` int(11) DEFAULT NULL, `error` int(11) DEFAULT NULL, `e_5` int(11) DEFAULT NULL, `e_10` int(11) DEFAULT NULL,\
          `e_15` int(11) DEFAULT NULL, `e_20` int(11) DEFAULT NULL, `e_25` int(11) DEFAULT NULL, `e_30` int(11) DEFAULT NULL\
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;".format(table)
    print sql
        
    c.execute(sql)

    fname = write_temp_file(dataset)
    print "File name",fname
    print "Table name", table
    sql = "LOAD DATA LOCAL INFILE '{0}' INTO TABLE {1} FIELDS TERMINATED BY ',';".format(fname, table)
    print sql
    c.execute(sql)
    db.commit()
    if table == 'new_small_ds1_tse_temporal_lookback4_balanced':
        os.remove(file)


def main():
    # option1 = raw_input("Enter your choice on how to balance dataset.:\nEnter 1 for Over-Sampling\nEnter 2 for Under-Sampling\n")
    option1 = 1
    option1 = int(option1)
    if option1 == 1:
        category = 'over_sampling'
        print "The following Algorighm will be used for over-sampling :"
        print "1 : Random Over Sampler"
        print "2 : SMOTE"
        print "3 : SMOTE-Boderline 1"
        print "4 : SMOTE-Boderline 2"
        print "5 : SMOTE-SVM"
        print "6 : SMOTE-Tomek Links"
        print "7 - SMOTE-ENN"
        print "8 : EasyEnsemble"
        print "9 : BalanceCascade"
        choice = raw_input("Enter your choice : ")
        #choice = randint(1,4)
        choice = int(choice)
        if choice == 1:
            algorithm = 'random_over_sampling'
        elif choice == 2:
            algorithm = 'smote'
        elif choice == 3:
            algorithm = 'smote_boderline1'
        elif choice == 4:
            algorithm = 'smote_boderline2'
        elif choice == 5:
            algorithm = 'smote_svm'
        elif choice == 6:
            algorithm = 'smote_tomek_links'
        elif choice == 7:
            algorithm = 'smote_enn'
        elif choice == 8:
            algorithm = 'easy_ensemble'
        elif choice == 9:
            algorithm = 'balance_cascade'

    elif option1 == 2:
        category = 'under_sampling'
        print "The following Algorighm will be used for under-sampling :"
        print "1 : Random Under Sampler"
        print "2 : Tomek links"
        print "3 : Clustering centroids"
        print "4 : NearMiss-1"
        print "5 : NearMiss-2"
        print "6 : NearMiss-3"
        print "7 : Condensed Nearest Neighbour"
        print "8 : One-Sided Selection"
        print "9 : Neighboorhood Cleaning Rule"
        # choice = raw_input("Enter your choice : ")
        choice = randint(1,9)
        choice = int(choice)
        if choice == 1:
            algorithm = 'under_sampling'
        elif choice == 2:
            algorithm = 'tomek_links'
        elif choice == 3:
            algorithm = 'clustering_centroids'
        elif choice == 4:
            algorithm = 'near_miss1'
        elif choice == 5:
            algorithm = 'near_miss2'
        elif choice == 6:
            algorithm = 'near_miss3'
        elif choice == 7:
            algorithm = 'condensed_nn'
        elif choice == 8:
            algorithm = 'one_sided_selection'
        elif choice == 9:
            algorithm = 'neighbourhood_cleaning_rule'

    tx, ty, ts_epoch, response = balanceIt(category, algorithm)
    new_ds = [None] * len(tx)
    print "Length of transformed Predictor set : {} and that of response set : {}".format(len(tx), len(ty))

    for i in xrange(len(tx)):
        new_ds[i] = [ts_epoch[int(tx[i][-1])][0]] + list(tx[i][0:-1]) + [int(ty[i])] + response[int(tx[i][-1])]

    push_to_db(new_ds, table = 'new_small_ds1_tse_temporal_lookback4_balanced')

    start()
    # f.close()

    '''Todo : Append tx & ty side by side thus forming new dataset. This new 2d list (Dataset) is passed to RF and replaced this line\
    data = [list(i) for i in list(c.fetchall())]. But before replacement is done, timestamp, ropchid, and error columns(e_5, e_10.. ) are appended also.
    The final appended data is same as data and would replace data for further runs.
    Module starts by running this script. It calls balanceIt to balance dataset. The balanced dataset is then appended with respective timestamps
    (by comparing their respective metrics) and also future errors. This dataset is passed on to RF script which then performs its implementation on this new dataset.'''

if __name__ == '__main__':
    print("Execution starts here")
    main()
