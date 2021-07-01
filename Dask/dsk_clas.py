# Import important libraries 
from operator import mod
import pandas as pd
import dask
from dask import dataframe as dd
from pymongo import MongoClient
import re
import nltk
from nltk.corpus import stopwords


# Retrieve the review data from the MongoDB DB
client = MongoClient("localhost:27017")
db = client.for_reviews
result = db.reviews.find({}, {"_id":0})
source = list(result)
res_df = pd.DataFrame(source)
ddf = dd.from_pandas(res_df, npartitions=16)

# Split the Features and Label
features = ddf['review']
label = ddf['label']


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

# Apply the cleaning to the reviews
clean = preprocess_text(features)


# Remove unnecessary stopwords from the reviews
nostop_clean = remove_stop_words(clean)

# Turn the reviews into a Pandas Dataframe
finalDF = pd.DataFrame(nostop_clean, columns=["review"])
# Turn the reviews in the Pandas Dataframe into a Dask Dataframe
finalDDF = dd.from_pandas(finalDF, npartitions=16)


from dask_ml.feature_extraction.text import HashingVectorizer
import pickle

# Vectorizer
vect = HashingVectorizer()
pickle.dump(vect, open("Hashing_Vect.sav", 'wb'))

from dask_ml.wrappers import Incremental
from dask_ml import metrics
from sklearn.linear_model import SGDClassifier



# Declare a classifier instance
model = Incremental(SGDClassifier(penalty="l1"), scoring="accuracy", assume_equal_chunks=True)

# Fit the reviews and label in the vectorizer
X=vect.fit_transform(finalDDF["review"])
y = label.astype(int)

# Train the classifier
model.fit(X,y,classes=[0, 1])
# Save the classifier
pickle.dump(model, open("SGD.sav", 'wb'))


# Make a prediction
predictions = model.predict(X)

# Calculate the classifier's accuracy
ac_sc = metrics.accuracy_score(y, predictions)
pickle.dump(ac_sc, open("score_dask.sav", 'wb'))