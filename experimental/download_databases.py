# This script tries (and mostly fails) to download full databases in sequence. I don't
# recommend trying this.

import imfp
from pandas import DataFrame

# Set a custom wait time
_imf_wait_time = 10

# Attempt to download databases sequentially
databases: DataFrame = imfp.imf_databases()
datasets: dict[str, list[DataFrame | None]] = {"database_names": [], "dataframes": []}
for database_id in databases["database_id"]:
    datasets["database_names"].append(database_id)
    try:
        datasets["dataframes"].append(imfp.imf_dataset(database_id))
    except Exception as e:
        datasets["dataframes"].append(None)
        print("An error occurred when downloading", database_id, ": ", e)
