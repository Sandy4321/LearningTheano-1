"""
Copyright (c) 2015, Hui Xu (huixucs@gmail.com)
All rights reserved.

Transform test images into what Theano can recognize

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


#def Generate(train_img_dir,val_img_dir,test_img_dir):
def Generate(test_img_dir):
    test_set_x=[]
    test_set_y=[]

    for test_label, sub, test_imgs in sorted(os.walk(test_img_dir)):# according to shunxu?
        if test_label!=test_img_dir:
            test_label=os.path.basename(test_label)
            for test_img in test_imgs:
                imgbody=imread(test_img_dir+'/'+test_label+'/'+test_img).flatten().astype(float)/255.#gray image vector
                imglabel=int(test_label)
                test_set_x.append(imgbody)
                test_set_y.append(imglabel)


    #rval=[(train_set_x,train_set_y),(val_set_x,val_set_y),(test_set_x,test_set_y)]
    rval=(test_set_x,test_set_y)
    output=open('../data/TestSet.pkl','wb')
    cPickle.dump(rval,output)
    output.close()
    f=open("../data/testSet.txt","w+")
    for test_y in test_set_y:
        f.write(str(test_y)+'\n')
    f.close()
    return rval
#"""
        

if __name__=="__main__":
    while 1:
        Folder=raw_input('Please input the folder to process:')
        if len(Folder) == 0:
            print  'Please input the folder to process:'
        else:
            break
    test_img_dir = Folder
    """
    sorted_train_dirs = sorted([name for name in os.listdir(train_img_dir)
                            if os.path.isdir(os.path.join(train_img_dir, name))])
    sorted_val_dirs = sorted([name for name in os.listdir(val_img_dir)
                            if os.path.isdir(os.path.join(val_img_dir, name))])
    sorted_test_dirs = sorted([name for name in os.listdir(test_img_dir)
                            if os.path.isdir(os.path.join(test_img_dir, name))])
    """
    #Generate(train_img_dir,val_img_dir,test_img_dir)
    Generate(test_img_dir)
    
   
