import streamlit as st
import pandas as pd
import plotly.express as px
from ret_hotels import ret_df
from pymongo import MongoClient


def app():
    # Remove the made with Streamlit watermark
    hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    
    # Retrieve the dataset for hotels which is saved in the MongoDB DB
    all_dat = ret_df("localhost:27017")

    # APP BEGINS HERE: Title
    st.title("Hotels in Europe 🏨")
    
    # FILTERS
    st.sidebar.header("Filters: 🔍")
    # Country Filter
    country_filter = st.sidebar.multiselect(label="Select a Country", options=list(all_dat.country.sort_values().unique()), help="Select a country or all countries", default=list(all_dat.country.sort_values().unique()))

    # Score filter
    score_filter = st.sidebar.slider(label="Filter hotels on average score", min_value=0.0, max_value=10.0, value=7.0, step=0.1, help="Will display all hotels from given score and higher")

    # Review_NR filter
    rev_nr_filter = st.sidebar.radio(label="Filter hotels on number of reviews", options=(["All", "< 500", "500 - 1000", "1000 - 2000", "2000 - 5000"]), help="Will display all hotels from given score and higher")

    # Raw data filter
    show_dat = st.sidebar.checkbox(label="Show raw data in table", value=False)

    # Breakline between filters
    st.sidebar.markdown("---")


    # Interactivity code
    if rev_nr_filter == "All":
        client = MongoClient("localhost:27017")
        db = client.for_hotels
        result = db.hotels.find({
            "country" : { "$in" : country_filter},
            "Average_Score" : { "$gte" : score_filter}
        })
        source = list(result)
        resultDf = pd.DataFrame(source)
        all_dat = resultDf
        # all_dat = all_dat.loc[(all_dat.country.isin(country_filter)) & (all_dat.Average_Score >= score_filter)]
    elif rev_nr_filter == "< 500":
        client = MongoClient("localhost:27017")
        db = client.for_hotels
        result = db.hotels.find({
            "country" : { "$in" : country_filter},
            "Average_Score" : { "$gte" : score_filter},
            "nr_revs" : {"$lt" : 500}
        })
        source = list(result)
        resultDf = pd.DataFrame(source)
        all_dat = resultDf
        # all_dat = all_dat.loc[(all_dat.country.isin(country_filter)) & (all_dat.Average_Score >= score_filter) & (all_dat.nr_revs < 500)]
    elif rev_nr_filter == "500 - 1000":
        client = MongoClient("localhost:27017")
        db = client.for_hotels
        result = db.hotels.find({
            "country" : { "$in" : country_filter},
            "Average_Score" : { "$gte" : score_filter},
            "nr_revs" : {"$gte" : 500, "$lte" : 1000}
        })
        source = list(result)
        resultDf = pd.DataFrame(source)
        all_dat = resultDf
        # all_dat = all_dat.loc[(all_dat.country.isin(country_filter)) & (all_dat.Average_Score >= score_filter) & ((all_dat.nr_revs >= 500) & (all_dat.nr_revs <= 1000))]
    elif rev_nr_filter == "1000 - 2000":
        client = MongoClient("localhost:27017")
        db = client.for_hotels
        result = db.hotels.find({
            "country" : { "$in" : country_filter},
            "Average_Score" : { "$gte" : score_filter},
            "nr_revs" : {"$gte" : 1000, "$lte" : 2000}
        })
        source = list(result)
        resultDf = pd.DataFrame(source)
        all_dat = resultDf
        # all_dat = all_dat.loc[(all_dat.country.isin(country_filter)) & (all_dat.Average_Score >= score_filter) & ((all_dat.nr_revs >= 1000) & (all_dat.nr_revs <= 2000))]
    else:
        client = MongoClient("localhost:27017")
        db = client.for_hotels
        result = db.hotels.find({
            "country" : { "$in" : country_filter},
            "Average_Score" : { "$gte" : score_filter},
            "nr_revs" : {"$gte" : 2000, "$lte" : 5000}
        })
        source = list(result)
        resultDf = pd.DataFrame(source)
        all_dat = resultDf
        # all_dat = all_dat.loc[(all_dat.country.isin(country_filter)) & (all_dat.Average_Score >= score_filter) & ((all_dat.nr_revs >= 2000) & (all_dat.nr_revs <= 5000))]

    
    st.sidebar.markdown("Number of hotels **" + str(len(all_dat)) + "**")

    px.set_mapbox_access_token("pk.eyJ1Ijoia2VuYW4weDAiLCJhIjoiY2tubHd3ZG14MHA1MjJ3cG0xbHU5a21pYyJ9.QGp80xoE6SEA00FtbuDMXA")
    try:
        fig = px.scatter_mapbox(all_dat, lat="lat", lon="lon", color="country", size="Average_Score", hover_name="Hotel_Name",
                                mapbox_style="dark", zoom=5, hover_data={"Hotel_Address":True, "Average_Score":True, "nr_revs":True, "country": False, "lat": False, "lon": False},
                                width=1200, height=550)
        fig.update_layout(showlegend=True)
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Rockwell"
            ),legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        st.plotly_chart(fig)

        st.markdown("---")

        # st.title("Number of hotels")
        nr_hotels = pd.DataFrame(all_dat["country"].value_counts())
        st.markdown("## Number of Hotels")
        st.bar_chart(nr_hotels)

        if ((len(country_filter) == 1) | (len(list(all_dat["country"].unique())) == 1)):
            st.markdown("---")
            st.markdown("## Hotel Scoring")
            fig2 = px.scatter(data_frame=all_dat, x=all_dat["Average_Score"], y=all_dat["nr_revs"], size=all_dat["Average_Score"],
                            hover_name=all_dat["Hotel_Name"], color=all_dat["Average_Score"], template="plotly_dark", width=1300, height=700)


            fig2.update_layout(
            xaxis_title="Average Reviewer Score",
            yaxis_title="Number of Reviews",
            legend_title="Average Score",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="white"
            )
        )
            st.plotly_chart(fig2)
        else:
            pass


        if show_dat:
            st.markdown("---")
            st.markdown("## Raw Data Table")
            st.table(all_dat.loc[:, ["Hotel_Name", "Average_Score", "Hotel_Address"]])
        else:
            pass

    except (KeyError, ValueError):
        st.error("No hotels found that satisfy the given filters!")