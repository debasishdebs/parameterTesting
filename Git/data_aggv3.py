#Data Aggregator v3

import pymysql
import datetime
import pandas as pd
import csv


class table_creator:

    def __init__(self):
        
        #instantiate db and cursor objects for MCOM and PA dbs respectively
        self.PA_db = self.connect_PA_db()
        self.PA_cursor = self.PA_db.cursor()
        self.mcom_db = self.connect_mcom_db()
        self.mcom_cursor = self.mcom_db.cursor()

        self.prompt_user()
        

    def prompt_user(self):
        '''
        Asks user if they would like to use (update) an existing table or not
        Calls: create_table
        Returns: None
        '''

        existing_table_response = raw_input("Would you like to use an existing table? y/n ")

        while existing_table_response != "y" and existing_table_response != "Y" and existing_table_response != "n" and existing_table_response != "N": #Makes sure they enter y or n
            existing_table_response = raw_input("Would you like to use an existing table? y/n ")

        if existing_table_response == "y" or existing_table_response == "Y": #Runs if the table they want to use exists
            pass
        elif existing_table_response == "n" or existing_table_response == "N": #Runs if they want a new table
            self.create_table()

    def connect_PA_db(self):
        '''
        Connects to predictiveAnalytics database
        Returns: database connection object
        '''
        
        db = pymysql.connect(host = "11.120.36.241", db = "predictiveAnalytics", user = "internship", passwd = "Pr3dict!v@")
        return db
    

    def connect_mcom_db(self):
        '''
        Connects to mcom_metrics database
        Returns: database connection object
        '''
        db = pymysql.connect(host = "11.120.236.206", db = "mcom_metrics", user = "internship", passwd = "Pr3dict!v@")
        return db

    def create_table(self):
        '''
        Creates and populates new table in predictiveAnalytics database
        Calls: show_tables, show_columns, create_sql, execute_sql
        Returns: None
        '''

        self.table_name = raw_input("What would you like the name of the new table to be called? ")
        tables = self.show_tables() #calls show_tables so user can input the tables they want

        sql_statements = []
        self.columns = []
        self.interval_size = {}

        for table in tables:
            columns = self.show_columns(table) #shows columns for each table specified
            for column in columns:
                #creates & stores sql statements used to select data from mcom_metrics db
                sql = self.create_sql(table,column)
                if type(sql) == list:
                        sql_statements += sql
                elif type(sql) == str:
                        sql_statements.append(sql)

        #determine the maximum time interval size of the chosen metrics
        self.max_interval_size = max(list(self.interval_size.values()))

        #prompts user for how far in the future they would like to consider
        look_ahead_len = raw_input("\nWhat is your lookahead (i.e. future prediction) length in minutes? \n(Note time intervals between columns will be: {} minutes. Please use a multiple of this interval): ".format(self.max_interval_size))
        look_ahead_len = int(look_ahead_len)
        self.look_ahead_len = look_ahead_len
        
        #creates inital part of the CREATE TABLE sql statement based on chosen metrics
        create_table_sql = "CREATE TABLE {} ( timestamp datetime, \n".format(self.table_name)

        self.column_names = list(set(self.columns))+['error']+self.create_e_columns()
        
        
        #construct the remaining CREATE TABLE sql statement based on chosen metrics
        for column in self.column_names[:-1]:
            create_table_sql += column+" INT,\n"
        create_table_sql += self.column_names[-1] + " INT);"
        print("\n"+create_table_sql+"\n")



        #create table in db
        self.PA_cursor.execute(create_table_sql)
        
        #populate table
        self.execute_sql(sql_statements)
        
    def create_e_columns(self):
        '''
        Adds on to the self.column_names list the appropriate
        amount of strings based on interval size and look ahead length
        (error column headers)
        Returns: None
        '''

        e_cols = []
        num_e_cols = self.look_ahead_len/self.max_interval_size
        for i in range(num_e_cols):
            e_cols.append("e_"+str((i+1)*self.max_interval_size))

        return e_cols

    def show_tables(self):
        """
        Show all tables in mcom_metrics database, prompts user to choose which they would like to pull from
        Returns: list of tables as strings the user chooses
        """
        
        sql = "SHOW TABLES FROM mcom_metrics"
        self.mcom_cursor.execute(sql)
        results = list(self.mcom_cursor.fetchall())
        for i in results:
            print(i[0])
        tables = raw_input("Please type the tables you would like to pull from seperated by commas(,): ")
        tables = tables.split(",")
        return tables

    
    def show_columns(self, table):
        """
        Shows all columns for given table, prompts user choose which they would like to use as metrics
        Returns: list of columns as strings chosen by the user
        """

        sql = "SHOW COLUMNS FROM {}".format(table)
        self.mcom_cursor.execute(sql)
        results = list(self.mcom_cursor.fetchall())
        print("\nPossible Columns from {} table: (timestamp column always chosen by default) ".format(table))
        for column in results:
            print("\t{}".format(column[0]))
        columns = raw_input("Please type the columns you would like to pull from seperated by commas(,): ")
        columns = columns.split(",")
        return columns
    

    def create_sql(self, table, column):
        '''
        Creates sql statements for SELECTing metrics from the table and column parameters
        Returns: sql statement (str) in non-vertically structured case
        Returns: list of sql statements (str) in vertically structured cased
        '''

        #Ask the user if the column chosen is vertically structured
        answer = raw_input("Is the {} column vertically structured? ".format(column))
        
        '''
        Vertically structured column e.g.
        
        Table: rt_orders_min
        |timestamp  |type       |count  |
        |10:50AM    |RCMPL      |5      |
        |10:50AM    |BCMPL      |3      |
        |10:50AM    |IS_RCMPL   |1      |
        |10:50AM    |IS_BCMPL   |0      |
        |...        |...        |...    |

        Want to extract all rows with RCMPL, essentially creating a table
        that looks like this:
        |timestamp  |RCMPL  |
        |10:50AM    |5      |
        |10:55AM    |7      |
        |11:00AM    |10     |
        |...        |...    |


        If the column chosen is similar to the 'type' column above then said
        column is VERTICALLY STRUCTURED
        '''


        if answer == "n":
            #create sql statement
            sql = "SELECT timestamp," + column + " FROM " + table + " WHERE timestamp >= %s AND timestamp < %s"
            self.columns.append(column)
            
            #Determine time interval size of chosen metric
            self.mcom_cursor.execute("SELECT timestamp FROM {} ORDER BY timestamp DESC LIMIT 10".format(table))
            results = self.mcom_cursor.fetchall()

            #case where not enough rows for given metric to determine time interval size
            if len(results) < 6:
                print "Unable to use {} metric -- not enough data points".format(chosen_pairs[i][0])
                return

            time_difference1 = (results[0][0]-results[1][0]).seconds//60
            time_difference2 = (results[1][0]-results[2][0]).seconds//60
            time_difference3 = (results[2][0]-results[3][0]).seconds//60
            time_difference4 = (results[3][0]-results[4][0]).seconds//60
            time_difference5 = (results[4][0]-results[5][0]).seconds//60
            time_list = [time_difference1,time_difference2,time_difference3,time_difference4,time_difference5]
            time_list.sort()
            median_time = time_list[2]
            
            self.interval_size[column] = median_time
            return sql

        #case where column is vertically structured
        elif answer == "y":

            #sql for extracting possible column headers
            sql = "SELECT DISTINCT {} FROM {}".format(column,table)
            self.mcom_cursor.execute(sql)
            headers = self.mcom_cursor.fetchall()
            print("possible column headers: ")
            for header in headers:
                    print("\t{}".format(header[0]))
            #prompt the user to choose key:value pairs from possible columns and actual columns
            chosen_pairs = raw_input("Please type column value pairs seperated by semicolons e.g. RCMPL,count; BCMPL,count: ")
            chosen_pairs = chosen_pairs.split(";")

            sql_list = []

            #loop over key:value pairs inputted by the user
            for i in range(len(chosen_pairs)):
                    chosen_pairs[i] = chosen_pairs[i].split(",")

                    #create sql statement for extracting specified metric
                    sql = "SELECT timestamp, {}, {} FROM {} WHERE {} = '{}' AND timestamp >= %s AND timestamp < %s".format(column, chosen_pairs[i][1], table,column, chosen_pairs[i][0])
                    sql_list.append(sql)
                    self.columns.append(chosen_pairs[i][0])
                    
                    ###Determine time interval size of chosen metric###
                    self.mcom_cursor.execute("SELECT timestamp FROM {} Where {} = '{}' ORDER By timestamp DESC LIMIT 10".format(table,column,chosen_pairs[i][0]))
                    results = self.mcom_cursor.fetchall()

                    #case where not enough rows for given metric to determine time interval size
                    if len(results) < 6:
                        print "Unable to use {} metric -- not enough data points".format(chosen_pairs[i][0])
                        continue                        
                    time_difference1 = (results[0][0]-results[1][0]).seconds//60
                    time_difference2 = (results[1][0]-results[2][0]).seconds//60
                    time_difference3 = (results[2][0]-results[3][0]).seconds//60
                    time_difference4 = (results[3][0]-results[4][0]).seconds//60
                    time_difference5 = (results[4][0]-results[5][0]).seconds//60
                    time_list = [time_difference1,time_difference2,time_difference3,time_difference4,time_difference5]
                    time_list.sort()
                    median_time = time_list[2]
        
                    self.interval_size[chosen_pairs[i][0]] = median_time
                    ###
            
            return sql_list

    def execute_sql(self, sql_list):
        '''
        Functionality:
        1. Executes sql statements passed in through sql_list parameter in monthly intervals
        2. Combines datasets which contain the same metric but were pulled from different tables
        3. Aggregates resulting datasets to max_time_interval size, if needed
        4. Combines datasets into a single dataframe
        5. Writes out dataframe to a csv files
        6. Puts data from csv file into db
        '''

        #Determine relevant dates and times used to start and stop the execution of sql statements
        now = datetime.datetime.now().replace(second = 0).replace(microsecond = 0)
        later = now - datetime.timedelta(weeks = 4)

        #Define the maximum past date to consider to be January 1st 2013 (this is apparently when MCOM 'got big')
        stop = datetime.datetime(2013,1,1,0,0)
        
        self.master_set=[]

        self.file_flag = False

        #Loop over time
        while later > stop:
                month_data = []
                #Loop over sql statements
                for i in range(len(sql_list)):
                        sql = sql_list[i]
                        col = self.columns[i]
                        #execute sql
                        check = self.mcom_cursor.execute(sql,(later,now))
                        if check != 0:
                            #extract data
                            temp = list(self.mcom_cursor.fetchall())
                            for j in range(len(temp)):
                                #check length of each row of data, if not eqal to 3, reformat it so
                                #want each row to take the form: [timestamp,column,value]
                                if len(temp[j]) != 3:
                                    temp[j] = list(temp[j])
                                    temp[j].insert(1, col)
                            month_data.append(temp)
                        

                #merge all data into a single dataset for each metric
                #e.g. if RCMPL comes from rt_orders_min and rt_orders_min_hist tables, then put all RCMPL rows into one dataset
                month_data = self.init_merge(month_data)

                #ensure all datasets are sorted from present --> historical
                for i in range(len(month_data)):
                    month_data[i] = sorted(month_data[i])[::-1]

                #check the sizes of the time intervals of datasets, aggregate if needed up to max_interval_size
                all_datasets = []
                for dataset in month_data:
                        key = dataset[0][1]
                        interval_size = self.interval_size[key]
                        if interval_size != self.max_interval_size:
                                dataset = self.aggregate(dataset, self.max_interval_size)
                                all_datasets.append(dataset)
                        else:
                                all_datasets.append(dataset)

                #combine all datasets into one master dataset                                    
                reformatted_data = self.reformat(all_datasets)
                
                #reconvert datasets from dataframe to a 2D list
                reformatted_data = reformatted_data.values.tolist()
                reformatted_data = self.reconvert_data(reformatted_data)
                
                #Labels when errors occur
                error_ds = self.label_errors(reformatted_data)

                #merge errors and data sets
                final_ds = self.merge_errors_to_ds(reformatted_data,error_ds)

                #check if output csv has been created or not
                if self.file_flag == False:
                    f = open(self.table_name+".csv",'w')
                    final_ds.insert(0,self.column_names)
                    self.file_flag = True
                    self.write_to_csv(final_ds,f)
                elif self.file_flag == True:
                    f = open(self.table_name+".csv",'a')
                    self.write_to_csv(final_ds,f)
                
                #update time
                now = final_ds[-1][0]
                later = later - datetime.timedelta(weeks = 4)

    def merge_errors_to_ds(self,dataset,errorset):
        '''
        Merge dataset to errorset
        Return: merged dataset (list)
        '''
        for i in range(len(dataset)):
            for row in errorset:
                ts = dataset[i][0]
                if ts == row[0]:
                    dataset[i] += row[3:]
                    break


        return dataset
        
        
    def write_to_csv(self,dataset,f):
        '''
        Takes final_ds and  writes or appends to file f
        Returns: None
        '''
        writer = csv.writer(f,lineterminator="\n")
        writer.writerows(dataset)
        f.close()
        
        

    def reformat(self,dataset):
        '''
        Converts list of datasets into one master dataset, as a pandas dataframe object
        Returns: dataframe containing all metrics
        '''

        #Convert to dataframe
        pd_list = []
        for ds in dataset:
            my_list = [[i[0].replace(second = 0)]+[i[-1]] for i in ds]
            col = ds[0][1]
            val_list = [i[-1] for i in ds]
            df = pd.DataFrame(my_list,columns = ['timestamp',col])
            #print df
            pd_list.append(df)

        #Merge dataframes
        master_df = pd_list[0]
        for df in pd_list[1:]:
            master_df = pd.merge(master_df,df,on='timestamp')
        
    
        return master_df


    def init_merge2(self,dataset):

        df_list = []
        for ds in dataset:
            #convert to dataframe
            my_list = [[i[0].replace(second = 0)]+[i[-1]] for i in ds]
            col = ds[0][1]
            val_list = [i[-1] for i in ds]
            df = pd.DataFrame(my_list,columns = ['timestamp',col])
            df_list.append(df)

        print(pd.concat(df_list,join='inner',verify_integrity=True))

        
            
            

    def label_errors(self, dataset):
        '''
        Labels dataset passed in with errors under the condition RCMPL = 0 for that timestamp and that timestamp+1
        Returns: 2D list labeled with errors
        '''

        #extract RCMPL data from mcom_metric's rt_orders_min and rt_orders_min_hist tables        
        start_ts = dataset[1][0]
        end_ts = dataset[-1][0]
        sql = "SELECT timestamp, type, count FROM rt_orders_min WHERE type = 'RCMPL' AND timestamp >= %s AND timestamp < %s ORDER BY timestamp DESC"
        self.mcom_cursor.execute(sql,(end_ts,start_ts))
        ds_1 = (list(self.mcom_cursor.fetchall()))
        sql = "SELECT timestamp, type, count FROM rt_orders_min_hist WHERE type = 'RCMPL' AND timestamp >= %s AND timestamp < %s ORDER BY timestamp DESC"
        self.mcom_cursor.execute(sql,(end_ts,start_ts))
        ds_2 =(list(self.mcom_cursor.fetchall()))

        print start_ts
        print end_ts
        print(len(ds_1))
        print(len(ds_2))

        #Merge error data (or don't)
        if len(ds_1) == 0:
            error_ds = ds_2
        elif len(ds_2) == 0:
            error_ds = ds_1
        else:
            error_ds = self.init_merge([ds_1,ds_2])[0]

        error_ds.sort(reverse = True)

        #aggregate error data
        error_ds = self.aggregate(error_ds, self.max_interval_size)

        error_ds.sort()

        i = 0
        while i < len(error_ds)-1:
            #check if this timestamp and next timestamp have 0 orders
            if error_ds[i][2] == 0 and error_ds[i+1][2] == 0:
                #print('error detected')
                #print(error_ds[i])
                #record the start of the error
                error_ds[i].append(1)
                j = 1
                while error_ds[i+j][2] == 0 and i+j < len(error_ds):
                    #print('non error')
                    #print(error_ds[i])
                    #record that these are not the start of an error
                    error_ds[i+j].append(0)
                    j += 1
                i += j
            else:
                #print(error_ds[i])
                error_ds[i].append(0)
                i+=1

                
        error_ds = self.transpose_errors(error_ds)

        return error_ds


    def transpose_errors(self,error_ds):
        '''
        Takes each timestamp in error_ds and transposes the error column to indicate
        whether or not an error occured in the future in intervals the size of
        max_interval_size, the number of additional columns created is equal to
        look_ahead_time/max_interval_size
        Returns: error_ds (list) with error column transposed to rows
        '''

        interval_count = self.look_ahead_len/self.max_interval_size

        error_ds = sorted(error_ds)

        for i in range(len(error_ds)):
            if i+interval_count < len(error_ds):
                #take according slice
                raw_list = error_ds[i+1:i+interval_count+1]
                for j in range(len(raw_list)):
                    raw_list[j] = raw_list[j][-1]
                #extend this row
                error_ds[i] += raw_list

        #truncate dataset, only keeping fully complete rows
        error_ds = error_ds[:-interval_count]

        error_ds = error_ds[::-1]

        return error_ds
        

    def reconvert_data(self,dataset):
        '''
        Reconverts 2D list (dataset)'s values to datetime/int objects
        Returns: converted 2D list
        '''

        for i in range(len(dataset)):
            ts = dataset[i][0]
            ts = str(ts)
            ts = self.convert_str_to_dt(ts)
            dataset[i][0] = ts
            for j in range(1,len(dataset[i])):
                dataset[i][j] = int(dataset[i][j])
        
        return dataset

    def convert_str_to_dt(self,aStr):
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


    def init_merge(self,ds_all):
        '''
        Takes a list of datasets, and merges those which contain the same metric
        Returns: 2D list of merged sublists
        '''
        
        i = 0
        while i < len(ds_all):
            merged = ds_all[i]
            j = i+1
            while j < len(ds_all):
                if merged[0][1] == ds_all[j][0][1]:
                    merged += ds_all[j]
                    ds_all.remove(ds_all[j])
                else:
                    j += 1
            ds_all[i] = merged
            i += 1

        output_ds = []

        #remove duplicates from each dataset
        for ds in ds_all:
            ts_list = list(set([i[0] for i in ds]))
            temp_ds = []
            for row in ds:
                if row[0] in ts_list:
                    temp_ds.append(row)
                    ts_list.remove(row[0])
                else:
                    print 'duplicate removed'
            output_ds.append(temp_ds)               
        
        return output_ds

    def aggregate(self,dataset,interval):
        '''
        Aggregates data points from the dataset parameter to match the time interval size
        determined by the interval paramter
        Returns: aggregated 2D list
        '''

        print "\nAggregating {} dataset to {} minute intervals".format(dataset[0][1],interval)

        reformatted_data = []

        #Find first timestamp that is a multiple of the interval parameter
        start_time = dataset[0][0]
        while start_time.minute % interval != 0:
            start_time -= datetime.timedelta(minutes = 1)

        current_index = 0
        end_time = start_time

        #loop over remaining dataset, aggregating values
        while current_index < len(dataset):
            val = 0
            end_time = start_time - datetime.timedelta(minutes = interval)
            while start_time > end_time and current_index < len(dataset):
                val += dataset[current_index][2]
                start_time -= datetime.timedelta(minutes = 1)
                current_index += 1
                
            reformatted_data.append([start_time,dataset[0][1],val])

        return reformatted_data

    
table_creator()
