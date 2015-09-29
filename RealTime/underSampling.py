__author__ = 'Debasish'

from unbalanced_dataset import UnderSampler, TomekLinks, ClusterCentroids, NearMiss, \
    CondensedNearestNeighbour, OneSidedSelection, NeighbourhoodCleaningRule

class underSampling:
    # Generate the new dataset using under-sampling method

    def __init__(self, verbose, x, y):
        self.verbose = verbose
        self.x = x
        self.y = y
    # 'Random under-sampling'
    def under_sampling(self):
        US = UnderSampler(verbose=self.verbose)
        usx, usy = US.fit_transform(self.x, self.y)
        print "Under Sampling Transformed"
        return usx, usy
    # 'Tomek links'
    def tomek_links(self):
        TL = TomekLinks(verbose=self.verbose)
        tlx, tly = TL.fit_transform(self.x, self.y)
        print "TomekLins Transformed"
        return tlx, tly
    def clustering_centroids(self):
        # 'Clustering centroids'
        CC = ClusterCentroids(verbose=self.verbose)
        ccx, ccy = CC.fit_transform(self.x, self.y)
        print "Clustering Centroids Transformed"
        return ccx, ccy
    # 'NearMiss-1'
    def near_miss1(self):
        NM1 = NearMiss(version=1, verbose=self.verbose)
        nm1x, nm1y = NM1.fit_transform(self.x, self.y)
        print "Near Miss Transformed"
        return nm1x, nm1y
    # 'NearMiss-2'
    def near_miss2(self):
        NM2 = NearMiss(version=2, verbose=self.verbose)
        nm2x, nm2y = NM2.fit_transform(self.x, self.y)
        print "Near Miss 2 Transformed"
        return nm2x, nm2y
    # 'NearMiss-3'
    def near_miss3(self):
        NM3 = NearMiss(version=3, verbose=self.verbose)
        nm3x, nm3y = NM3.fit_transform(self.x, self.y)
        print "Near Miss 3 transformed"
        return nm3x, nm3y
    # 'Condensed Nearest Neighbour'
    def condensed_nn(self):
        CNN = CondensedNearestNeighbour(size_ngh=51, n_seeds_S=51, verbose=self.verbose)
        cnnx, cnny = CNN.fit_transform(self.x, self.y)
        print "Condensed NN Transformed"
        return cnnx, cnny
    # 'One-Sided Selection'
    def one_sided_selection(self):
        OSS = OneSidedSelection(size_ngh=51, n_seeds_S=51, verbose=self.verbose)
        ossx, ossy = OSS.fit_transform(self.x, self.y)
        print "OSS Transforemd"
        return ossx, ossy
    # 'Neighboorhood Cleaning Rule'
    def neighbourhood_cleaning_rule(self):
        NCR = NeighbourhoodCleaningRule(size_ngh=51, verbose=self.verbose)
        ncrx, ncry = NCR.fit_transform(self.x, self.y)
        print "Neighbourhood Cleaning Transformed"
        return ncrx, ncry
