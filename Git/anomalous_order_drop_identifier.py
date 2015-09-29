import csv
import p_poly
import poly_test
import datetime
import MySQLdb


def checkErrors(data):
    #fills in holes of original error detection
        i = 0
        j = 0
        while i < len(data) and j < len(data):
                if data[i] == 0:
                        i += 1
                        j += 1
                elif data[i] == 1 and i < len(data):
                        if i == len(data) - 1:
                                break
                        j += 1
                        if data[j] == 0:
                                if (j - i) > 3:
                                        i = j
                        elif data[j] == 1:
                                while i < j:
                                        data[i] = 1
                                        i += 1                                        
        return data

def main(load_error_to_db = False,load_error_to_dataset = False):

    #read in data
    f = open("prototype1 (4).csv")
    reader = csv.reader(f)
    data = []
    for i in reader:
            dt = poly_test.convert_str_to_dt(i[0])
            for j in range(1,len(i)):
                i[j] = float(i[j])

            data.append([dt]+i[1:])
    f.close()


    #create different major datasets
    date_data = [i[0] for i in data]
    rcmpl_data = [i[1] for i in data]
    blocked_data = [i[2] for i in data]
    unblocked_data = [i[3] for i in data]

    error_data = []
    
    index = 0    
    while index < len(data):
        this_dt = data[index][0].replace(hour = 0).replace(minute = 0)
        next_dt = this_dt + datetime.timedelta(days = 1)
        daily_data = []

        #group data by day
        while this_dt < next_dt and index < len(data)-1:
            daily_data.append([index,data[index][0],data[index][1]])
            index += 1
            this_dt = data[index][0].replace(hour = 0).replace(minute = 0)

        #create relevant lists
        x_vals = [i for i in range(len(daily_data))]
        y_vals = [i[2] for i in daily_data]

        #create/fit polynomial and detrend data        
        y_new,y_poly = p_poly.poly_detrend(x_vals,y_vals,degree=6,d_type="d")
            
        #detect errors
        error_vals = poly_test.error_detect(y_new,0,20)

        #build error_data list
        for i in range(len(error_vals)):
                error_vals[i] = list(error_vals[i])
                error_vals[i][0] = daily_data[error_vals[i][0]][1]
                error_data.append(error_vals[i])
        
        if index == len(data) - 1:
            break
        

    #add relevant information to original dataset loaded in
    for i in range(len(data)):
        error_flag = False
        for j in range(len(error_data)):
            if data[i][0] == error_data[j][0]:
                #data[i].append(error_data[j][1])
                data[i].append(error_data[j][2])
                data[i].append(1)
                error_flag = True
                error_data.pop(j)
                break
        if not error_flag:
            #data[i].append(None)
            data[i].append(None)
            data[i].append(0)

    #create binary (1 for error at timestamp 0 ow) error list
    error_binary = [i[-1] for i in data]

    #fill in holes for errors
    error_binary_new = checkErrors(error_binary)
    for i in range(len(error_binary_new)):
        data[i].append(error_binary_new[i])

    #create error list to write out/upload to db
    error_list = []
    for i in range(len(data)):
        if data[i][-1] == 1:
            if data[i][4] != None:
                latest_std = data[i][4]
                temp = [data[i][0],data[i][4]]
            else:
                data[i][4] = latest_std
                temp = [data[i][0],latest_std]
            error_list.append(temp)
    
    if load_error_to_db:

        #write out contents
        f = open("error_ts_score.csv",'w')
        writer = csv.writer(f,lineterminator="\n")
        writer.writerows(error_list)
        f.close()

        #upload data to db
        db = MySQLdb.connect("11.120.36.241","internship","Pr3dict!v@","predictiveAnalytics")
        c = db.cursor()
        sql = "LOAD DATA LOCAL INFILE 'error_ts_score.csv' INTO TABLE order_anomalies FIELDS TERMINATED BY ','"
        c.execute(sql)
        db.commit()
        db.close()
        
    if upload_master_dataset:

        #create updated data list
        data = [[i[0],i[1],i[2],i[3],i[6],i[4]] for i in data]

        #write out contents
        f = open("order_dataset.csv",'w')
        writer = csv.writer(f,lineterminator="\n")
        writer.writerows(data)
        f.close()

        #upload data to db
        db = MySQLdb.connect("11.120.36.241","internship","Pr3dict!v@","predictiveAnalytics")
        c = db.cursor()
        sql = "LOAD DATA LOCAL INFILE 'order_dataset.csv' INTO TABLE order_dataset FIELDS TERMINATED BY ','"
        c.execute(sql)
        db.commit()
        db.close()
    
