


import pandas as pd
from nate_tools import GetTaxonID, GetLocationID, GetObservationSummary, GetObservations, ReadDF
from data_objects import DataFrame

"""
# Testing ReadDF
df_fname = "df_out_horny_toads.csv"
obj_raw = pd.read_csv(df_fname)
obj = DataFrame("test_df", obj_raw)
objs={obj.name: obj}
df_name = obj.name
cols = ["preferred_common_name", "iconic_taxon_id", "conservation_status"]
filters = [("conservation_status", "=", "vulnerable")]
res, objs = ReadDF.call(objs, df=df_name, cols=cols, query_tuples=filters)

print(res)
print(objs)
"""

# Testing GetObservations
args = {
    "taxon_id": 40,
    "place_id": 35003,
    "dataframe_name": "gila_monster_obs",
    #"d1": "2024-01-01",
    #"d2": "2025-01-01",
    "n": 10
}
objs={}
res, objs = GetObservations.call(objs, **args)

print(res)
print(type(objs))





