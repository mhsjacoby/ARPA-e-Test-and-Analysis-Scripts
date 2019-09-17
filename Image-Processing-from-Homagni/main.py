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
import csv

from numpy.random import seed
seed(1)
from tensorflow import set_random_seed
set_random_seed(2)

gpu = '0'

os.environ["KERAS_BACKEND"] = "tensorflow"
os.environ["CUDA_VISIBLE_DEVICES"] = gpu
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
from keras import backend as K
K.set_session(sess)

##########
#package imports 
from models import siamese,siameseVAE
from utils import Siamese_Loader

from PIL import Image
import glob
import copy

def maxpooling(array,supersize,filename,infer):
    new_a=np.zeros_like(array,dtype=np.float32)
    for i in range(np.shape(array)[0]-supersize[0]):
        for j in range(np.shape(array)[1]-supersize[1]):
            patch=array[i:i+supersize[0],j:j+supersize[1]]
            new_a[i:i+supersize[0],j:j+supersize[1]]+=np.max(patch)/(supersize[0]*supersize[1])
    new_im = Image.fromarray(new_a.astype(np.uint8))
    '''
    if infer==True:
        new_im.save('test_data/blurred'+repr(supersize)+'/'+filename)
    else:
        new_im.save('testpooling'+repr(supersize)+'/'+filename)
    '''
    return new_a

def data_process(Filename, label, pooling_param, resize_param):
    image_list=[]
    labels=[]

    for filename in glob.glob(Filename): #assuming gif
        im=Image.open(filename)
        #im = im.resize((32, 32))
        print("maxpooling callibration occupancy data ")
        array=np.array(im)
        array=maxpooling(array,pooling_param,filename,False)
        new_im = Image.fromarray(array)
        im = new_im.resize((resize_param, resize_param))

        im=np.array(im)
        im=np.reshape(im,(resize_param,resize_param,1))
        image_list.append(im)
        labels.append(label)
    return image_list, labels
def pickle_save(x_train,y_train,x_val,y_val,x_test,y_test):
    x_train_file = open('x_train_file.obj', 'wb')
    pickle.dump(x_train, x_train_file)
    x_train_file.close()

    y_train_file = open('y_train_file.obj', 'wb')
    pickle.dump(y_train, y_train_file)
    y_train_file.close()

    x_val_file = open('x_val_file.obj', 'wb')
    pickle.dump(x_val, x_val_file)
    x_val_file.close()

    y_val_file = open('y_val_file.obj', 'wb')
    pickle.dump(y_val, y_val_file)
    y_val_file.close()

    x_test_file = open('x_test_file.obj', 'wb')
    pickle.dump(x_test, x_test_file)
    x_test_file.close()

    y_test_file = open('y_test_file.obj', 'wb')
    pickle.dump(y_test, y_test_file)
    y_test_file.close()

def pickle_load():
    x_train_file = open('x_train_file.obj', 'rb')
    x_train = pickle.load(x_train_file)
    x_train_file.close()

    y_train_file = open('y_train_file.obj', 'rb')
    y_train = pickle.load(y_train_file)
    y_train_file.close()

    x_val_file = open('x_val_file.obj', 'rb')
    x_val = pickle.load(x_val_file)
    x_val_file.close()

    y_val_file = open('y_val_file.obj', 'rb')
    y_val = pickle.load(y_val_file)
    y_val_file.close()

    x_test_file = open('x_test_file.obj', 'rb')
    x_test = pickle.load(x_test_file)
    x_test_file.close()

    y_test_file = open('y_test_file.obj', 'rb')
    y_test = pickle.load(y_test_file)
    y_test_file.close()

    return x_train,y_train,x_val,y_val,x_test,y_test


def read_images(filename_occ, filename_unocc, pooling_param, resize_param):
    image_list_train = []
    image_list_val = []
    image_list_test = []

    y_train=[]
    y_val = []
    y_test = []

    try:
        x_train,y_train,x_val,y_val,x_test,y_test = pickle_load()
        return x_train,y_train,x_val,y_val,x_test,y_test
    except:
        print("Preprocessed files dont exist ")

    x,y = data_process('cal_data/'+filename_occ+'/*.png', 1, pooling_param, resize_param) # 1 for occupied label
    image_list_train.extend(x)
    y_train.extend(y)

    x,y = data_process('cal_data/'+filename_unocc+'/*.png', 0, pooling_param, resize_param) # 1 for occupied label
    image_list_train.extend(x)
    y_train.extend(y)

    x,y = data_process('sup_set/'+filename_occ+'/*.png', 1, pooling_param, resize_param) # 1 for occupied label
    image_list_val.extend(x)
    y_val.extend(y)

    x,y = data_process('sup_set/'+filename_unocc+'/*.png', 0, pooling_param, resize_param) # 1 for occupied label
    image_list_val.extend(x)
    y_val.extend(y)

    x,y = data_process('test_set/'+filename_occ+'/*.png', 1, pooling_param, resize_param) # 1 for occupied label
    image_list_test.extend(x)
    y_test.extend(y)

    x,y = data_process('test_set/'+filename_unocc+'/*.png', 0, pooling_param, resize_param) # 1 for occupied label
    image_list_test.extend(x)
    y_test.extend(y)


    x_train= np.array(image_list_train)
    x_val= np.array(image_list_val)
    x_test= np.array(image_list_test)

    y_train= np.array(y_train)
    y_train= np.reshape(y_train,(len(y_train),1))

    y_val= np.array(y_val)
    y_val= np.reshape(y_val,(len(y_val),1))

    y_test= np.array(y_test)
    y_test= np.reshape(y_test,(len(y_test),1))

    #Save them to pickle for fast loading later on
    pickle_save(x_train,y_train,x_val,y_val,x_test,y_test)

    return x_train,y_train,x_val,y_val,x_test,y_test


def main():
    #control the image maxpooling parameter
    pooling_param=[2,2]
    resize_param = 64

    x_train, y_train, x_val, y_val, x_test, y_test=read_images('occupied','unoccupied',pooling_param, resize_param)
    print("y_train shape ",y_train.shape)

    loader=Siamese_Loader(x_train,x_val,x_test,y_train,y_val,y_test, resize_param)
    #loader.create_support(20)
    sm=siamese(resize_param,1,False)
    '''
    #******************CODE FOR TESTING PERFORMANCE **********************
    # Just testing performance, make sure model loads the weights
    gt_occ=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    counter=0
    c_occ=0
    c_unocc=0
    w_occ=0
    w_unocc=0
    for filename in glob.glob('test_data/*.png'): #assuming gif
        imo=Image.open(filename)

        print("maxpooling testing data ")
        array=np.array(imo)
        array=maxpooling(array,pooling_param,filename,True)
        new_im = Image.fromarray(array)
        im = new_im.resize((32, 32))

        im = im.resize((32, 32))
        im=np.array(im)
        im=np.reshape(im,(32,32,1))
        res= loader.infer(sm.siamese_net,im,1)#Last argument doesnt matter

        #Getting the conf. matrix
        if(res>0.5 and gt_occ[counter]==1):
            c_occ+=1
        if(res<0.5 and gt_occ[counter]==0):
            c_unocc+=1
        if(res<0.5 and gt_occ[counter]==1):
            w_unocc+=1
        if(res>0.5 and gt_occ[counter]==0):
            w_occ+=1

        filename.replace('.png', '')
        imo.save('test_data/true_pred'+repr(pooling_param)+'/'+filename+repr(res)+'.png')
        counter+=1
    #sm1=siameseVAE(28,1,200,50,32) #Need to try this for MNIST
    print("True Positives ",c_occ)
    print("True negatives ",c_unocc)
    print("False positives ",w_occ)
    print("False negatives ",w_unocc)

    sys.exit(0)
    #******************CODE FOR TESTING PERFORMANCE **********************
    '''
    #This is the training part
    evaluate_every = 500
    loss_every=500
    batch_size = 20
    N_way = 200 #The entire training set is used as support set : 100 occupied + 100 unoccupied 

    for i in range(900000):
        (inputs,targets)=loader.get_batch(batch_size)
        loss=sm.siamese_net.train_on_batch(inputs,targets)
        if i % evaluate_every == 0:
            v_acc, o_acc = loader.test_oneshot_ability(sm.siamese_net,N_way)

            print("Network loss ",loss)

            fname = 'training_prog.csv'
            file1 = open(fname, 'a')
            writer = csv.writer(file1)
            fields1=[v_acc,o_acc,loss]
            writer.writerow(fields1)
            file1.close()

            sm.siamese_net.save('weights/model_weight'+repr(pooling_param))

        if i % loss_every == 0:
            print("iteration {}, training loss: {:.2f},".format(i,loss))
if __name__ == '__main__':
    main()