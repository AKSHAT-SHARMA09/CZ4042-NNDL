
'''
This file is used for Hyperparameter Tuning of parameters used in the construction of the LSTM architecture.
The parameters - 
1. Number of Epochs
2. Batch Size
3. Optimization Algorithm
4. Learning Rate
5. Network Weight Initialization
6. Dropout Regularization
are tuned using GridSearchCV.

The remaining parameters, namely the embedding size, input and output dimensions were chosen based on trial and error of 
different parameter values. 

The outputs of the same are presented and discussed in the report.
'''

# Imports for Hyperparameter-Tuning
import nltk
import pandas as pd
from nltk.corpus import stopwords
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D, Dropout, Bidirectional, ConvLSTM2D, Flatten, Conv1D, Attention, Input
from keras.models import Sequential
from sklearn.model_selection import train_test_split
import re
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
import numpy as np
from keras import backend as K
from keras.layers import Layer
from nltk.tokenize import word_tokenize
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV
from keras.constraints import maxnorm
from tensorflow.keras.optimizers import Adam

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

tweetData = pd.read_csv('../data/Feature-Engineered.csv', index_col=False)

# Added in to avoid formatting error
labels = np.array(tweetData['tweettype'])
y = []
for i in range(len(labels)):
    if labels[i] == 'sadness':
        y.append(0)
    elif labels[i] == 'neutral':
        y.append(1)
    elif labels[i] == 'joy':
        y.append(2)
    elif labels[i] == 'love':
        y.append(3)
    elif labels[i] == 'enthusiasm':
        y.append(4)
    elif labels[i] == 'anger':
        y.append(5)
    elif labels[i] == 'surprise':
        y.append(6)
    elif labels[i] == 'relief':
        y.append(7)
    elif labels[i] == 'fear':
        y.append(8)
y = np.array(y)
print(y)
labels = tf.keras.utils.to_categorical(y, 9, dtype="float32")
del y


def featureEngineering(tweet):
    # Lower case tweet
    tweetMod = tweet.lower()
    # Replace URLs with a space in the message
    tweetMod = re.sub('https?:\/\/[a-zA-Z0-9@:%._\/+~#=?&;-]*', ' ', tweetMod)
    # Replace ticker symbols with a space. The ticker symbols are any stock symbol that starts with $.
    tweetMod = re.sub('\$[a-zA-Z0-9]*', ' ', tweetMod)
    # Replace StockTwits usernames with a space. The usernames are any word that starts with @.
    tweetMod = re.sub('\@[a-zA-Z0-9]*', ' ', tweetMod)
    # Replace everything not a letter or apostrophe with a space
    tweetMod = re.sub('[^a-zA-Z\']', ' ', tweetMod)
    # Remove single letter words
    tweetMod = ' '.join([w for w in tweetMod.split() if len(w) > 1])

    return tweetMod


# Process for all tweets
tweetData['modTweet'] = [featureEngineering(tweet) for tweet in tweetData['tweet']]

def lemmatizeTweet(tweet):
  words = [word for word in word_tokenize(tweet) if (word.isalpha()==1)]
  # Remove stop words
  stop = set(stopwords.words('english'))
  words = [word for word in words if (word not in stop)]
  # Lemmatize words (first noun, then verb)
  wnl = nltk.stem.WordNetLemmatizer()
  lemmatized = [wnl.lemmatize(wnl.lemmatize(word, 'n'), 'v') for word in words]
  return " ".join(lemmatized)

tweetData['lemmatizedText'] = tweetData["modTweet"].apply(lambda x:lemmatizeTweet(x))

# Padding of sequences based on number of unique words
tokenizer = Tokenizer(num_words=27608, split=' ')
tokenizer.fit_on_texts(tweetData['lemmatizedText'].values)
X = tokenizer.texts_to_sequences(tweetData['lemmatizedText'].values)
X = pad_sequences(X)

X_train, X_test, Y_train, Y_test = train_test_split(X, labels, test_size=0.3, random_state=42)

len(labels)

"""**Number of Epochs + Batch Size**"""

def build_lstm():
    keras.backend.clear_session()
    model_dropout = Sequential()
    model_dropout.add(Embedding(input_dim=128, output_dim=8, input_length=X.shape[1]))
    model_dropout.add(Dropout(0.4))
    model_dropout.add(Bidirectional(LSTM(units=256, return_sequences=True)))
    model_dropout.add(Dropout(0.4))
    model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
    model_dropout.add(Dense(9, activation='softmax'))
    model_dropout.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model_dropout

# Create model
model = KerasClassifier(build_fn=build_lstm, verbose=0)

# Define the grid search parameters
batch_size = [512, 256, 128, 64]
epochs = [20, 50, 100, 200]
param_grid = dict(batch_size=batch_size, epochs=epochs)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X_train, Y_train)

# Summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

"""**Optimization Algorithm**"""

def build_lstm(optimizer):
    keras.backend.clear_session()
    model_dropout = Sequential()
    model_dropout.add(Embedding(input_dim=27608, output_dim=8, input_length=X.shape[1]))
    model_dropout.add(Dropout(0.4))
    model_dropout.add(Bidirectional(LSTM(units=256, return_sequences=True)))
    model_dropout.add(Dropout(0.4))
    model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
    model_dropout.add(Dense(9, activation='softmax'))
    model_dropout.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return model_dropout

# Create model
model=KerasClassifier(build_fn=build_lstm, epochs=50, batch_size=512, verbose=-1)

# Define the grid search parameters
optimizer = ['SGD', 'RMSprop', 'Adagrad', 'Adam', 'Adamax','Adadelta', 'Nadam'] 
param_grid = dict(optimizer=optimizer)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X_train, Y_train)

# Summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

"""**Learning Rate**"""

def build_lstm(learn_rate):
    keras.backend.clear_session()
    model_dropout = Sequential()
    model_dropout.add(Embedding(input_dim=128, output_dim=8, input_length=X.shape[1]))
    model_dropout.add(Dropout(0.4))
    model_dropout.add(Bidirectional(LSTM(units=256, return_sequences=True)))
    model_dropout.add(Dropout(0.4))
    model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
    model_dropout.add(Dense(9, activation='softmax'))
    optimizer = Adam(lr = learn_rate)
    model_dropout.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return model_dropout

# Create model
model=KerasClassifier(build_fn=build_lstm, epochs=50, batch_size=512, verbose=-1)

# Define the grid search parameters
learn_rate = [0.001, 0.01, 0.03, 0.05, 0.07, 0.09, 0.1, 0.2]
param_grid = dict(learn_rate=learn_rate)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X_train, Y_train)

# Summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))



"""**Network Weight Initialization**"""

def build_lstm(init_mode):
    keras.backend.clear_session()
    model_dropout = Sequential()
    model_dropout.add(Embedding(input_dim=128, output_dim=8, input_length=X.shape[1]))
    model_dropout.add(Dropout(0.4))
    model_dropout.add(Bidirectional(LSTM(units=256, return_sequences=True, kernel_initializer=init_mode)))
    model_dropout.add(Dropout(0.4))
    model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False, kernel_initializer=init_mode)))
    model_dropout.add(Dense(9, activation='softmax'))
    optimizer = Adam(lr = 0.001)
    model_dropout.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return model_dropout

# Create model
model=KerasClassifier(build_fn=build_lstm, epochs=50, batch_size=512, verbose=-1)

# Define the grid search parameters
init_mode = ['uniform', 'lecun_uniform', 'normal', 'zero', 'glorot_normal', 'glorot_uniform', 'he_normal', 'he_uniform']
param_grid = dict(init_mode=init_mode)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X_train, Y_train)

# Summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))



"""**Dropout Regularization**"""

def build_lstm(dropout_rate=0.0, weight_constraint=0):
    embed_dim = 8
    keras.backend.clear_session()
    model_dropout = Sequential()
    model_dropout.add(Embedding(input_dim=128, output_dim=embed_dim, input_length=X.shape[1]))
    model_dropout.add(Dropout(dropout_rate))
    model_dropout.add(Bidirectional(LSTM(units=256, kernel_initializer='normal', return_sequences=True, kernel_constraint=maxnorm(weight_constraint))))
    model_dropout.add(Dropout(dropout_rate))
    model_dropout.add(Bidirectional(LSTM(units=128, kernel_initializer='normal', return_sequences=False)))
    model_dropout.add(Dense(9, activation='softmax'))
    optimizer = Adam(lr=0.001)
    model_dropout.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return model_dropout

# Create model
model=KerasClassifier(build_fn=build_lstm, epochs=50, batch_size=512, verbose=-1)

# Define the grid search parameters
weight_constraint = [1, 2, 3, 4, 5]
dropout_rate = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
param_grid = dict(dropout_rate=dropout_rate, weight_constraint=weight_constraint)
grid = GridSearchCV(estimator=model, param_grid=param_grid, cv=3)
grid_result = grid.fit(X_train, Y_train)

# Summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

"""**Trial and Error of remaining parameters based on Accuracy + Loss Plots**"""

embed_dim = 64
keras.backend.clear_session()
model_dropout = Sequential()
model_dropout.add(Embedding(max(pd.DataFrame(X_train).max())+1,embed_dim,input_length = X.shape[1]))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
model_dropout.add(Dense(9, activation='softmax'))

model_dropout.summary()

model_dropout.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
history = model_dropout.fit(X_train, Y_train, epochs = 20, batch_size=64, validation_data=(X_test, Y_test))

# plotting the accuracies for the training epochs
plt.figure(1)
plt.plot(history.history['categorical_accuracy'])
plt.plot(history.history['val_categorical_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testAcc1.png')

# plotting the losses for the training epochs
plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('cross-entropy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testloss1.png')

embed_dim = 128
keras.backend.clear_session()
model_dropout = Sequential()
model_dropout.add(Embedding(max(pd.DataFrame(X_train).max())+1,embed_dim,input_length = X.shape[1]))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
model_dropout.add(Dense(9, activation='softmax'))

model_dropout.summary()

model_dropout.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
history = model_dropout.fit(X_train, Y_train, epochs = 20, batch_size=64, validation_data=(X_test, Y_test))

plt.figure(1)
plt.plot(history.history['categorical_accuracy'])
plt.plot(history.history['val_categorical_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testAcc4.png')

plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('cross-entropy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testloss4.png')

embed_dim = 32
keras.backend.clear_session()
model_dropout = Sequential()
model_dropout.add(Embedding(max(pd.DataFrame(X_train).max())+1,embed_dim,input_length = X.shape[1]))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
model_dropout.add(Dense(9, activation='softmax'))

model_dropout.summary()

model_dropout.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
history = model_dropout.fit(X_train, Y_train, epochs = 20, batch_size=64, validation_data=(X_test, Y_test))

plt.figure(1)
plt.plot(history.history['categorical_accuracy'])
plt.plot(history.history['val_categorical_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testAcc5.png')

plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('cross-entropy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testloss5.png')

embed_dim = 16
keras.backend.clear_session()
model_dropout = Sequential()
model_dropout.add(Embedding(max(pd.DataFrame(X_train).max())+1,embed_dim,input_length = X.shape[1]))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
model_dropout.add(Dense(9, activation='softmax'))

model_dropout.summary()

model_dropout.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
history = model_dropout.fit(X_train, Y_train, epochs = 20, batch_size=64, validation_data=(X_test, Y_test))

plt.figure(1)
plt.plot(history.history['categorical_accuracy'])
plt.plot(history.history['val_categorical_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testAcc6.png')

plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('cross-entropy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testloss6.png')

embed_dim = 8
keras.backend.clear_session()
model_dropout = Sequential()
model_dropout.add(Embedding(max(pd.DataFrame(X_train).max())+1,embed_dim,input_length = X.shape[1]))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
model_dropout.add(Dense(9, activation='softmax'))

model_dropout.summary()

model_dropout.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
history = model_dropout.fit(X_train, Y_train, epochs = 20, batch_size=64, validation_data=(X_test, Y_test))

plt.figure(1)
plt.plot(history.history['categorical_accuracy'])
plt.plot(history.history['val_categorical_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testAcc7.png')

plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('cross-entropy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testloss7.png')

embed_dim = 8
keras.backend.clear_session()
model_dropout = Sequential()
model_dropout.add(Embedding(max(pd.DataFrame(X_train).max())+1,embed_dim,input_length = X.shape[1]))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=True)))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
model_dropout.add(Dense(9, activation='softmax'))

model_dropout.summary()

model_dropout.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
history = model_dropout.fit(X_train, Y_train, epochs = 20, batch_size=64, validation_data=(X_test, Y_test))

plt.figure(1)
plt.plot(history.history['categorical_accuracy'])
plt.plot(history.history['val_categorical_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testAcc8.png')

plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('cross-entropy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testloss8.png')

embed_dim = 8
keras.backend.clear_session()
model_dropout = Sequential()
model_dropout.add(Embedding(max(pd.DataFrame(X_train).max())+1,embed_dim,input_length = X.shape[1]))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=256, return_sequences=True)))
model_dropout.add(Dropout(rate=0.4))
model_dropout.add(Bidirectional(LSTM(units=128, return_sequences=False)))
model_dropout.add(Dense(9, activation='softmax'))

model_dropout.summary()

model_dropout.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
history = model_dropout.fit(X_train, Y_train, epochs = 20, batch_size=64, validation_data=(X_test, Y_test))

plt.figure(1)
plt.plot(history.history['categorical_accuracy'])
plt.plot(history.history['val_categorical_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testAcc9.png')

plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('cross-entropy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='best')
plt.savefig('/content/drive/MyDrive/NNDL-Group-project/plots/testloss9.png')