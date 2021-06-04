import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import conv as layers
import larq as lq

from tensorflow.keras.datasets import mnist

def show_data(train_images, train_labels, test_images, test_labels):

    print('MNIST Dataset Shape:')
    print('X_train: ' + str(train_images.shape))
    print('Y_train: ' + str(train_labels.shape))
    print('X_test:  '  + str(test_images.shape))
    print('Y_test:  '  + str(test_labels.shape))

    class_names = ['0', '1', '2', '3', '4',
                   '5', '6', '7', '8', '9']
    plt.figure(figsize=(10,10))
    for i in range(25):
        plt.subplot(5,5,i+1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(train_images[i], cmap=plt.cm.binary)
        plt.xlabel(class_names[train_labels[i]])
    plt.savefig('train_data.png')


def plot_image(i, predictions_array, true_label, img):
    class_names = ['0', '1', '2', '3', '4','5', '6', '7', '8', '9']
    true_label, img = true_label[i], img[i]
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(img, cmap=plt.cm.binary)

    predicted_label = np.argmax(predictions_array)
    if predicted_label == true_label:
        color = 'blue'
    else:
        color = 'red'

    plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],
                                100*np.max(predictions_array),
                                class_names[true_label]),
                                color=color)

def plot_value_array(i, predictions_array, true_label):
    true_label = true_label[i]
    plt.grid(False)
    plt.xticks(range(10))
    plt.yticks([])
    thisplot = plt.bar(range(10), predictions_array, color="#777777")
    plt.ylim([0, 1])
    predicted_label = np.argmax(predictions_array)

    thisplot[predicted_label].set_color('red')
    thisplot[true_label].set_color('blue')


def show_predictions(predictions, test_images, test_labels):

    plt.figure(figsize=(10,10))
    for i in range(25):
        plt.subplot(5,5,i+1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(test_images[i], cmap=plt.cm.binary)
        plt.xlabel(np.argmax(predictions[i]))
    plt.savefig('test_data.png')

    num_rows = 5
    num_cols = 3
    num_images = num_rows*num_cols
    plt.figure(figsize=(2*2*num_cols, 2*num_rows))
    for i in range(num_images):
      plt.subplot(num_rows, 2*num_cols, 2*i+1)
      plot_image(i, predictions[i], test_labels, test_images)
      plt.subplot(num_rows, 2*num_cols, 2*i+2)
      plot_value_array(i, predictions[i], test_labels)
    plt.tight_layout()
    plt.savefig('accuracy.png')


def main():

    num_classes = 10
    input_shape = (28, 28, 1)

    (X_train, Y_train), (X_test, Y_test) = mnist.load_data()
    X_train = X_train.reshape((60000, 28, 28, 1))
    X_test = X_test.reshape((10000, 28, 28, 1))
    X_train, X_test = X_train / 127.5 - 1, X_test / 127.5 - 1

    kwargs = dict(input_quantizer="ste_sign",
              kernel_quantizer="ste_sign",
              kernel_constraint="weight_clip")

    model = tf.keras.Sequential()
    model.add(lq.layers.QuantConv2D(32, (3, 3),
                                kernel_quantizer="ste_sign",
                                kernel_constraint="weight_clip",
                                use_bias=False,
                                input_shape=(28, 28, 1)))
    model.add(tf.keras.layers.MaxPooling2D((2, 2)))
    model.add(tf.keras.layers.BatchNormalization(scale=False))

    model.add(lq.layers.QuantConv2D(64, (3, 3), use_bias=False, **kwargs))
    model.add(tf.keras.layers.MaxPooling2D((2, 2)))
    model.add(tf.keras.layers.BatchNormalization(scale=False))
    #
    model.add(lq.layers.QuantConv2D(64, (3, 3), use_bias=False, **kwargs))
    model.add(tf.keras.layers.BatchNormalization(scale=False))
    model.add(tf.keras.layers.Flatten())
    #
    model.add(lq.layers.QuantDense(64, use_bias=False, **kwargs))
    model.add(tf.keras.layers.BatchNormalization(scale=False))
    model.add(lq.layers.QuantDense(10, use_bias=False, **kwargs))
    model.add(tf.keras.layers.BatchNormalization(scale=False))
    model.add(tf.keras.layers.Activation("softmax"))

    lq.models.summary(model)

    optimizer = lq.optimizers.CaseOptimizer(
    (lq.optimizers.Bop.is_binary_variable, lq.optimizers.Bop()),
    default_optimizer=tf.keras.optimizers.Adam(0.01),
    )

    model.compile(optimizer=optimizer,
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    history = model.fit(X_train, Y_train, batch_size=64, epochs=1)
    test_loss, test_acc = model.evaluate(X_test, Y_test)
    print('\nAccuracy:', test_acc)

    predictions = model.predict(X_test)
    print("prediction: ", np.argmax(predictions[0]))
    show_predictions(predictions, X_test, Y_test)

    # print(model.get_weights())

    # print(model.get_layer('quant_conv2d').get_weights())
    # print(model.get_layer('max_pooling2d').get_weights())
    # print(model.get_layer('quant_conv2d_1').get_weights())
    # print(model.get_layer('max_pooling2d_1').get_weights())
    # print(model.get_layer('quant_conv2d_2').get_weights())
    # print(model.get_layer('flatten').get_weights())
    # print(model.get_layer('quant_dense').get_weights())
    # print(model.get_layer('quant_dense_1').get_weights())
    # print(model.get_layer('activation').get_weights())


main()
