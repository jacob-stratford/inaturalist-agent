


import pandas as pd
from nate_tools import GetTaxonID, GetLocationID, GetObservationData, ReadDF
from data_objects import DataFrame



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




