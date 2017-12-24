import tensorflow as tf
import numpy as np
#构建x
x_data = np.linspace(-1,1,300)[:,None]
#构建噪声
noise = np.random.normal(0,0.05,x_data.shape)
#构建y
y_data = np.square(x_data) - 0.5 + noise
#输入输出占位符
xs = tf.placeholder(tf.float32,[None,1])
ys = tf.placeholder(tf.float32,[None,1])
def add_layer(inputs,in_size,out_size,activation_function=None):
    '''
    #构建隐藏层和输出层
    :param inputs: 输入数据
    :param in_size: 输入数据维度
    :param out_size: 输出数据维度
    :param activation_function: 激活函数
    :return: 输出数据
    '''
    #构建权重
    weight = tf.Variable(tf.random_normal([in_size,out_size]))
    #构建偏置
    biases = tf.Variable(tf.zeros([1,out_size])+0.1)
    #输出
    wx_plus_b = tf.matmul(inputs,weight) + biases
    if activation_function is None:
        outputs = wx_plus_b
    else:
        outputs = activation_function(wx_plus_b)
    return outputs
#添加隐藏层
h1 = add_layer(xs,1,20,activation_function=tf.nn.relu)
#添加输出层
prediction = add_layer(h1,20,1,activation_function=None)
#计算预测值和真实值的误差
loss = tf.reduce_mean(tf.reduce_sum(tf.square(ys - prediction),reduction_indices=[1]))
train_step = tf.train.GradientDescentOptimizer(0.1).minimize(loss)
#初始化变量
init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)
for i in range(1000):
    sess.run(train_step,feed_dict={xs:x_data,ys:y_data})
    if i % 50:
        print(sess.run(loss,feed_dict={xs:x_data,ys:y_data}))