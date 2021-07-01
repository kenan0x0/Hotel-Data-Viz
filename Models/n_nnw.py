# Import the needed libraries which are needed for the correct functioning of the model and data
import pickle
from ret_revs import ret_df
import re
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras.layers.core import Dense
from keras.layers.embeddings import Embedding
from keras.layers import Flatten

from matplotlib import pyplot as plt


# Retrieve the dataset from the mongoDB DB
df = ret_df("localhost:27017")

# Clean and remove the stopwords from the reviews (Assignment 1 as reviews didn't change, therefore, no need to change the cleaning process)
REPLACE_NO_SPACE = re.compile("(\.)|(\;)|(\:)|(\!)|(\?)|(\,)|(\")|(\()|(\))|(\[)|(\])|(\d+)")
REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")
NO_SPACE = ""
SPACE = " "

def preprocess_text(rev):
    rev = [REPLACE_NO_SPACE.sub(NO_SPACE, line.lower()) for line in rev]
    rev = [REPLACE_WITH_SPACE.sub(SPACE, line) for line in rev]

    return rev


english_stop_words = stopwords.words('english')
def remove_stop_words(corpus):
    removed_stop_words = []
    for review in corpus:
        removed_stop_words.append(
            ' '.join([word for word in review.split() 
                      if word not in english_stop_words])
        )
    return removed_stop_words


# Clean the data
cleaned = preprocess_text(df["review"])

# Remove stopwords
stop_removed = remove_stop_words(cleaned)

# Create the features and label to allow for successful creation of the train and test data
X = stop_removed
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Tokenize the reviews
max_words = 5000


tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(X_train)


X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)

maxlen = 50

X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

# Adding 1 because of reserved 0 index
vocab_size = len(tokenizer.word_index) + 1

# Create the model
model = Sequential()
model.add(Embedding(vocab_size, 32, input_length=maxlen))
model.add(Flatten())
model.add(Dense(250, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])


# Train the neural network
history = model.fit(X_train, y_train, batch_size=128, epochs=6, verbose=1, validation_split=0.2)
score = model.evaluate(X_test, y_test, verbose=1)