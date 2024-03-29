"""
Copyright (c) 2015, Hui Xu (huixucs@gmail.com)
All rights reserved.
Need logistic_sgd.py and mlp.py in https://github.com/lisa-lab/DeepLearningTutorials 

This Modified code is for testing arbitrary amount of test images based on trained LeNet
Model.

Right Now it is the simplest version.

References:

1.http://deeplearning.net/tutorial/lenet.html
2.http://automl.chalearn.org/general-mnist---cnn-example

This tutorial introduces the LeNet5 neural network architecture
using Theano.  LeNet5 is a convolutional neural network, good for
classifying images. This tutorial shows how to build the architecture,
and comes with all the hyper-parameters you need to reproduce the
paper's MNIST results.


This implementation simplifies the model in the following ways:

 - LeNetConvPool doesn't implement location-specific gain and bias parameters
 - LeNetConvPool doesn't implement pooling by average, it implements pooling
   by max.
 - Digit classification is implemented with a logistic regression rather than
   an RBF network
 - LeNet5 was not fully-connected convolutions at second layer

References:
 - Y. LeCun, L. Bottou, Y. Bengio and P. Haffner:
   Gradient-Based Learning Applied to Document
   Recognition, Proceedings of the IEEE, 86(11):2278-2324, November 1998.
   http://yann.lecun.com/exdb/publis/pdf/lecun-98.pdf

"""
import os
import sys
import timeit

import numpy

import cPickle

import theano
import theano.tensor as T
from theano.tensor.signal import downsample
from theano.tensor.nnet import conv

#from logistic_sgd import LogisticRegression, load_data
from logistic_sgd import LogisticRegression
from mlp import HiddenLayer


class LeNetConvPoolLayer(object):
    """Pool Layer of a convolutional network """

    def __init__(self, rng, input, filter_shape, image_shape, poolsize=(2, 2)):
        """
        Allocate a LeNetConvPoolLayer with shared variable internal parameters.

        :type rng: numpy.random.RandomState
        :param rng: a random number generator used to initialize weights

        :type input: theano.tensor.dtensor4
        :param input: symbolic image tensor, of shape image_shape

        :type filter_shape: tuple or list of length 4
        :param filter_shape: (number of filters, num input feature maps,
                              filter height, filter width)

        :type image_shape: tuple or list of length 4
        :param image_shape: (batch size, num input feature maps,
                             image height, image width)

        :type poolsize: tuple or list of length 2
        :param poolsize: the downsampling (pooling) factor (#rows, #cols)
        """

        assert image_shape[1] == filter_shape[1]
        self.input = input

        # there are "num input feature maps * filter height * filter width"
        # inputs to each hidden unit
        fan_in = numpy.prod(filter_shape[1:])
        # each unit in the lower layer receives a gradient from:
        # "num output feature maps * filter height * filter width" /
        #   pooling size
        fan_out = (filter_shape[0] * numpy.prod(filter_shape[2:]) /
                   numpy.prod(poolsize))
        # initialize weights with random weights
        W_bound = numpy.sqrt(6. / (fan_in + fan_out))
        self.W = theano.shared(
            numpy.asarray(
                rng.uniform(low=-W_bound, high=W_bound, size=filter_shape),
                dtype=theano.config.floatX
            ),
            borrow=True
        )

        # the bias is a 1D tensor -- one bias per output feature map
        b_values = numpy.zeros((filter_shape[0],), dtype=theano.config.floatX)
        self.b = theano.shared(value=b_values, borrow=True)

        # convolve input feature maps with filters
        conv_out = conv.conv2d(
            input=input,
            filters=self.W,
            filter_shape=filter_shape,
            image_shape=image_shape
        )

        # downsample each feature map individually, using maxpooling
        pooled_out = downsample.max_pool_2d(
            input=conv_out,
            ds=poolsize,
            ignore_border=True
        )

        # add the bias term. Since the bias is a vector (1D array), we first
        # reshape it to a tensor of shape (1, n_filters, 1, 1). Each bias will
        # thus be broadcasted across mini-batches and feature map
        # width & height
        self.output = T.tanh(pooled_out + self.b.dimshuffle('x', 0, 'x', 'x'))

        # store parameters of this layer
        self.params = [self.W, self.b]

        # keep track of model input
        self.input = input
class LeNet(object):
    """LeNet or Convolutional Neural Networks

    """
    # return (self.layer0.W, self.layer0.b,...,self.laryer3.W,self.layer3.b)
    def __getstate__(self):
        weights = [p.get_value() for p in self.params]
        return weights
    def __setstate__(self, weights):
        i = iter(weights)
        for p in self.params:
            p.set_value(i.next())

    def __init__(self, rng, input, batch_size, nkerns):
        ######################
        # BUILD ACTUAL MODEL #
        ######################
        print '... building/testing the model'

        # Reshape matrix of rasterized images of shape (batch_size, 28 * 28)
        # to a 4D tensor, compatible with our LeNetConvPoolLayer
        # (28, 28) is the size of MNIST images.
        layer0_input = input.reshape((batch_size, 1, 28, 28))

        # Construct the first convolutional pooling layer:
        # filtering reduces the image size to (28-5+1 , 28-5+1) = (24, 24)
        # maxpooling reduces this further to (24/2, 24/2) = (12, 12)
        # 4D output tensor is thus of shape (batch_size, nkerns[0], 12, 12)
        self.layer0 = LeNetConvPoolLayer(
            rng,
            input=layer0_input,
            image_shape=(batch_size, 1, 28, 28),
            filter_shape=(nkerns[0], 1, 5, 5),
            poolsize=(2, 2)
        )

        # Construct the second convolutional pooling layer
        # filtering reduces the image size to (12-5+1, 12-5+1) = (8, 8)
        # maxpooling reduces this further to (8/2, 8/2) = (4, 4)
        # 4D output tensor is thus of shape (batch_size, nkerns[1], 4, 4)
        self.layer1 = LeNetConvPoolLayer(
            rng,
            input=self.layer0.output,
            image_shape=(batch_size, nkerns[0], 12, 12),
            filter_shape=(nkerns[1], nkerns[0], 5, 5),
            poolsize=(2, 2)
        )

        # the HiddenLayer being fully-connected, it operates on 2D matrices of
        # shape (batch_size, num_pixels) (i.e matrix of rasterized images).
        # This will generate a matrix of shape (batch_size, nkerns[1] * 4 * 4),
        # or (500, 50 * 4 * 4) = (500, 800) with the default values.
        layer2_input = self.layer1.output.flatten(2)

        # construct a fully-connected sigmoidal layer
        self.layer2 = HiddenLayer(
            rng,
            input=layer2_input,
            n_in=nkerns[1] * 4 * 4,
            n_out=500,
            activation=T.tanh
        )

        # classify the values of the fully-connected sigmoidal layer
        self.layer3 = LogisticRegression(input=self.layer2.output, n_in=500, n_out=10)

        # the cost we minimize during training is the NLL of the model
        #self.cost = self.layer3.negative_log_likelihood(y)

        self.errors = self.layer3.errors
        # create a list of all model parameters to be fit by gradient descent
        self.params= self.layer3.params + self.layer2.params + self.layer1.params + self.layer0.params
        # create a list of gradients for all model parameters
        #self.grads = T.grad(self.cost, self.params)


def shared_dataset(data_xy, borrow=True):
    """ Function that loads the dataset into shared variables

    The reason we store our dataset in shared variables is to allow
    Theano to copy it into the GPU memory (when code is run on GPU).
    Since copying data into the GPU is slow, copying a minibatch everytime
    is needed (the default behaviour if the data is not in a shared
    variable) would lead to a large decrease in performance.
    """
    data_x, data_y = data_xy
    shared_x = theano.shared(numpy.asarray(data_x,
                                           dtype=theano.config.floatX),
                             borrow=borrow)
    shared_y = theano.shared(numpy.asarray(data_y,
                                           dtype=theano.config.floatX),
                             borrow=borrow)
    # When storing data on the GPU it has to be stored as floats
    # therefore we will store the labels as ``floatX`` as well
    # (``shared_y`` does exactly that). But during our computations
    # we need them as ints (we use labels as index, and if they are
    # floats it doesn't make sense) therefore instead of returning
    # ``shared_y`` we will have to cast it to int. This little hack
    # lets ous get around this issue
    return shared_x, T.cast(shared_y, 'int32')

def load_data(dataset):
    ''' Loads the dataset

    :type dataset: string
    :param dataset: the path to the dataset (here MNIST)
    '''

    #############
    # LOAD DATA #
    #############

    # Download the MNIST dataset if it is not present
    data_dir, data_file = os.path.split(dataset)
    if data_dir == "" and not os.path.isfile(dataset):
        # Check if dataset is in the data directory.
        new_path = os.path.join(
            os.path.split(__file__)[0],
            "..",
            "data",
            dataset
        )
        if os.path.isfile(new_path) or data_file == 'mnist.pkl.gz':
            dataset = new_path

    if (not os.path.isfile(dataset)) and data_file == 'mnist.pkl.gz':
        import urllib
        origin = (
            'http://www.iro.umontreal.ca/~lisa/deep/data/mnist/mnist.pkl.gz'
        )
        print 'Downloading data from %s' % origin
        urllib.urlretrieve(origin, dataset)

    print '... loading data'

    # Load the dataset
    #f = gzip.open(dataset, 'rb')
    f = open(dataset, 'rb')
    #train_set, valid_set, test_set = cPickle.load(f)
    train_set, valid_set = cPickle.load(f)
    f.close()
    #train_set, valid_set, test_set format: tuple(input, target)
    #input is an numpy.ndarray of 2 dimensions (a matrix)
    #witch row's correspond to an example. target is a
    #numpy.ndarray of 1 dimensions (vector)) that have the same length as
    #the number of rows in the input. It should give the target
    #target to the example with the same index in the input.


    #test_set_x, test_set_y = shared_dataset(test_set)
    valid_set_x, valid_set_y = shared_dataset(valid_set)
    train_set_x, train_set_y = shared_dataset(train_set)

    rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y)]
    #        ,(test_set_x, test_set_y)]
    return rval

def fit_predict(train_set_x, train_set_y,valid_set_x, valid_set_y
                , action, filename,
                test_set_x=[], test_set_y=[]
                ,learning_rate=0.1, n_epochs=200, nkerns=[20,50]
                , train_batch_size=500, test_batch_size=17, seed=23455):
    rng = numpy.random.RandomState(seed)
    # allocate symbolic variables for the data
    index = T.lscalar()  # index to a [mini]batch

    # start-snippet-1
    x = T.matrix('x')   # the data is presented as rasterized images
    y = T.ivector('y')  # the labels are presented as 1D vector of
                        # [int] labels
    if action=='fit':
        n_train_batches = train_set_x.get_value(borrow=True).shape[0]
        n_valid_batches = valid_set_x.get_value(borrow=True).shape[0]
        n_train_batches /= train_batch_size
        n_valid_batches /= train_batch_size

        ######################
        # BUILD ACTUAL MODEL #
        ######################
        print '... building the model'

        classifier = LeNet(
            rng=rng,
            input = x,
            batch_size=train_batch_size,
            nkerns=nkerns
        )
        # create a function to compute the mistakes that are made by the model
        validate_model = theano.function(
            [index],
            classifier.errors(y),
            givens={
                x: valid_set_x[index * train_batch_size: (index + 1) * train_batch_size],
                y: valid_set_y[index * train_batch_size: (index + 1) * train_batch_size]
            }
        )

        # the cost we minimize during training is the NLL of the model
        cost = classifier.layer3.negative_log_likelihood(y)

        # create a list of gradients for all model parameters
        grads = T.grad(cost, classifier.params)

        # train_model is a function that updates the model parameters by
        # SGD Since this model has many parameters, it would be tedious to
        # manually create an update rule for each model parameter. We thus
        # create the updates list by automatically looping over all
        # (params[i], grads[i]) pairs.
        updates = [
            (param_i, param_i - learning_rate * grad_i)
            for param_i, grad_i in zip(classifier.params,grads)
        ]

        train_model = theano.function(
            inputs=[index],
            outputs=cost,
            updates=updates,
            givens={
                x: train_set_x[index * train_batch_size: (index + 1) * train_batch_size],
                y: train_set_y[index * train_batch_size: (index + 1) * train_batch_size]
            }
        )
        ###############
        # TRAIN MODEL #
        ###############
        print '... training'
        # early-stopping parameters
        patience = 10000  # look as this many examples regardless
        patience_increase = 2  # wait this much longer when a new best is
                               # found
        improvement_threshold = 0.995  # a relative improvement of this much is
                                       # considered significant
        validation_frequency = min(n_train_batches, patience / 2)
                                      # go through this many
                                      # minibatche before checking the network
                                      # on the validation set; in this case we
                                      # check every epoch

        best_validation_loss = numpy.inf
        best_iter = 0
        start_time = timeit.default_timer()

        epoch = 0
        done_looping = False


        while (epoch < n_epochs) and (not done_looping):
            epoch = epoch + 1
            for minibatch_index in xrange(n_train_batches):

                iter = (epoch - 1) * n_train_batches + minibatch_index

                if iter % 100 == 0:
                    print 'training @ iter = ', iter
                cost_ij = train_model(minibatch_index)

                if (iter + 1) % validation_frequency == 0:

                    # compute zero-one loss on validation set
                    validation_losses = [validate_model(i) for i
                                         in xrange(n_valid_batches)]
                    this_validation_loss = numpy.mean(validation_losses)
                    print('epoch %i, minibatch %i/%i, validation error %f %%' %
                          (epoch, minibatch_index + 1, n_train_batches,
                           this_validation_loss * 100.))

                    # if we got the best validation score until now
                    if this_validation_loss < best_validation_loss:

                        #improve patience if loss improvement is good enough
                        if this_validation_loss < best_validation_loss *  \
                           improvement_threshold:
                            patience = max(patience, iter * patience_increase)

                        # save best validation score and iteration number
                        best_validation_loss = this_validation_loss
                        best_iter = iter

                if patience <= iter:
                    done_looping = True
                    break

        #save and load
        f=file(filename, 'wb')
        cPickle.dump(classifier.__getstate__(),f,protocol=cPickle.HIGHEST_PROTOCOL)
        f.close()

        end_time = timeit.default_timer()
        #print >> sys.stderr,('The training ran for %.2fm' % ((end_time-start_time)/60.))
        print('Optimization complete.')
        print('Best validation score of %f %% obtained at iteration %i, ' %
              (best_validation_loss * 100., best_iter + 1))
        print >> sys.stderr, ('The code for file ' +
                              os.path.split(__file__)[1] +
                              ' ran for %.2fm' % ((end_time - start_time) / 60.))
    if action == 'predict':
        classifier_2 = LeNet(
            rng =rng,
            input=x,
            batch_size=test_batch_size,
            nkerns=nkerns
        )
        print "load model weight..."

        f=file(filename,'rb')
        classifier_2.__setstate__(cPickle.load(f))
        f.close()
        n_test_batches = test_set_x.get_value(borrow=True).shape[0]
        n_test_batches /= test_batch_size

        if n_test_batches != 1:
            test_model = theano.function(
                [index],
                outputs=(classifier_2.layer3.errors(y),classifier_2.layer3.y_pred,y),#output
                givens={
                    x: test_set_x[index * test_batch_size: (index + 1) * test_batch_size],
                    y: test_set_y[index * test_batch_size: (index + 1) * test_batch_size]
                }, on_unused_input='warn'
            )
            (test_losses,test_y_predicted,test_y) = [
                test_model(i)
                for i in xrange(n_test_batches)
            ]
        else:
            test_model = theano.function(
                [],
                outputs=(classifier_2.layer3.errors(y),classifier_2.layer3.y_pred,y),#output
                #outputs=classifier_2.layer3.y_pred,
                givens={
                    x: test_set_x,
                    y: test_set_y
                }, on_unused_input='ignore'
            )
            (test_losses,test_y_predicted,test_y) = test_model()
        RET =[]

        test_score = numpy.mean(test_losses)
        RET.append((test_losses,test_y_predicted,test_y))
        f=open("../data/testOutcome.txt","w+")
        f.write('losses \t predict labels \t real labels\n')
        for test_out_item in RET:
            f.write(str(test_out_item[0])+'\t'+str(test_out_item[1])+'\t'+str(test_out_item[2])+'\t'+'\n')
        f.close()

        print('test performance %f, see ../data/testOutcome.txt for vivid results' %
              (test_score * 100.))
        print "finish predicting."
        #return RET

def fit(filename='weights.pkl'):
    datasets = load_data('../data/ForTrainedModel.pkl')

    train_set_x, train_set_y = datasets[0]
    valid_set_x, valid_set_y = datasets[1]
    fit_predict(train_set_x, train_set_y,valid_set_x,valid_set_y,
                    filename=filename, action='fit')
def predict(filename='weights.pkl'):
    f = open('../data/TestSet.pkl', 'rb')
    #train_set, valid_set, test_set = cPickle.load(f)
    test_set = cPickle.load(f)
    f.close()
    test_set_x, test_set_y = shared_dataset(test_set)
    fit_predict(train_set_x=[],train_set_y=[],valid_set_x=[],valid_set_y=[],filename=filename
                       ,test_set_x=test_set_x, test_set_y=test_set_y,action='predict')


if __name__ == '__main__':
    fit()
    predict()
