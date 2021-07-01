import streamlit as st
import pandas as pd
import plotly.express as px
from ret_hotels import ret_df
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import requests
import plotly.graph_objects as go
import time


def app():
    # Remove the made with Streamlit watermark
    hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    all_dat = ret_df("localhost:27017")
    df = pd.read_csv("C:\\deps\\Hotel_Reviews.csv", sep=",")
    


    st.markdown("## Map With Hotels")
    hotel_names = list(all_dat["Hotel_Name"])
    hotel_names.insert(0, "")

    hotel_name = st.sidebar.selectbox(label="Search Hotel Name", options=hotel_names, help="Enter hotel name to see info about that hotel")

    if hotel_name == "":
        st.map(all_dat)
    else:
        all_dat = all_dat.loc[all_dat.Hotel_Name == hotel_name]
        st.map(all_dat)
        fig = px.pie(df, values=df["Reviewer_Nationality"].loc[df.Hotel_Name == hotel_name].value_counts(), names=df["Reviewer_Nationality"].loc[df.Hotel_Name == hotel_name].unique())
        fig.update_layout(width=900,
                            height=700,
                            margin=dict(l=1, r=1, b=1, t=1))
        fig.update_traces(textposition='inside')
        st.markdown("---")
        st.markdown("## Nationality of reviewers for hotel **" + str(hotel_name) + "**")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        st.markdown("## Word Clouds for hotel **" + str(hotel_name) + "**")
        #### Add wordcloud here
        

        my_stopwords = set(STOPWORDS)
        my_stopwords.update(["Hotel", "Staff", "hotel", "room", "staff", "did", "Did", "Didn't", "didn't", "location", "breakfast", "was", "wasn't", "didn t", "wasn t"])
        # Negative Word Cloud
        down_mask = np.array(Image.open("./down.png"))
        wordcloud = WordCloud(width=800, height=400, colormap= "Reds", stopwords= my_stopwords, background_color="rgba(255, 255, 255, 0)", mode="RGBA", max_words=2000, mask=down_mask).generate(' '.join(df["Negative_Review"].loc[df.Hotel_Name == hotel_name]))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.margins(x=0, y=0)
        plt.show()
        wordcloud.to_file("./wc_down.png")
        
        # Positive Word Cloud
        up_mask = np.array(Image.open("./up.png"))
        wordcloud2 = WordCloud(width=800, height=400, colormap= "Greens", stopwords= my_stopwords, background_color="rgba(255, 255, 255, 0)", mode="RGBA", max_words=2000, mask=up_mask).generate(' '.join(df["Positive_Review"].loc[df.Hotel_Name == hotel_name]))
        plt.imshow(wordcloud2, interpolation="bilinear")
        plt.axis("off")
        plt.margins(x=0, y=0)
        plt.show()
        wordcloud2.to_file("./wc_up.png")


        #### Add wordcloud here
        col1, col2 = st.beta_columns(2)
        col1.subheader("Word Cloud of Negative Reviews")
        col1.image("./wc_down.png")
        col2.subheader("Word Cloud of Positive Reviews")
        col2.image("./wc_up.png")

        


        # GOOGLE PLACES AND DETAILS APIs AND API KEYS---- KEEP SEPARATE FOR CLARITY
        # API Key for Places
        places_api_key = "AIzaSyBHtlD7NRsVdjMCQT9PVBUoF--PKmQFD3E"
        location = hotel_name

        endpoint_place = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
        endpoint_details = 'https://maps.googleapis.com/maps/api/place/details/json?'
        endpoint_photos = "https://maps.googleapis.com/maps/api/place/photo?"

        place_params = {'key': places_api_key,
                    'input': location,
                    'language': 'en',
                    'inputtype': 'textquery'}

        place_response = requests.get(endpoint_place, params=place_params)
        place_id = place_response.json()["candidates"][0]["place_id"]

        details_params = {'key': places_api_key,
                    'place_id': place_id,
        }

        details_response = requests.get(endpoint_details, params=details_params)
        all_info = details_response.json()

        
        phone_number = all_info["result"]["international_phone_number"]
        google_maps = all_info["result"]["url"]
        try:
            website = all_info["result"]["website"]
        except:
            website = "Unknown"
        lat = all_info["result"]["geometry"]["location"]["lat"]
        lng = all_info["result"]["geometry"]["location"]["lng"]
        try:
            open_now = all_info["result"]["opening_hours"]["open_now"]
            if (open_now):
                open_now = "Yes"
            else:
                open_now = "No"
            opening_days = all_info["result"]["opening_hours"]["weekday_text"]
        except KeyError:
            open_now = "Unknown"
            opening_days = ["Not Found"]
        addr = all_info["result"]["formatted_address"]
        all_photos = []
        try:
            for i in range(len(all_info["result"]["photos"])):
                all_photos.append(all_info["result"]["photos"][i]["photo_reference"])
        except KeyError:
            pass
        
        

        # Weather API, DO NOT CHANGE! KEEP EMPTY######################################################
        all_dat["cty"] = all_dat.country.apply(lambda x: "Amsterdam" if("Netherlands" in x) else "London" if("United Kingdom" in x) else "Paris" if("France" in x) else "Barcelona" if("Spain" in x) else "Vienna" if("Austria" in x) else "Milan" if("Italy" in x) else "Unknown!?")
        API_KEY_WEATHER = "11551f48ac9b3b88a4f577acf96dc825"
        CITY = all_dat["cty"]
        weather_params = {
            "q" : CITY,
            "APPID" : API_KEY_WEATHER,
            "units" : "metric"
        }
        ENDPOINT_WEATHER = "http://api.openweathermap.org/data/2.5/weather?"
        res = requests.get(ENDPOINT_WEATHER, weather_params)
        cont = res.json()
        icon = cont["weather"][0]["icon"]
        desc = cont["weather"][0]["description"]
        main = cont["weather"][0]["main"]
        city_name = cont["name"]
        country_code = cont["sys"]["country"]
        temp = cont["main"]["temp"]
        feels_like = cont["main"]["feels_like"]
        ENDPOINT_WEATHER_ICON = f"http://openweathermap.org/img/wn/{icon}@2x.png"

        im = Image.open(requests.get(ENDPOINT_WEATHER_ICON, stream=True).raw)
        im.save("C:\\deps\\wthr.png")
        icon_image = Image.open("C:\\deps\\wthr.png")
        # Weather API, DO NOT CHANGE! KEEP EMPTY######################################################


        st.sidebar.markdown("---")
        st.sidebar.markdown("Selected Hotel: **" + str(hotel_name) + "**")
        st.sidebar.markdown("Open Now: **" + str(open_now) + "**")
        st.sidebar.markdown("Total Reviews: **" + str(list(all_dat["nr_revs"])[0]) + "**")
        st.sidebar.markdown("Avg. Reviewer Score: **" + str(int(list(all_dat["Average_Score"])[0]*10)) + "**")
        st.sidebar.progress(int(list(all_dat["Average_Score"])[0]*10))
        st.sidebar.markdown("Hotel Address: **" + str(addr) + "**")
        st.sidebar.markdown("Phone Number: **" + str(phone_number) + "**")
        st.sidebar.markdown("Website: **" + str(website) + "**")
        st.sidebar.table(opening_days)
        sidebar_info, sidebar_icon = st.sidebar.beta_columns(2)
        sidebar_info.markdown("Place: <br />" + "**" + str(city_name) + "**, **" + str(country_code) + "**", unsafe_allow_html = True)
        sidebar_info.markdown("Description: <br />" + "**" + str(main) + "**, **" + str(desc) + "**", unsafe_allow_html = True)
        sidebar_info.markdown("Temperature: <br />" + "**" + str(temp) + "**", unsafe_allow_html = True)
        sidebar_info.markdown("Feels like: <br />" + "**" + str(feels_like) + "**", unsafe_allow_html = True)
        sidebar_icon.image(icon_image)
        st.sidebar.markdown(f"More information about the hotel [here]({google_maps})")



        # GOOGLE PLACES AND DETAILS APIs AND API KEYS---- KEEP SEPARATE FOR CLARITY


        # Streetview requests and API key
        # streetview_api_key = "AIzaSyAAdSKGuz3XxCaXkNqb2vwMiLjC-usuoII"

        # pic_params = {'key': streetview_api_key,
        #             'location': addr,
        #             'fov':100,
        #             'size': "1200x700"}

        # url = 'https://maps.googleapis.com/maps/api/streetview?'
        # pic_response = requests.get(url, params=pic_params)

        # with open('location.jpg', 'wb') as file:
        #     file.write(pic_response.content)
        # pic_response.close()
        # st.markdown("---")
        # st.markdown("## Google Streets shot of hotel *"+hotel_name+"*")
        # st.image("location.jpg")
        # Test street view


#float(all_dat["lon"])
#         &heading=100
        st_view = f'''
        <iframe
        width="1040"
        height="510"
        frameborder="0" style="border:0"
        src="https://www.google.com/maps/embed/v1/streetview
        ?key=AIzaSyB-Brz_YiD68v6gQNyrDbWXvb9ViY2Wd58
        &location={lat},{lng}
        &pitch=10
        &fov=100" allowfullscreen>
        </iframe>
        '''
        st.markdown("---")
        st.markdown("## Street view of hotel **" + str(hotel_name) + "**")
        st.markdown(st_view, unsafe_allow_html=True)


        # SHOW IMAGES OF THE SELECTED HOTEL
        try:
            final_images_paths = []
            counter = 1
            for ref in all_photos:
                photo_params = {'photoreference': ref,
                            'maxwidth': 500,
                            'key': places_api_key
                }
                photos_request = requests.get(endpoint_photos, params=photo_params)
                image_name = "C:\\deps\\images\\" + str(counter) + ".jpg"
                with open(image_name, 'wb') as file:
                    file.write(photos_request.content)
                counter += 1
                final_images_paths.append(image_name)

            photos_request.close()

            st.markdown("---")
            st.markdown("## Images of hotel **" + str(hotel_name) + "**")
            hotel_imgs = []
            for path in final_images_paths:
                image = Image.open(path)
                image = image.resize((500,333))
                hotel_imgs.append(image)
            st.image(hotel_imgs)
        except:
            st.markdown("---")
            st.markdown("### Hotel **" + str(hotel_name) + "** has no public images!")
            err_image = Image.open("C:\\deps\\errFil.png")
            st.image(err_image)
            # image = image.resize((500,333))
            # hotel_imgs.append(image)
