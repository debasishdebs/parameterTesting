from __future__ import division
import random
import csv
import math
import matplotlib.pyplot as plt



maxDepth = 15
sizeLimit = 20
lambdA = 10
tau = 5


def initializeWorkingSpace(Dmin,Dmax):
    '''
    Redefine the range of each dimension in the feature space s.t. each
    dimension has a new range.
    
    Input: Dmin,Dmax - lists of min and max values for each dimension of
    the feature space. Indices are aligned (e.g. feature1's min and max
    values have the same index in both lists).

    Output: min,max - lists of redefined min and max values for each
    dimension of the feature space. Indicies are aligned. 
    '''
    
    minimums = []
    maximums = []

    for i in range(len(Dmin)):
        s = random.randrange(round(Dmin[i]),round(Dmax[i]))
        sigma = 2*max([s-Dmin[i],Dmax[i]-s])
        minimums.append(s-sigma)
        maximums.append(s+sigma)

    return minimums,maximums
    


def updateMass(x,node,refWin):
    '''
    Update mass r of node argument if x is within the reference window (refWin)
    otherwise update mass l (in the latest time window) of node argument.
    
    Input: x - a test instance (list), node - a node in an HS-Tree (Node object),
    refWin - boolean denoting whether x is wihthin the reference window or not (defined globally, passed in for convenience)
    Output: none
    '''
    global maxDepth
    
    #update mass of node
    if refWin:
        node.r += 1
    else:
        node.l += 1

    if node.level < maxDepth:
        #determine the next node to go to
        if x[node.splitAttr] < node.splitVal:
            nextNode = node.left
        else:
            nextNode = node.right

        updateMass(x,nextNode,refWin)



class Node:

    def __init__(self, leftNode, rightNode, q, p, r, l, k):
        self.left = leftNode
        self.right = rightNode
        self.splitAttr = q
        self.splitVal = p
        self.r = r
        self.l = l
        self.level = k
        

def buildSingleHSTree(minArray, maxArray, k):
    global maxDepth
    if k == maxDepth:
        r = 0
        l = 0
        return Node(None, None, None, None, r, l, k)
    else:
        randomDimn = random.randint(0, len(minArray)-1)
        p = (maxArray[randomDimn] + minArray[randomDimn])/2
        temp = maxArray[randomDimn]
        maxArray[randomDimn] = p
        left = buildSingleHSTree(minArray, maxArray, k+1)
        maxArray[randomDimn] = temp
        minArray[randomDimn] = p
        right = buildSingleHSTree(minArray, maxArray, k+1)
        r = 0
        l = 0
        return Node(left, right, randomDimn, p, r, l, k)

def score(x, node):
    global sizeLimit
    global maxDepth
    #print 'node level: '+str(node.level)
    #print 'node.r: '+str(node.r)
    #try:
    #    print 'node.splitVal: '+str(node.splitVal)
    #    print 'x[node.splitAttr]: '+str(x[node.splitAttr])
    #except:
    #    pass
    if (node.level >= maxDepth) or (node.r <= sizeLimit):
        #print 'reached max level'
        return node.r * math.pow(2,node.level)
    else:
        if x[node.splitAttr] < node.splitVal:
            return score(x, node.left)
        else:
            return score(x, node.right)


class Streaming_HS_trees:

    def __init__(self,winSize,numTrees):

        #first task is to find min and max values for each dimension in stream
        #for now we'll read in a csv file which only contains RCMPL data
        self.dataStream = self.readDataStream()
        self.findRanges()

        global maxDepth
        self.maxDepth = maxDepth
        
        self.winSize = winSize
        self.numTrees = numTrees
        self.alpha = 0.1

        self.trees = []
        self.createTrees()

        self.simulate_data_stream()

    def simulate_data_stream(self):

        current_index = self.winSize
        count = 0
        self.change = 0
        self.d = 0
        self.dev = 0
        self.ref_d = 0
        self.ref_dev = 0
        scores_list = []
        
        while current_index < len(self.dataStream):
            x = self.dataStream[current_index]
            s = 0
            for i in range(len(self.trees)):
                updateMass(x,self.trees[i],False)
                s += score(x,self.trees[i])
            scores_list.append(s)
            count += 1
            if count == self.winSize:
                #detect change
                self.detect_change()
                if self.change >= lambdA:
                    self.update_model()
                    self.change = 0
                #self.reset_node_l()
                count = 0
                
            current_index += 1
           # print self.dataStream[current_index]
        print('finished simulation')

        plt.figure(1)
        plt.subplot(211)
        plt.plot(scores_list)

        plt.subplot(212)
        plt.plot(self.dataStream)
        plt.title("max depth= {}, numTrees = {}, sizeLimit = {}, lambda = {},tau = {}, alpha = {}".format(self.maxDepth,self.numTrees,sizeLimit,lambdA,tau,self.alpha))
        
        plt.show()
        

        output_list = zip(self.dataStream,scores_list)
        f = open('hs_output_alpha05.csv','w')
        writer = csv.writer(f,lineterminator="\n")
        writer.writerows(output_list)
        f.close()

    def reset_node_l(self):
        #resets node

        for i in range(len(self.trees)):
            tree = self.trees[i]
            self.traverse_tree_reset_node_l(tree)
        

    def traverse_tree_reset_node_l(self,node):
        #updates node.l values

        if node.l > 0 or node.r > 0:
                node.l = 0
        if node.level == maxDepth:
            return
        else:
            self.traverse_tree_reset_node_l(node.left)
            self.traverse_tree_reset_node_l(node.right)


    def update_model(self):
        #updates nodes in each tree

        for i in range(len(self.trees)):
            tree = self.trees[i]
            self.traverse_tree_update_nodes(tree)
        self.update_ref_vars()
        

    def update_ref_vars(self):
        #updates reference variables
        
        print 'old ref vars:'
        print 'd: '+str(self.ref_d)
        print 'dev: '+str(self.ref_dev)
        self.ref_d = self.d
        self.ref_dev = self.dev
        print 'new ref vars:'
        print 'd: '+str(self.ref_d)
        print 'dev: '+str(self.ref_dev)
        
            
    def traverse_tree_update_nodes(self,node):
        #updates node masses

        if node.l > 0 or node.r > 0:
                node.r = node.l        
        if node.level == maxDepth:
            return
        else:
            self.traverse_tree_update_nodes(node.left)
            self.traverse_tree_update_nodes(node.right)
        

    def detect_change(self):
        #detects change in mass of nodes
        
        global tau
        
        self.create_high_mass_node_set()
        pct_change = self.calc_pct_change()
        if pct_change > self.ref_d + tau*self.ref_dev:
            #print 'threshold exceeded'
            self.change += 1
        
        self.calc_pred_avg_dev(self.alpha)
        self.calc_pred_pct_change(self.alpha)

    def calc_pred_avg_dev(self,alpha):
        #calculates predicted average deviation of mass

        self.dev = alpha*abs(self.d-self.calc_pct_change()) + (1-alpha)*self.dev

    def create_high_mass_node_set(self):
        #creates list of high mass nodes and nonzero nodes
        
        self.nonzero_nodes = []
        self.high_mass_nodes = []
        
        for i in range(len(self.trees)):
            node = self.trees[i]
            self.traverse_tree_grab_nonzero_mass_nodes(node)
            
        mean_r = self.calc_node_mean()
        for node in self.nonzero_nodes:
            if node.r > mean_r:
                self.high_mass_nodes.append(node)

    def calc_pred_pct_change(self,alpha):

        #calculates predicted percent change
        self.d = alpha*self.calc_pct_change() + (1-alpha)*self.d                

    def calc_pct_change(self):
        #calculates actual percent change

        numerator = sum([abs(node.r - node.l) for node in self.high_mass_nodes])
        denominator = sum([node.r for node in self.high_mass_nodes])
        d = numerator/denominator
        return d
        

    def calc_node_mean(self):
        #calculates the mean of the mass of the nodes

        vals = [node.r for node in self.nonzero_nodes]
        mean_r = sum(vals)/len(self.nonzero_nodes)
        return mean_r
                

    def traverse_tree_grab_nonzero_mass_nodes(self,node):
        #grabs nonzero mass nodes

        if node.level == maxDepth:
            return
        else:
            if node.r > 0 or node.l > 0:
                self.nonzero_nodes.append(node)
            
            self.traverse_tree_grab_nonzero_mass_nodes(node.left)
            self.traverse_tree_grab_nonzero_mass_nodes(node.right)
    
            
    def readDataStream(self):
        #reads in datastream from file
        
        f = open("C:/Users/B004221/Desktop/rcmpl_testing.csv")
        reader = csv.reader(f)
        data = []
        for i in reader:
            for j in range(len(i)):
                i[j] = float(i[j])
            data.append(i)

        data = data[:1000]

        return data

    def findRanges(self):
        #finds ranges of values of dataStream
        
        minList = []
        maxList = []
        for j in range(len(self.dataStream[0])):
            temp = []
            for i in range(len(self.dataStream)):
                temp.append(self.dataStream[i][j])
            minList.append(min(temp))
            maxList.append(max(temp))
        
        self.minList = minList
        self.maxList = maxList

    def createTrees(self):

        #build self.numTrees many HS-trees
        for i in range(self.numTrees):
            new_min_list,new_max_list = initializeWorkingSpace(self.minList,self.maxList)
            tree = buildSingleHSTree(new_min_list,new_max_list,0)
            #update reference mass profile for first self.winSize data points
            #in each tree
            for j in range(self.winSize):
                x = self.dataStream[j]
                updateMass(x,tree,True)
            self.trees.append(tree)
        
            

my_obj = Streaming_HS_trees(5,10)


        





    
    
