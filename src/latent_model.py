from matplotlib import pyplot as plt
import tensorflow as tf
import numpy as np
import os
from IPython import display
import pandas as pd
import time
from sklearn import neighbors
from joblib import dump, load
from sklearn.preprocessing import OneHotEncoder


# https://stackoverflow.com/questions/58352326/running-the-tensorflow-2-0-code-gives-valueerror-tf-function-decorated-functio
tf.config.run_functions_eagerly(True)


class CVAE(tf.keras.Model):
    """Convolutional variational autoencoder.
        taken from https://www.tensorflow.org/tutorials/generative/cvae
    """

    def __init__(self, latent_dim):
        super(CVAE, self).__init__()
        self.latent_dim = latent_dim
        self.encoder = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(input_shape=(28, 28, 1)),
                tf.keras.layers.Conv2D(
                    filters=32, kernel_size=3, strides=(2, 2), activation='relu'),
                tf.keras.layers.Conv2D(
                    filters=64, kernel_size=3, strides=(2, 2), activation='relu'),
                tf.keras.layers.Flatten(),
                # No activation
                tf.keras.layers.Dense(latent_dim + latent_dim),
            ]
        )

        self.decoder = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(input_shape=(latent_dim,)),
                tf.keras.layers.Dense(units=7 * 7 * 32, activation=tf.nn.relu),
                tf.keras.layers.Reshape(target_shape=(7, 7, 32)),
                tf.keras.layers.Conv2DTranspose(
                    filters=64, kernel_size=3, strides=2, padding='same',
                    activation='relu'),
                tf.keras.layers.Conv2DTranspose(
                    filters=32, kernel_size=3, strides=2, padding='same',
                    activation='relu'),
                # No activation
                tf.keras.layers.Conv2DTranspose(
                    filters=1, kernel_size=3, strides=1, padding='same'),
            ]
        )

    @tf.function
    def sample(self, eps=None):
        if eps is None:
            eps = tf.random.normal(shape=(100, self.latent_dim))
        return self.decode(eps, apply_sigmoid=True)

    def encode(self, x):
        mean, logvar = tf.split(self.encoder(x), num_or_size_splits=2, axis=1)
        return mean, logvar

    def reparameterize(self, mean, logvar):
        eps = tf.random.normal(shape=mean.shape)
        return eps * tf.exp(logvar * .5) + mean

    def decode(self, z, apply_sigmoid=False):
        logits = self.decoder(z)
        if apply_sigmoid:
            probs = tf.sigmoid(logits)
            return probs
        return logits

    def characters_to_latent(self, images):
        mu = []
        sigma = []

        for index in range(images.shape[0]):
            print(index, end="\r")

            original = images[index:index + 1, :, :, :]

            a, b = self.encode(original)
            z = self.reparameterize(a, b)

            mu.append(float(z[0][0]))
            sigma.append(float(z[0][1]))

        df2 = pd.DataFrame({"mu": mu, "sigma": sigma})
        return df2


def log_normal_pdf(sample, mean, logvar, raxis=1):
    log2pi = tf.math.log(2. * np.pi)
    return tf.reduce_sum(
        -.5 * ((sample - mean) ** 2. * tf.exp(-logvar) + logvar + log2pi),
        axis=raxis)


def compute_loss(model, x):
    mean, logvar = model.encode(x)
    z = model.reparameterize(mean, logvar)
    x_logit = model.decode(z)

    # not sure why the following had to be added in
    x = tf.cast(x, tf.float32)
    cross_ent = tf.nn.sigmoid_cross_entropy_with_logits(logits=x_logit, labels=x)
    logpx_z = -tf.reduce_sum(cross_ent, axis=[1, 2, 3])
    logpz = log_normal_pdf(z, 0., 0.)
    logqz_x = log_normal_pdf(z, mean, logvar)
    return -tf.reduce_mean(logpx_z + logpz - logqz_x)


@tf.function
def train_step(model, x, optimizer):
    """Executes one training step and returns the loss.

    This function computes the loss and gradients, and uses the latter to
    update the model's parameters.
    """
    with tf.GradientTape() as tape:
        loss = compute_loss(model, x)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

def generate_images(model, epoch, test_sample):
    mean, logvar = model.encode(test_sample)
    z = model.reparameterize(mean, logvar)
    predictions = model.sample(z)
    fig = plt.figure(figsize=(4, 4))

    for i in range(predictions.shape[0]):
        plt.subplot(4, 4, i + 1)
        plt.imshow(predictions[i, :, :, 0], cmap='gray')
        plt.axis('off')

    # tight_layout minimizes the overlap between 2 sub-plots
#     plt.savefig('image_at_epoch_{:04d}.png'.format(epoch))
    plt.show()


def train_model(train_images, test_images, model_name, epochs):
    # set the dimensionality of the latent space to a plane for visualization later
    latent_dim = 2
    num_examples_to_generate = 16
    batch_size = 64

    train_size = train_images.shape[0]
    test_size = test_images.shape[0]

    train_dataset = (tf.data.Dataset.from_tensor_slices(train_images)
                     .shuffle(train_size).batch(batch_size))
    test_dataset = (tf.data.Dataset.from_tensor_slices(test_images)
                    .shuffle(test_size).batch(batch_size))

    assert batch_size >= num_examples_to_generate
    for test_batch in test_dataset.take(1):
        test_sample = test_batch[0:num_examples_to_generate, :, :, :]

    # keeping the random vector constant for generation (prediction) so
    # it will be easier to see the improvement.
    random_vector_for_generation = tf.random.normal(
        shape=[num_examples_to_generate, latent_dim])
    model = CVAE(latent_dim)

    generate_images(model, 0, test_sample)
    optimizer = tf.keras.optimizers.Adam(1e-4)

    for epoch in range(1, epochs + 1):
        start_time = time.time()
        for train_x in train_dataset:
            train_step(model, train_x, optimizer)
        end_time = time.time()

        loss = tf.keras.metrics.Mean()
        for test_x in test_dataset:
            loss(compute_loss(model, test_x))
        elbo = -loss.result()

        display.clear_output(wait=False)
        print('Epoch: {}, Test set ELBO: {},time elapse for current epoch: {}'
              .format(epoch, elbo, end_time - start_time))
        generate_images(model, epoch, test_sample)

    return model


def load_or_train_model(train_images, test_images, model_name, epochs,directory):
    """
    load a previously trained model. If no such model exists, train one
    """
    weights_file = f"{directory}weights_{model_name}"

    if not os.path.exists(weights_file + ".index"):
        model = train_model(train_images, test_images, model_name, epochs)
        model.save_weights(weights_file)
    else:
        print("loading")
        latent_dim = 2
        num_examples_to_generate = 16
        batch_size = 64

        model = CVAE(latent_dim)
        model.load_weights(weights_file)

        # show how the loaded model is doing
        test_size = test_images.shape[0]
        test_dataset = (tf.data.Dataset.from_tensor_slices(test_images)
                        .shuffle(test_size).batch(batch_size))
        for test_batch in test_dataset.take(1):
            test_sample = test_batch[0:num_examples_to_generate, :, :, :]
            generate_images(model, 0, test_sample)

    return model


class Classifier:
    def __init__(self, directory, model_name,df=None):
        if df is not None:
            self.clf,self.character_set = self.build_classifier(df,directory,model_name)
        else:
            self.clf,self.character_set = self.load_classifier(directory,model_name)

    @staticmethod
    def build_classifier(df, directory, model_name):
        model_file = os.path.join(directory, model_name + "_knn_clf")
        if os.path.isfile(model_file):
            print("Warning - overwriting existing saved model")

        clf = neighbors.KNeighborsClassifier(10, weights='uniform')
        clf.fit(df[["mu", "sigma"]], df["character"])
        dump(clf, model_file)

        character_set = pd.DataFrame({"character":clf.classes_})
        return clf,character_set

    @staticmethod
    def load_classifier(directory, model_name):
        model_file = os.path.join(directory, model_name+"_knn_clf")
        assert os.path.isfile(model_file)

        clf = load(model_file)

        character_set = pd.DataFrame({"character":clf.classes_})
        return clf, character_set

    def create_and_classify_idealized(self, latent_df):
        """
        calculate the idealized character for every character and get its confidence
        :param latent_df:
        :return:
        """
        ideal_df = latent_df.groupby("character")[["mu", "sigma"]].median().reset_index()
        # make sure that the order in ideal_df matches the order in self.character_set
        ideal_df = ideal_df.merge(self.character_set.reset_index(),on="character")
        ideal_df = ideal_df.sort_values("index").drop("index",axis=1)

        probabilities = self.clf.predict_proba(ideal_df[["mu", "sigma"]])

        size_df = latent_df.groupby("character").size().reset_index()
        size_df = size_df.rename(columns={0: "character_count"})
        ideal_df = ideal_df.merge(size_df, on="character")

        enc = OneHotEncoder(handle_unknown='ignore')
        ideal_as_1hot = enc.fit_transform(self.character_set).todense()
        self_probability = np.multiply(ideal_as_1hot, probabilities)
        ideal_df["confidence"] = np.amax(self_probability,axis=1)

        return ideal_df

    def classify_latent(self, latent_df):
        """
        classify each point in the latent dataframe with both the most likely character
        and our confidence about that classification
        """
        probabilities = self.clf.predict_proba(latent_df[["mu", "sigma"]])
        print(probabilities[0,:])
        df = pd.DataFrame({"confidence": np.amax(probabilities, axis=1)})

        most_likely_as_index = pd.DataFrame(probabilities.argmax(axis=1))
        most_likely = most_likely_as_index.merge(self.character_set, left_on=0, right_index=True, how="left")
        df["most_likely_character"] = most_likely["character"]

        return df
