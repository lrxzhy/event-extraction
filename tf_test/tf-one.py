#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Time        : 2017/9/28 下午2:20
# @Author      : Zoe
# @File        : tf-one.py
# @Description : tf test

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer


def test1():
    x_data = np.random.rand(100).astype(np.float32)
    y_data = x_data*0.1+0.3

    weights = tf.Variable(tf.random_uniform([1], -1.0, 1.0))
    biases = tf.Variable(tf.zeros([1]))

    y = weights*x_data+biases

    loss = tf.reduce_mean(tf.square(y-y_data))
    optimizer = tf.train.GradientDescentOptimizer(0.5)
    train = optimizer.minimize(loss)

    init = tf.global_variables_initializer()

    with tf.Session() as sess:
        sess.run(init)
        for step in range(201):
            sess.run(train)
            if step % 20 == 0:
                print(step, sess.run(weights), sess.run(biases))


def test2():
    m1 = tf.constant([[3, 3]])
    m2 = tf.constant([[2], [2]])
    product = tf.matmul(m1, m2)

    with tf.Session() as sess:
        print(sess.run(product))


def test3():
    state = tf.Variable(0, name='counter')
    # print(state.name)
    one = tf.constant(1)

    new_value = tf.add(state, one)
    update = tf.assign(state, new_value)

    init = tf.global_variables_initializer()

    with tf.Session() as sess:
        sess.run(init)
        for _ in range(3):
            sess.run(update)
            print(sess.run(state))


def test4():
    input1 = tf.placeholder(tf.float32)
    input2 = tf.placeholder(tf.float32)
    output = tf.multiply(input1, input2)
    with tf.Session() as sess:
        print(sess.run(output, feed_dict={input1: [7.], input2: [2.]}))


def add_layer(inputs, in_size, out_size, n_layer, activation_function=None):
    layer_name = 'layer%s' % n_layer
    with tf.name_scope(layer_name):
        with tf.name_scope('weights'):
            Weights = tf.Variable(tf.random_normal([in_size, out_size]), name='W')
            tf.summary.histogram(layer_name+'/weights', Weights)
        with tf.name_scope('biases'):
            biases = tf.Variable(tf.zeros([1, out_size])+0.1, name='b')
            tf.summary.histogram(layer_name + '/biases', biases)
        with tf.name_scope('Wx_plus_b'):
            Wx_plus_b = tf.matmul(inputs, Weights) + biases
        if activation_function is None:
            outputs = Wx_plus_b
        else:
            outputs = activation_function(Wx_plus_b)
            tf.summary.histogram(layer_name + '/outputs', outputs)
        return outputs


def test5():
    # 清空log目录
    os.remove('logs/' + [files[0] for root, dirs, files in os.walk('logs/')][0])

    x_data = np.linspace(-1, 1, 300)[:, np.newaxis]
    noise = np.random.normal(0, 0.05, x_data.shape)
    y_data = np.square(x_data)-0.5+noise

    with tf.name_scope('inputs'):
        xs = tf.placeholder(tf.float32, [None, 1], name='x_input')
        ys = tf.placeholder(tf.float32, [None, 1], name='y_input')

    l1 = add_layer(xs, 1, 10, n_layer=1, activation_function=tf.nn.relu)
    prediction = add_layer(l1, 10, 1, n_layer=2, activation_function=None)

    with tf.name_scope('loss'):
        loss = tf.reduce_mean(tf.reduce_sum(tf.square(ys - prediction), reduction_indices=[1]))
        tf.summary.scalar('loss', loss)
    with tf.name_scope('train'):
        train_step = tf.train.GradientDescentOptimizer(0.1).minimize(loss)

    init = tf.global_variables_initializer()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x_data, y_data)
    plt.ion()
    plt.show()
    with tf.Session() as sess:
        # 要写完整地址
        merged = tf.summary.merge_all()
        writer = tf.summary.FileWriter('logs/', sess.graph)
        sess.run(init)
        for i in range(1000):
            sess.run(train_step, feed_dict={xs: x_data, ys: y_data})
            if i % 50 == 0:
                result = sess.run(merged, feed_dict={xs: x_data, ys: y_data })
                writer.add_summary(result, i)
                # print(sess.run(loss, feed_dict={xs: x_data, ys: y_data}))
                try:
                    ax.lines.remove(lines[0])
                except Exception:
                    pass
                prediction_value = sess.run(prediction, feed_dict={xs: x_data, ys: y_data})
                lines = ax.plot(x_data, prediction_value, 'r-', lw=5)
                plt.pause(0.3)
        writer.close()

test5()

def test6():
    def compute_accuracy(v_xs, v_ys):
        global prediction
        y_pre = sess.run(prediction, feed_dict={xs: v_xs})
        correct_prediction = tf.equal(tf.argmax(y_pre, 1), tf.argmax(v_ys, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        result = sess.run(accuracy, feed_dict={xs: v_xs, ys: v_ys})
        return result

    mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
    xs = tf.placeholder(tf.float32, [None, 784])
    ys = tf.placeholder(tf.float32, [None, 10])

    prediction = add_layer(xs, 784, 10, n_layer=1, activation_function=tf.nn.softmax)
    cross_entropy = tf.reduce_mean(-tf.reduce_sum(ys*tf.log(prediction), reduction_indices=[1]))
    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(1000):
            batch_xs, batch_ys = mnist.train.next_batch(100)
            sess.run(train_step, feed_dict={xs: batch_xs, ys: batch_ys})
            if i%50 == 0:
                print(compute_accuracy(mnist.test.images, mnist.test.labels))


def test7():
    def add_layer(inputs, in_size, out_size, layer_name, activation_function=None):
        # add one more layer and return the output of this layer
        Weights = tf.Variable(tf.random_normal([in_size, out_size]))
        biases = tf.Variable(tf.zeros([1, out_size]) + 0.1, )
        Wx_plus_b = tf.matmul(inputs, Weights) + biases
        # here to dropout
        Wx_plus_b = tf.nn.dropout(Wx_plus_b, keep_prob)
        if activation_function is None:
            outputs = Wx_plus_b
        else:
            outputs = activation_function(Wx_plus_b, )
        tf.summary.histogram(layer_name + '/outputs', outputs)
        return outputs

    digits = load_digits()
    X = digits.data
    y = digits.target
    y = LabelBinarizer().fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3)

    keep_prob = tf.placeholder(tf.float32)
    xs = tf.placeholder(tf.float32, [None, 64])  # 8x8
    ys = tf.placeholder(tf.float32, [None, 10])

    # add output layer
    l1 = add_layer(xs, 64, 50, 'l1', activation_function=tf.nn.tanh)
    prediction = add_layer(l1, 50, 10, 'l2', activation_function=tf.nn.softmax)
    # loss
    cross_entropy = tf.reduce_mean(-tf.reduce_sum(ys * tf.log(prediction), reduction_indices=[1]))
    tf.summary.scalar('loss', cross_entropy)

    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

    with tf.Session() as sess:
        merged = tf.summary.merge_all()
        # summary writer goes in here
        train_writer = tf.summary.FileWriter("logs/train", sess.graph)
        test_writer = tf.summary.FileWriter("logs/test", sess.graph)

        sess.run(tf.global_variables_initializer())
        for i in range(1000):
            sess.run(train_step, feed_dict={xs: X_train, ys: y_train, keep_prob: 0.5})
            if i % 50 == 0:
                # record loss
                train_result = sess.run(merged, feed_dict={xs: X_train, ys: y_train, keep_prob: 1})
                test_result = sess.run(merged, feed_dict={xs: X_test, ys: y_test, keep_prob: 1})
                train_writer.add_summary(train_result, i)
                test_writer.add_summary(test_result, i)


def test8_saver():
    W = tf.Variable([[1, 2, 3], [3, 4, 5]], dtype=tf.float32, name='weights')
    b = tf.Variable([[1, 2, 3]], dtype=tf.float32, name='biases')

    init = tf.global_variables_initializer()
    saver = tf.train.Saver()
    with tf.Session() as sess:
        sess.run(init)
        save_path = saver.save(sess, 'my_net/save_net.ckpt')
        print("save to path:", save_path)


def test9_load():
    W = tf.Variable(np.arange(6).reshape((2, 3)), dtype=tf.float32, name='weights')
    b = tf.Variable(np.arange(3).reshape((1, 3)), dtype=tf.float32, name='biases')

    saver = tf.train.Saver()

    with tf.Session() as sess:
        saver.restore(sess, 'my_net/save_net.ckpt')
        print("weight:", sess.run(W))
        print("biases:", sess.run(b))


def test10_visualize():
    mnist = input_data.read_data_sets("MNIST_data", one_hot=False)

    trainimg = mnist.train.images
    trainlabel = mnist.train.labels
    testimg = mnist.test.images
    testlabel = mnist.test.labels

    print(testimg[0])
    print(testlabel[0])

    f, a = plt.subplots(1, 10, figsize=(5, 2))
    for i in range(10):
        a[i].imshow(np.reshape(mnist.test.images[i], (28, 28)))
    plt.show()


# test10_visualize()

def test11_npshape():
    a = np.arange(0,100).reshape(-1,5,5)
    print(a.shape)
    c = np.row_stack((a, np.arange(0,25).reshape(1,5,5)))
    print(c.shape)

    t = list()
    text_mat = np.zeros(shape=(2, 3))
    text_mat1 = np.ones(shape=(2, 3))
    t.append(text_mat)
    t.append(text_mat1)
    print(np.array(t).shape)
    y_tag = ['B_Movement', 'B_Justice', 'B_Transaction', 'B_Contact', 'B_Personnel', 'B_Business', 'B_Life', 'B_Conflict', 'O']
    print(y_tag.index('a'))

    y = np.zeros(shape=(32, 1))
    y[0] = y_tag.index('O')
    print(y)

