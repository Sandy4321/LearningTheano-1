# LearningTheano
Modified https://github.com/lisa-lab/DeepLearningTutorials version for real project use.

## LeNet model for testing arbitrary amount of testing data

Codes are in "LeNet" directory.

Tested Environment: RAM 32GB, GPU GTX 970

Status of the code: under modifying.

### Additional documents (in Chinese)

https://www.zybuluo.com/water/note/202946


### **Running Steps**

All the data sets should be organized in a giant direcotory, which contains 10 sub-directories, every sub-directory is named according to each real classes label(integer), e.g. 0, 1, 2, ... . In each sub-directory, there are images that belong to specific class, e.g. 0_17.jpg.



The preprocessing steps assum that all the images are gray, which means every pixal is between [0,255].

>$ python imagestopkl.py

>// to generate train(90%) and validation(10%) set. 会提示输入图像数据到路径。图像数据在服务器/home/xuhui/DeeplearningTutorial/data/tk10-images 

>$ python imagestopklFTest.py

>// to generate test set

>$(THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python convolutional_mlp.py > test.txt&
