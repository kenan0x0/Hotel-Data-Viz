from pymongo import MongoClient
import pandas as pd
from clean_data import clean_Data

filename = "C:\\deps\\Hotel_Reviews.csv"
client = MongoClient("localhost:27017")

# Dataframe for the reviews only
df = clean_Data(filename)


# The dataframe responsible for hotels. Not reviews
all_dat = pd.read_csv(filename, sep=",")

# Drop empty values
all_dat.dropna(inplace=True)

# Remove all duplicate hotel names to make sure that only unique hotel names are left over
all_dat = all_dat.drop_duplicates(subset="Hotel_Name")

# Create a new column "country". Will contain the name of the country where a hotel is located
all_dat["country"] = all_dat.Hotel_Address.apply(lambda x: "The Netherlands" if("Netherlands" in x) else "United Kingdom" if("United Kingdom" in x) else "France" if("France" in x) else "Spain" if("Spain" in x) else "Austria" if("Austria" in x) else "Italy" if("Italy" in x) else "Somewhere Else!?")

# Streamlit understands lon but not lng. Replace to work
all_dat = all_dat.rename(columns={"lng": "lon"})

# This new dataframe will be used to supply the new hotel dataframe with relavant info such as the number of reviews for each hotel and pos and neg reviews for later
df2 = pd.read_csv(filename, sep=",")

# Create a new column which will insert the number of reviews a hotel has
z = df2['Hotel_Name'].value_counts()
z1 = z.to_dict()
all_dat['nr_revs'] = all_dat['Hotel_Name'].map(z1) 

# Connect to the respective database. It'll create one if one does not already exist
db = client.for_reviews
db2 = client.for_hotels


# Sends the cleaned datasets both for the reviews (used in Models) and hotels (used in the dashboard)
db.reviews.insert_many(df.to_dict('records'))
db2.hotels.insert_many(all_dat.to_dict('records'))