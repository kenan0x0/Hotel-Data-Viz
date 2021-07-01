import streamlit as st
from keras.models import load_model
import pickle
import re
import nltk
from nltk.corpus import stopwords


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

loaded_score_dask = pickle.load(open("C:\\deps\\score_dask.sav", 'rb'))

def app():
    # Remove the made with Streamlit watermark
    hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    review = st.text_area(label="Insert a review to see if it's positive or negative: ", height=400, help="Enter a review")

    if review == "":
        pass
    else:
        first = preprocess_text([review])
        second = remove_stop_words(first)
        loaded_vect = pickle.load(open("C:\\deps\\Hashing_Vect.sav", 'rb'))
        loaded_clas = pickle.load(open("C:\\deps\\SGD.sav", 'rb'))
        third = loaded_vect.fit_transform(second)
        pred = loaded_clas.predict(third)[0]
        if pred == 0:
            st.error("Negative Review ❌")
            st.write("Accuracy: {:.3f}".format(loaded_score_dask))
        else:
            st.success("Positive Review ✔️")
            st.write("Accuracy: {:.3f}".format(loaded_score_dask))
