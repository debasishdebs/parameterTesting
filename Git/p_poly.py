import csv
import numpy
import pylab

def poly_detrend(x,y,degree=4,plot1=False,plot2=False,d_type='d'):
    '''
    Fits a piecewise polynomial of the specified degree to the data passed in as x and y
    Takes difference/ratio between datapoint and polynomial to detrend data
    Parameters: x (list) - 1D list of x coordinate values
                y (list) - 1D list of y coordinate values
                degree (int) - the degree of the polynomial to fit
                plot1 (bool) - True if you want a plot of the polynomial overlaid on the input data
                plot2 (bool) - True if you want a plot of detrended data
                d_type (str, either "d" or "r") - "d" for difference between datapoint and polynomial
                                                  "r" for ratio between datapoint and polynomial
    Returns: y_new (list) - 1D list of detrended y-coordinate values
             y_poly (list) - 1D list of polynomial y-coordinate values
    '''

    #Create polynomial function    
    poly = numpy.polyfit(x,y,degree)
    poly_func = numpy.poly1d(poly)

    #Apply polynomial function
    y_poly = [poly_func(i) for i in x]

    y_new = []

    #detrend data
    if d_type == 'd':
        for i in range(len(y)):
            y_temp = y[i] - poly_func(i)
            y_new.append(y_temp)
    
    elif d_type == 'r':
        for i in range(len(y)):
            y_temp = float(y[i])/float(poly_func(i))
            y_new.append(y_temp)

    #plot results
    if plot1:
        import pylab
        pylab.plot(x,y,'o')
        pylab.plot(x,y_poly,'r-')
        pylab.show()

    if plot2:
        import pylab
        pylab.plot(x,y_new)
        pylab.show()

    return y_new,y_poly




######Code below used for testing######

##def test(filepath,plot=True):
##    import pylab
##    import numpy
##
##    f = open("C:/Users/B004221/Desktop/rcmpl_testing.csv")
##    reader = csv.reader(f)
##    data = []
##    for i in reader:
##        data.append(float(i[0]))
##    f.close()
##
##    data = data[:1000]
##
##    y_new = []
##    var_list = []
##    
##    index = 0
##    while index < len(data):
##        test_slice = data[index:index+200]
##        x_vals = [i for i in range(len(test_slice))]
##        try:
##            y_temp,y_poly = poly_detrend(x_vals,test_slice,degree=4,d_type='d')
##            for i in range(len(y_temp)):
##                #print(y_poly[i],test_slice[i])
##                y_new.append(y_temp[i])                
##
##        except:
##            pass
##        index += 200
##
##    f = open("rcmpl_detrend.csv",'w')
##    writer = csv.writer(f,lineterminator="\n")
##    writer.writerows([[i] for i in y_new])
##    
##
##    if plot:
##        x_vals = [i for i in range(len(y_new))]
##        pylab.plot(x_vals,y_new,"r-")
##        pylab.show()     
