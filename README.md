# LearningTheano
Modified https://github.com/lisa-lab/DeepLearningTutorials version for real project use.

## LeNet model for testing arbitrary amount of testing data/n

Codes are in "LeNet" directory./n

Tested Environment: RAM 32GB, GPU GTX 970/n

Status of the code: under modifying./n

**Running Steps**/n

$ python imagestopkl.py/n

$ python imagestopklFTest.py

$(THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python convolutional_mlp.py > test.txt&)
