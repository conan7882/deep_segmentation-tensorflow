# File: VGG.py
# Author: Qian Ge <geqian1001@gmail.com>

import argparse

import numpy as np
import tensorflow as tf

from tensorcv.dataflow.matlab import MatlabData
from tensorcv.models.layers import *
from tensorcv.models.base import BaseModel
from tensorcv.utils.common import apply_mask, get_tensors_by_names
from tensorcv.train.config import TrainConfig
from tensorcv.predicts.config import PridectConfig
from tensorcv.train.simple import SimpleFeedTrainer
from tensorcv.callbacks.saver import ModelSaver
from tensorcv.callbacks.summary import TrainSummary
from tensorcv.callbacks.inference import FeedInference
from tensorcv.callbacks.monitors import TFSummaryWriter
from tensorcv.callbacks.inferencer import InferScalars
from tensorcv.predicts.simple import SimpleFeedPredictor
from tensorcv.predicts.predictions import PredictionImage
from tensorcv.callbacks.debug import CheckScalar

import config

VGG_MEAN = [103.939, 116.779, 123.68]

class Model(BaseModel):
    def __init__(self, num_class = 1000, 
                 num_channels = 3, 
                 im_height = 224, im_width = 224,
                 learning_rate = 0.0001):

        self.learning_rate = learning_rate
        self.num_channels = num_channels
        self.im_height = im_height
        self.im_width = im_width
        self.num_class = num_class

        self.set_is_training(True)

    def _create_input(self):
        self.keep_prob = tf.placeholder(tf.float32, name='keep_prob')
        self.image = tf.placeholder(tf.float32, name = 'image',
                            shape = [None, self.im_height, self.im_width, self.num_channels])
        self.label = tf.placeholder(tf.int64, [None, self.num_class], 'label')

    def _get_placeholder(self):
        return [self.image, self.label]
        # image, label 

    def _get_prediction_placeholder(self):
        return self.image

    def _get_graph_feed(self):
        if self.is_training:
            feed = {self.keep_prob: 0.5}
        else:
            feed = {self.keep_prob: 1}
        return feed

    def _create_model(self):

    
        with tf.variable_scope('conv1') as scope:
            conv1_1 = conv(self.image, 3, 64, 'conv1_1', nl = tf.nn.relu)
            conv1_2 = conv(conv1_1, 3, 64, 'conv1_2', nl = tf.nn.relu)
            pool1 = max_pool(conv1_2, padding = 'SAME')

        with tf.variable_scope('conv2') as scope: 
            conv2_1 = conv(pool1, 3, 128, 'conv2_1', nl = tf.nn.relu)
            conv2_2 = conv(conv2_1, 3, 128, 'conv2_2', nl = tf.nn.relu)
            pool2 = max_pool(conv2_2, padding = 'SAME')

        with tf.variable_scope('conv3') as scope:  
            conv3_1 = conv(pool2, 3, 256, 'conv3_1', nl = tf.nn.relu)
            conv3_2 = conv(conv3_1, 3, 256, 'conv3_2', nl = tf.nn.relu)
            conv3_3 = conv(conv3_2, 3, 256, 'conv3_3', nl = tf.nn.relu)
            conv3_4 = conv(conv3_3, 3, 256, 'conv3_4', nl = tf.nn.relu)
            pool3 = max_pool(conv3_4, padding = 'SAME')

        with tf.variable_scope('conv4') as scope: 
            conv4_1 = conv(pool3, 3, 512, 'conv4_1', nl = tf.nn.relu)
            conv4_2 = conv(conv4_1, 3, 512, 'conv4_2', nl = tf.nn.relu)
            conv4_3 = conv(conv4_2, 3, 512, 'conv4_3', nl = tf.nn.relu)
            conv4_4 = conv(conv4_3, 3, 512, 'conv4_4', nl = tf.nn.relu)
            pool4 = max_pool(conv4_4, padding = 'SAME')

        with tf.variable_scope('conv5') as scope: 
            conv5_1 = conv(pool4, 3, 512, 'conv5_1', nl = tf.nn.relu)
            conv5_2 = conv(conv5_1, 3, 512, 'conv5_2', nl = tf.nn.relu)
            conv5_3 = conv(conv5_2, 3, 512, 'conv5_3', nl = tf.nn.relu)
            conv5_4 = conv(conv5_3, 3, 512, 'conv5_4', nl = tf.nn.relu)
            pool5 = max_pool(conv5_4, padding = 'SAME')

        with tf.variable_scope('fc6') as scope: 
            fc6 = fc(pool5, 4096, nl = tf.nn.relu)
            dropout_fc6 = dropout(fc6, self.keep_prob, self.is_training)

        with tf.variable_scope('fc7') as scope: 
            fc7 = fc(dropout_fc6, 4096, nl = tf.nn.relu)
            dropout_fc7 = dropout(fc7, self.keep_prob, self.is_training)

        with tf.variable_scope('fc8') as scope: 
            fc8 = fc(dropout_fc7, 1000)

        with tf.name_scope('prediction'):
            self.prediction_pro = tf.nn.softmax(fc8, name='pre_prob')
            self.prediction = tf.argmax(fc8, name='pre_label', dimension = -1)

    def _get_loss(self):
        with tf.name_scope('loss'):
            # return tf.reduce_sum((self.prediction_pro - self.label)**2)
            return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits
                    (logits = self.prediction_pro, labels = self.label), 
                    name = 'result') 

    def _get_optimizer(self):
        return tf.train.GradientDescentOptimizer(learning_rate = self.learning_rate)
            
    def _ex_setup_graph(self):
        with tf.name_scope('accuracy'):
            correct_prediction = tf.equal(self.prediction, self.label)
            self.accuracy = tf.reduce_mean(
                        tf.cast(correct_prediction, tf.float32), 
                        name = 'result')

         
#     def _setup_summary(self):
#         with tf.name_scope('train_summary'):
#             tf.summary.image("train_Predict",
#                     tf.expand_dims(tf.cast(self.prediction, tf.float32), -1), 
#                     collections = ['train'])
#             tf.summary.image("im",tf.cast(self.image, tf.float32),
#                              collections = ['train'])
#             tf.summary.image("gt", 
#                        tf.expand_dims(tf.cast(self.gt, tf.float32), -1), 
#                        collections = ['train'])
#             tf.summary.image("mask", 
#                        tf.expand_dims(tf.cast(self.mask, tf.float32), -1),
#                        collections = ['train'])
#             tf.summary.scalar('train_accuracy', self.accuracy, 
#                               collections = ['train'])
#         with tf.name_scope('test_summary'):
#             tf.summary.image("test_Predict", 
#                       tf.expand_dims(tf.cast(self.prediction, tf.float32), -1),
#                       collections = ['test'])

# def get_config(FLAGS):
#     mat_name_list = ['level1Edge', 'GT', 'Mask']
#     dataset_train = MatlabData('train', mat_name_list = mat_name_list,
#                                data_dir = FLAGS.data_dir)
#     dataset_val = MatlabData('val', mat_name_list = mat_name_list, 
#                              data_dir = FLAGS.data_dir)
#     inference_list = [InferScalars('accuracy/result', 'test_accuracy')]
    
#     return TrainConfig(
#                  dataflow = dataset_train, 
#                  model = Model(num_channels = FLAGS.input_channel, 
#                                num_class = FLAGS.num_class, 
#                                learning_rate = 0.0001),
#                  monitors = TFSummaryWriter(summary_dir = FLAGS.summary_dir),
#                  callbacks = [
#                     ModelSaver(periodic = 10,
#                                checkpoint_dir = FLAGS.summary_dir),
#                     TrainSummary(key = 'train', periodic = 10),
#                     FeedInference(dataset_val, periodic = 10, 
#                                   extra_cbs = TrainSummary(key = 'test'),
#                                   inferencers = inference_list),
#                               # CheckScalar(['accuracy/result'], periodic = 10),
#                   ],
#                  batch_size = FLAGS.batch_size, 
#                  max_epoch = 200,
#                  summary_periodic = 10)

# def get_predictConfig(FLAGS):
#     mat_name_list = ['level1Edge']
#     dataset_test = MatlabData('Level_1', shuffle = False,
#                                mat_name_list = mat_name_list,
#                                data_dir = FLAGS.test_data_dir)
#     prediction_list = PredictionImage(['prediction/label', 'prediction/probability'], 
#                                       ['test','test_pro'], 
#                                       merge_im = True)

#     return PridectConfig(
#                 dataflow = dataset_test,
#                 model = Model(FLAGS.input_channel, 
#                                 num_class = FLAGS.num_class),
#                 model_name = 'model-14070',
#                 model_dir = FLAGS.model_dir,    
#                 result_dir = FLAGS.result_dir,
#                 predictions = prediction_list,
#                 batch_size = FLAGS.batch_size)

# def get_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--data_dir', 
#         help = 'Directory of input training data.',
#         default = 'D:\\GoogleDrive_Qian\\Foram\\Training\\CNN_Image\\')
#     parser.add_argument('--summary_dir', 
#         help = 'Directory for saving summary.',
#         default = 'D:\\Qian\\GitHub\\workspace\\test\\')
#     parser.add_argument('--checkpoint_dir', 
#         help = 'Directory for saving checkpoint.',
#         default = 'D:\\Qian\\GitHub\\workspace\\test\\')

#     parser.add_argument('--test_data_dir', 
#         help = 'Directory of input test data.',
#         default = 'D:\\GoogleDrive_Qian\\Foram\\testing\\')
#     parser.add_argument('--model_dir', 
#         help = 'Directory for restoring checkpoint.',
#         default = 'D:\\Qian\\GitHub\\workspace\\test\\')
#     parser.add_argument('--result_dir', 
#         help = 'Directory for saving prediction results.',
#         default = 'D:\\Qian\\GitHub\\workspace\\test\\2\\')

#     parser.add_argument('--input_channel', default = 1, 
#                         help = 'Number of image channels')
#     parser.add_argument('--num_class', default = 2, 
#                         help = 'Number of classes')
#     parser.add_argument('--batch_size', default = 1)

#     parser.add_argument('--predict', help = 'Run prediction', action='store_true')
#     parser.add_argument('--train', help = 'Train the model', action='store_true')

#     return parser.parse_args()

if __name__ == '__main__':
    VGG = Model(num_class = 1000, learning_rate = 0.0001,
                num_channels = 3, im_height = 224, im_width = 224)
    VGG.create_graph()
    VGG.get_grads()
    VGG.get_optimizer()

    writer = tf.summary.FileWriter(config.summary_dir)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        writer.add_graph(sess.graph)

    writer.close()

    # FLAGS = get_args()
    # if FLAGS.train:
    #     config = get_config(FLAGS)
    #     SimpleFeedTrainer(config).train()
    # elif FLAGS.predict:
    #     config = get_predictConfig(FLAGS)
    #     SimpleFeedPredictor(config).run_predict()


 