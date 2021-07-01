from pymongo import MongoClient
import pandas as pd

def ret_df(host):
    client = MongoClient(host)
    db = client.for_hotels
    result = db.hotels.find({}, {"_id":0})
    source = list(result)
    res_df = pd.DataFrame(source)
    return res_df