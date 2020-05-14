from keras.layers import Input, Conv2D, Lambda, merge, Dense, Flatten,MaxPooling2D
from keras.models import Model, Sequential
from keras.regularizers import l2
from keras import backend as K
from keras.optimizers import SGD,Adam
from keras.losses import binary_crossentropy
import numpy.random as rng
import numpy as np
import os
import dill as pickle
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
from keras.datasets import cifar10
import sys
import random

import copy

from PIL import Image

import os
import glob

import time as t


class Siamese_Loader:
    """For loading batches and testing tasks to a siamese net"""
    def __init__(self,Xtrain,Xval,Xtest,Ytrain,Yval,Ytest,resize_param): #Adapted slightly to load directly from cifar10
        numclasses=len(np.unique(Ytrain))

        self.resize_param = resize_param

        self.Xtrain=np.zeros((numclasses,len(Xtrain),resize_param,resize_param,1))
        print("Got number of distinct classes as ",numclasses)
        print("Got new shape of Xtrain as ",self.Xtrain.shape)
        self.valid_tuple=[]
        for i in range(len(Ytrain)): #Warning !! not an efficient implementation, dictionary is recommended 
            self.Xtrain[Ytrain[i],i,:,:,:]=Xtrain[i] #(label, index in dataset and image information )
            self.valid_tuple.append([Ytrain[i],i]) #(label, index in dataset)
        #print("Got new Xtrain as ",self.Xtrain)
        self.Xval = Xval
        self.Yval=Yval

        self.Xtest = Xtest
        self.Ytest=Ytest
        #self.Xtrain = Xtrain
        self.n_classes=numclasses
        self.n_examples,self.w,self.h,_ = Xtrain.shape
        self.n_val,self.n_ex_val,_,_ = Xval.shape

    def get_batch(self,n):
        """Create batch of n pairs, half same class, half different class"""
        categories = rng.choice(self.n_classes,size=(n,),replace=True)
        valid_choice=rng.choice(len(self.valid_tuple),size=(n,),replace=True) #chose n number of elements with replacement
        pairs=[np.zeros((n*n, self.h, self.w,1)) for i in range(2)] #Will create 2 dummy 0 image arrays, each of size n^2

        #print("pairs look like ",pairs[0][1].shape)
        targets=np.zeros((n*n,)) #Placeholder for denoting if the pair have same category or not (0 or 1)
        #print("Shape of targets ",targets.shape)
        for i in range(int(len(valid_choice))):
            for j in range(int(len(valid_choice))):
                t1=self.valid_tuple[valid_choice[i]][0][0]
                t2=self.valid_tuple[valid_choice[j]][0][0]
                pairs[0][n*i+j,:,:,:] = self.Xtrain[self.valid_tuple[valid_choice[i]][0][0],self.valid_tuple[valid_choice[i]][1]].reshape(self.w,self.h,1)
                pairs[1][n*i+j,:,:,:] = self.Xtrain[self.valid_tuple[valid_choice[j]][0][0],self.valid_tuple[valid_choice[j]][1]].reshape(self.w,self.h,1)
                if(t1==t2):
                    targets[n*i+j]=1
                else:
                    targets[n*i+j]=0
        return pairs, targets

    def make_oneshot_task(self,N):
        """Create pairs of test image, support set for testing N way one-shot learning. """
        categories = rng.choice(self.n_val,size=(N,),replace=False)
        indices = rng.randint(0,self.n_ex_val,size=(N,))
        true_category = categories[0]
        ex1, ex2 = rng.choice(self.n_examples,replace=False,size=(2,))
        test_image = np.asarray([self.Xval[true_category,ex1,:,:]]*N).reshape(N,self.w,self.h,1)
        support_set = self.Xval[categories,indices,:,:]
        support_set[0,:,:] = self.Xval[true_category,ex2]
        support_set = support_set.reshape(N,self.w,self.h,1)
        pairs = [test_image,support_set]
        targets = np.zeros((N,))
        targets[0] = 1
        return pairs, targets

    def create_support(self,N):#N controls how many elements you want in the support
        Xval=[]
        Yval=[]
        indices = rng.choice(int(len(self.Yval)),size=(N,),replace=False) #Use the whole training set as the support set
        for i in range(len(indices)):
            Xval.append(self.Xval[indices[i]])
            Yval.append(self.Yval[indices[i]])
        #supports=rng.choice(Xval,size=(N,),replace=False) #Taking support elements from the first half of validation set itself
        #print("shape of supports ",Xval[0].shape)
        #sys.exit(0)

        return Xval,Yval

    def create_pairs_for_single_test(self,num_ways,test_img,test_class):
        #num_ways=100
        supports,classes=self.create_support(num_ways) #testing 100 way one shot learning
        yes_no=[]
        pairs=[np.zeros((num_ways, self.h, self.w,1)) for i in range(2)]
        for i in range(num_ways):
            #print("pairs ",pairs[0][i,:,:,:])
            #print("support[i] ",supports[i])
            #sys.exit(0)
            pairs[0][i,:,:,:]=copy.copy(supports[i])
            pairs[1][i,:,:,:]=copy.copy(test_img)
            if(classes[i]==test_class):
                yes_no.append(1.0)
            else:
                yes_no.append(0.0)
        return pairs,classes,yes_no
    def infer(self,model,test_img,test_class):
        p,c,y_n=self.create_pairs_for_single_test(100,test_img,test_class) #sample 100 images to form a support set and pair those up with the test image
        probs=model.predict(p)
        pred_class=[]
        for i in range(len(probs)):
            if(probs[i]>0.5):
                pred_class.append(c[i])
        pred_class=np.array(pred_class)
        res=np.sum(pred_class)/len(probs)
        print("Percentage chance that this is an image of occupied room ",res)
        return res

    def test_oneshot_ability(self,model,num_ways):
        print("Testing one shot ability ")
        test_set=[]
        occ_acc=0.0
        vac_acc=0.0

        print("Warning ! removing all files in test_result.. wait for validation to finish")
        files = glob.glob('test_results/occupied/*')
        for f in files:
            os.remove(f)
        files = glob.glob('test_results/unoccupied/*')
        for f in files:
            os.remove(f)

        for j in range(len(self.Ytest)): #test on the entire testing set
            p,c,y_n=self.create_pairs_for_single_test(num_ways,self.Xtest[j],self.Ytest[j])
            probs=model.predict(p)
            #print("len(probs) ",len(probs))
            pred_class=[]
            for i in range(len(probs)):
                #print("probs ",probs[i])
                #print("probs[i]>0.5 ",probs[i]>0.5)
                if(probs[i]>=0.5):
                    pred_class.append(c[i])
                    #print("c[i] ",c[i])
            pred_class=np.array(pred_class)
            res=2*np.sum(pred_class)/len(probs) #Multiplying by 2 because half of the support set is occupied and half vacant
            #print("res ",res)
            #print("Percentage chance that this is an image of occupied room ",res)
            

            if(np.round(res)==1 and self.Ytest[j]==1):
                occ_acc+=1.0
                new_im = Image.fromarray((self.Xtest[j].reshape((64,64))).astype(np.uint8))
                new_im.save('test_results/occupied/'+repr(j)+repr(res*100)+'.png')
                print("Saved occupied image ")
            if(np.round(res)==0 and self.Ytest[j]==0):
                vac_acc+=1.0
                new_im = Image.fromarray((self.Xtest[j].reshape((64,64))).astype(np.uint8))
                new_im.save('test_results/unoccupied/'+repr(j)+repr(100*(1-res))+'.png')
                print("Saved unoccupied image ")

        #Test set always contain half occupied and half vacant images
        print("Average accuracy on vacant  ",2*float(vac_acc/len(self.Ytest)))
        print("Average accuracy on occupied ",2*float(occ_acc/len(self.Ytest)))
        print("Now waiting ... ")
        t.sleep(2.0)
        return 2*float(vac_acc/len(self.Ytest)), 2*float(vac_acc/len(self.Ytest))

    def test_oneshot(self,model,N,k,verbose=0):
        """Test average N way oneshot learning accuracy of a siamese neural net over k one-shot tasks"""
        pass
        n_correct = 0
        if verbose:
            print("Evaluating model on {} unique {} way one-shot learning tasks ...".format(k,N))
        for i in range(k):
            inputs, targets = self.make_oneshot_task(N)
            probs = model.predict(inputs)
            if np.argmax(probs) == 0:
                n_correct+=1
        percent_correct = (100.0*n_correct / k)
        if verbose:
            print("Got an average of {}% {} way one-shot learning accuracy".format(percent_correct,N))
        return percent_correct