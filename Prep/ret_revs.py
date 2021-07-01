from pymongo import MongoClient
import pandas as pd
import dask.dataframe as ddf

def ret_df(host):
    client = MongoClient(host)
    db = client.for_reviews
    result = db.reviews.find({}, {"_id":0})
    source = list(result)
    res_df = pd.DataFrame(source)
    res_df = ddf.from_pandas(res_df, npartitions=2)
    return res_df