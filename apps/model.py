import streamlit as st
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import pickle
import re
import nltk
import requests
from nltk.corpus import stopwords
import io
import time


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

# The tokenizer
loaded_tok = pickle.load(open("C:\\deps\\Tokenizer.sav", 'rb'))

# All trained neural networks
loaded_mod_conv = load_model("C:\\deps\\conv1d_model.h5")
loaded_mod_recu = load_model("C:\\deps\\lstm_model.h5")
loaded_mod_norm = load_model("C:\\deps\\flatten_model.h5")

# All scores of the trained networks
loaded_score_conv = pickle.load(open("C:\\deps\\conv1d_model_score.sav", 'rb'))
loaded_score_recu = pickle.load(open("C:\\deps\\rec_model_score.sav", 'rb'))
loaded_score_norm = pickle.load(open("C:\\deps\\flat_model_score.sav", 'rb'))

maxlen = 50


# Inserted review MUST be in a list! Otherwise, each letter in the review will be seen as a review
def live_predict(rev):
    preds = []
    first = preprocess_text(rev)
    second = remove_stop_words(first)
    third = loaded_tok.texts_to_sequences(second)
    fourth = pad_sequences(third, padding='post', maxlen=maxlen)
    pred_conv = preds.append(loaded_mod_conv.predict(fourth))
    pred_recu = preds.append(loaded_mod_recu.predict(fourth))
    pred_norm = preds.append(loaded_mod_norm.predict(fourth))
    return preds

def app():
    # Remove the made with Streamlit watermark
    hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.markdown("<img src=\"https://kenan0x0.github.io/Misc/ml.png\" alt=\"Machine Learning\" style=\"float:right;\"/>", unsafe_allow_html=True)
    rev = st.text_area(label="Insert a review to see if it's positive or negative: ", height=400, help="Enter a review")

    if rev == "":
        st.markdown("The prediction is: " )
    else:

        url = "https://api.meaningcloud.com/sentiment-2.1"


        payload={
            'key': 'b7843f2ad7a95cc4cabfaefcdbf3f8fb',
            'txt': rev,
            'lang': 'en',
        }
        response = requests.post(url, data=payload)
        pos_neg = response.json()["score_tag"]
        conf = response.json()["confidence"]

        col1, col2, col3, col4 = st.beta_columns(4)
        col1.subheader("Conv1D")
        col2.subheader("LSTM")
        col3.subheader("Flatten")
        col4.subheader("API")

        res = live_predict([rev])
        preds = []
        preds.append(int(round(res[0][0][0])))
        preds.append(int(round(res[1][0][0])))
        preds.append(int(round(res[2][0][0])))
        for i in range(len(preds)):
            if preds[i] == 0:
                preds[i] = "Negative"
            else:
                preds[i] = "Positive"
        if ((pos_neg == 'P') | (pos_neg == 'P+')):
            pos_neg = "Positive"
        elif ((pos_neg == 'N') | (pos_neg == 'N+')):
            pos_neg = "Negative"
        else:
            pos_neg = "Neutral"
        col1.write(preds[0])
        col1.write("Accuracy: {:.3f}".format(loaded_score_conv[1]))

        col2.write(preds[1])
        col2.write("Accuracy: {:.3f}".format(loaded_score_recu[1]))

        col3.write(preds[2])
        col3.write("Accuracy: {:.3f}".format(loaded_score_norm[1]))

        col4.write(pos_neg)
        col4.write("Confidence: " + str(conf) + "%")