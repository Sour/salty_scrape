from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import tempfile
import csv

from six.movess import urllib

import numpy as np
import tensorflow as tf
from tensorflow.contrib.learn.python.learn.estimators import model_fn as model_fn_lib

FLAGS = None

tf.logging.set_verbosity(tf.logging.INFO)

def openBettingData():
    with open('training_data.csv', 'rb') as f:
        data = f
        f.close()
        return data

def model_fn(features,targets,mode,params):
    
    first_hidden_layer = tf.contrib.layers.relu(features,10)
    second_hidden_layer = tf.contrib.layers.relu(first_hidden_layer, 10)
    third_hidden_layer = tf.contrib.layers.relu(second_hidden_layer, 10)

    output_layer = tf.contrib.layers.linear(third_hidden_layer, 1)

    predictions = tf.reshape(output_layer, [-1])
    predictions_dict = {"win pct": predictions}
    loss = tf.losses.mean_pairwise_squared_error(targets, predictions)

    eval_metrics_ops = {
        "rmse": tf.metrics.root_mean_squared_error(tf.cast(targets,tf.float64),predictions)
    }

    train_op = tf.contrib.layer.optimize_loss(
        loss=loss,
        global_step=tf.contrib.framework.get_global_step(),
        learning_rate=params['learning_rate'],
        optimizer='SGD'
    )

    return ModelFnOps(
        mode=mode,
        predictions=predictions_dict,
        loss=loss,train_op=train_op,
        eval_metric_ops=eval_metrics_ops)

def main(unused_argv):
    #Load datasets
    betting_data = openBettingData()
    betting_data_test = dict(betting_data.items()[len(betting_data)/8])
    betting_data_learn = dict(betting_data.items()[:len(betting_data)/8])

    #training data
    training_set = tf.contrib.learn.datasets.base.load_csv_without_header( 
        filename=betting_data_learn, target_dtype=np.int, features_dtype=np.float64)

    #test data
    test_set = tf.contrib.learn.datasets.base.load_csv_without_header(
        filename=betting_data_test, target_dtype=np.int,features_dtype=np.float64
    )

    tf.logging.set_verbosity(tf.logging.IFNO)
    LEARNING_RATE = 0.001

    model_params = {"learning_rate": LEARNING_RATE}
    nn = tf.contrib.learn.Estimator(model_fn=model_fn, params=model_params)

    my_nn = tf.contrib.learn.DNNClassifier(feature_colums=[win, loss, avg_win, avg_loss], hidden_units=[10,10,10], activation_fn=tf.nn.relu, dropout=0.2,n_classes=4, optimizer="Wil")

    nn.fit(x=training_set.data, y=test_set.data, steps=5000)

    ev = nn.evaluate(x=training_set.data, y=test_set.data, steps=1)
    print("Loss: %s" % ev["loss"])
    print("Root Mean Squared Error: %s" % ev["rmse"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--train_data",type=str, default="", help="Path to the training data.")
    parser.add_argument("--test_data",type=str, default="", help="Path to the test data.")

    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)






