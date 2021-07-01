import pandas as pd


# This script takes one parameter which is the name of a CSV file which will be cleaned.
def clean_Data(filename):
    
    df = pd.read_csv(filename)
    df

    dfNeg = df.loc[:, ["Negative_Review"]].loc[df.Review_Total_Negative_Word_Counts > 7]
    dfPos = df.loc[:, ["Positive_Review"]].loc[df.Review_Total_Positive_Word_Counts > 7]

    dfNeg.rename(columns = {'Negative_Review':'review'}, inplace = True)
    dfNeg["label"] = 0
    dfNeg

    dfPos.rename(columns = {'Positive_Review':'review'}, inplace = True)
    dfPos["label"] = 1
    dfPos

    cleaned_df = pd.concat([dfNeg, dfPos], ignore_index=True)
    cleaned_df = cleaned_df.sample(frac = 1).reset_index(drop=True)
    return cleaned_df
    