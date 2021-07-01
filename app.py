import streamlit as st
from apps import map, model, hotel_info, dsk_snt
from multiapp import MultiApp

# plotly, streamlit, tensorflow, keras, nltk, sklearn

app = MultiApp()

st.set_page_config(layout="wide", initial_sidebar_state="auto")

st.sidebar.markdown("Assignment 2 - Big Data - HvA")


app.add_app("Hotel Map", map.app)
app.add_app("Hotel Info", hotel_info.app)
app.add_app("Model", model.app)
app.add_app("Dask", dsk_snt.app)

app.run()