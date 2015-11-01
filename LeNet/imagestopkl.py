"""
Copyright (c) 2015, Hui Xu (huixucs@gmail.com)
All rights reserved.
Transform images into what Theano can recognize

Image restoration type:
Folder contains many subfolders, which names are class lables(integer, e.g. 0,1,2,...),
in each subfolders, there are multiple images belong to the subfolder class,
which named as classlable_number.jpg/png, e.g. 0_17.jpg

Theano data type:
a tuple of 3 lists : the training set, the validation set and the testing set. 
Each of the three lists is a pair formed from a list of images and a list of class labels 
for each of the images. An image is represented as numpy 1-dimensional array of 784 (28 x 28) 
float values between 0 and 1 (0 stands for black, 1 for white). 
The labels are numbers between 0 and 9 indicating which digit the image represents.

Process procedure:
1. Random distribute original images into three folders: train(90%), val(10%)
   In each of these folder, the organization way is the same as Image restoration type.
2. Generating Theano data type according to ascending order, for train and val respectively.

To do: Data set is too large to be processed, we should seperate the whole data set into mini-batches first   

"""
import os
import shutil
#import PIL
import cPickle
#from PIL import Image
import scipy
from scipy.misc import imread

import numpy
from numpy import ndarray

def RandomDistr(filefolder):
    if not os.path.exists('../data/train'):
        os.mkdir('../data/train')
    if not os.path.exists('../data/val'):
        os.mkdir('../data/val')
    #if not os.path.exists('../data/test'):
    #    os.mkdir('../data/test')
    folderlist=os.walk(filefolder)
    for subdir, subsubdir, files in folderlist:
       # print subdir
        if subdir != filefolder:
           # print subdir

            subdirbase=os.path.basename(subdir)
            os.mkdir('../data/train/'+subdirbase)
            os.mkdir('../data/val/'+subdirbase)
            #os.mkdir('../data/test/'+subdirbase)
            filesnum=len(files)
            trainnum=filesnum*9/10 #70% of each class
            valnum=filesnum*1/10 #10% of each class
            trainfilelist=files[0:trainnum-1]
            valfilelist=files[trainnum:]
            #valfilelist=files[trainnum:trainnum+valnum-1]
            #testfilelist=files[trainnum+valnum:]
            for trainfile in trainfilelist:
                shutil.copy(subdir+'/'+trainfile,'../data/train/'+subdirbase)
            for valfile in valfilelist:
                shutil.copy(subdir+'/'+valfile,'../data/val/'+subdirbase)
            #for testfile in testfilelist:
            #    shutil.copy(subdir+'/'+testfile,'../data/test/'+subdirbase)
    
    #rval = ['../data/train','../data/val' ,'../data/test' ]
    #return rval

#def Generate(train_img_dir,val_img_dir,test_img_dir):
def Generate(train_img_dir,val_img_dir):
    #print os.listdir(train_img_dir)
#"""
    train_set_x=[]
    train_set_y=[]
    val_set_x=[]
    val_set_y=[]
    #test_set_x=[]
    #test_set_y=[]
    for train_label, sub, train_imgs in os.walk(train_img_dir):
        if train_label!=train_img_dir:
            train_label=os.path.basename(train_label)
            for train_img in train_imgs:
                imgbody=imread(train_img_dir+'/'+train_label+'/'+train_img).flatten().astype(float)/255.#gray image vector
                imglabel=int(train_label)
                train_set_x.append(imgbody)
                train_set_y.append(imglabel)

    for val_label, sub, val_imgs in os.walk(val_img_dir):
        if val_label!=val_img_dir:
            val_label=os.path.basename(val_label)
            for val_img in val_imgs:
                imgbody=imread(val_img_dir+'/'+val_label+'/'+val_img).flatten().astype(float)/255.#gray image vector
                imglabel=int(val_label)
                val_set_x.append(imgbody)
                val_set_y.append(imglabel)
    """
    for test_label, sub, test_imgs in os.walk(test_img_dir):
        if test_label!=test_img_dir:
            test_label=os.path.basename(test_label)
            for test_img in test_imgs:
                imgbody=imread(test_img_dir+'/'+test_label+'/'+test_img).flatten().astype(float)/255.#gray image vector
                imglabel=int(test_label)
                test_set_x.append(imgbody)
                test_set_y.append(imglabel)
    """
    #rval=[(train_set_x,train_set_y),(val_set_x,val_set_y),(test_set_x,test_set_y)]
    rval=[(train_set_x,train_set_y),(val_set_x,val_set_y)]
    #output=open('../data/data/testMnist.pkl','wb')
    output=open('../data/ForTrainedModel.pkl','wb')
    cPickle.dump(rval,output)
    output.close()
    return rval
#"""
        

if __name__=="__main__":
    while 1:
        Folder=raw_input('Please input the folder to process:')
        if len(Folder) == 0:
            print  'Please input the folder to process:'
        else:
            break
    RandomDistr(Folder)
    distFolder=['../data/train','../data/val' ,'../data/test']

    train_img_dir = distFolder[0]
    val_img_dir = distFolder[1]
    #test_img_dir = distFolder[2]
    """
    sorted_train_dirs = sorted([name for name in os.listdir(train_img_dir)
                            if os.path.isdir(os.path.join(train_img_dir, name))])
    sorted_val_dirs = sorted([name for name in os.listdir(val_img_dir)
                            if os.path.isdir(os.path.join(val_img_dir, name))])
    sorted_test_dirs = sorted([name for name in os.listdir(test_img_dir)
                            if os.path.isdir(os.path.join(test_img_dir, name))])
    """
    #Generate(train_img_dir,val_img_dir,test_img_dir)
    Generate(train_img_dir,val_img_dir)
