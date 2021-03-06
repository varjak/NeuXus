#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 16:35:34 2020

@author: thanos
"""
import pandas as pd
import joblib
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import os
import glob

path = os.system('pwd')
extension = 'csv'
file = glob.glob('*.{}'.format(extension))[0]
#load data
df = pd.read_csv(file, delimiter=';',  decimal=",", header=0)
print(df.head(3))

#assign array of samples
X = df.values[:,2:df.shape[1]].astype(float) #features
y = df['class'].values #class labels

lda = LinearDiscriminantAnalysis()
lda.fit(X, y) #Fit LDA model

print('Score: ',lda.score(X, y))

# save the model to disk
filename = 'lda_model.sav'
joblib.dump(lda, filename)
print('model saved!')
