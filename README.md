# LearningTheano
Modified https://github.com/lisa-lab/DeepLearningTutorials version for real project use.

## LeNet model for testing arbitrary amount of testing data
Codes are in "LeNet" directory.
Tested Environment: RAM 32GB, GPU GTX 970
Status of the code: under modifying.

**Running Steps**
$ python imagestopkl.py

$ python imagestopklFTest.py

$(THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python convolutional_mlp.py > test.txt&)
