import csv
import pandas as pd
from sklearn.metrics import *
from collections import Counter
from ggplot import *
import os
        
def read_file(fname):
    lines = csv.reader(open(fname, "rt"))
    dataset = list(lines)
    return dataset

def main():
    fname = raw_input("Enter File Name? (If in diff dir, enter full path)")
    if fname.endswith('.csv'):
        status = True
    else:
        status = False
        
    if status == True:
        err_col = raw_input("Enter error column number")
        err_col = int(err_col)
        pred_col = raw_input("Enter prediction column number")
        pred_col = int(pred_col)
        prob_pred_col = raw_input("Enter class probability column number")
        prob_pred_col = int(prob_pred_col)
        ftr = raw_input("How far out is prediction column? (5min, 10min, 15min..). Enter only minutes (5/10/15..)")
        ftr = int(ftr)
        if ftr in [5, 10, 15, 20, 25, 30] :
            ind = ftr/5
            dataset = read_file(fname)
            err_column = []
            pred_column = []
            prob_pred_column = []
            for i in range(1,len(dataset)):
                err_column.append(dataset[i][err_col])
                pred_column.append(dataset[i][pred_col])
                prob_pred_column.append(dataset[i][prob_pred_col])
            #print len(err_column)
            err_column = err_column[ind:]
            pred_column = pred_column[:-1*ind]
            prob_pred_column = prob_pred_column[:-1*ind]
            print len(err_column), len(pred_column)
            print set(pred_column)
            err_column = pd.Series(data=err_column)
            pred_column = pd.Series(data=pred_column)
            
            ct = pd.crosstab(err_column, pred_column,rownames=['actual'], colnames=['preds'])
            print "Confusion Matrix :\n", ct
            
            e_col = [int(x) for x in err_column]
            prob_pred_column = [float(x) for x in prob_pred_column]
            auc = roc_auc_score(e_col, prob_pred_column)
            fpr, tpr, threshold = roc_curve(e_col, prob_pred_column)
            p = Counter(err_column)['1']
            n = Counter(err_column)['0']     
            tp = tpr*p
            fp = fpr*n     
            df = pd.DataFrame(dict(fp=fp, tp=tp))
            plt = ggplot(df, aes(x='fp',y='tp')) + geom_line() + geom_abline(linetype='dashed') +\
                ggtitle("ROC Curve w/ AUC=%s" % str(auc))
            ggsave(filename=os.getcwd() + '\\oob\\31_05\\max_feature_sqrt\\manual_balance_class\\singleFile\\auc.png', plot=plt) 
        else:
            print "Please enter correct far out prediction time"
            print "Calling main() again. Enter details correctly."
            main()
    else:
        print "The filename you entered aint .csv. Please enter a .csv file"
        choice = raw_input("Enter choice:\n1:Quit\n2:Restart")
        if choice == '1':
            exit()
        elif choice == '2':
            main()

            
        
main()
