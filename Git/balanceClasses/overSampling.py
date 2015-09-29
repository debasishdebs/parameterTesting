__author__ = 'Debasish'
import numpy as np
from unbalanced_dataset import OverSampler, SMOTE, EasyEnsemble, SMOTEENN, SMOTETomek, BalanceCascade

class overSampling:
    # Generate the new dataset using under-sampling method

    def __init__(self,verbose,  x, y):
        self.x = x
        self.y = y
        self.verbose = verbose
        self._ratio = float(np.count_nonzero(y==1)) / float(np.count_nonzero(y==0))

    # 'Random over-sampling'
    def random_over_sampling(self):
        OS = OverSampler(ratio=self._ratio, verbose=self.verbose)
        osx, osy = OS.fit_transform(self.x, self.y)
        return osx, osy
    # 'SMOTE'
    def smote(self):
        smote = SMOTE(ratio=self._ratio, verbose=self.verbose, kind='regular')
        smox, smoy = smote.fit_transform(self.x, self.y)
        return  smox, smoy
    # 'SMOTE bordeline 1'
    def smote_boderline1(self):
        bsmote1 = SMOTE(ratio=self._ratio, verbose=self.verbose, kind='borderline1')
        bs1x, bs1y = bsmote1.fit_transform(self.x, self.y)
        return bs1x, bs1y
    # 'SMOTE bordeline 2'
    def smote_boderline2(self):
        bsmote2 = SMOTE(ratio=self._ratio, verbose=self.verbose, kind='borderline2')
        bs2x, bs2y = bsmote2.fit_transform(self.x, self.y)
        return bs2x, bs2y
    # 'SMOTE SVM'
    def smote_svm(self):
        svm_args={'class_weight' : 'auto'}
        svmsmote = SMOTE(ratio=self._ratio, verbose=self.verbose, kind='svm', **svm_args)
        svsx, svsy = svmsmote.fit_transform(self.x, self.y)
        return svsx, svsy
    # 'SMOTE Tomek links'
    def smote_tomek_links(self):
        STK = SMOTETomek(ratio=self._ratio, verbose=self.verbose)
        stkx, stky = STK.fit_transform(self.x, self.y)
        return stkx, stky
    # 'SMOTE ENN'
    def smote_enn(self):
        SENN = SMOTEENN(ratio=self._ratio, verbose=self.verbose)
        ennx, enny = SENN.fit_transform(self.x, self.y)
        return ennx. enny

    # 'EasyEnsemble'
    def easy_ensemble(self):
        EE = EasyEnsemble(verbose=self.verbose)
        eex, eey = EE.fit_transform(self.x, self.y)
        return eex, eey
    # 'BalanceCascade'
    def balance_cascade(sel):
        BS = BalanceCascade(verbose=self.verbose)
        bsx, bsy = BS.fit_transform(self.x, self.y)
        return bsx, bsy
