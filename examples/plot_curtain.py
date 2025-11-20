"""
TOLNet Ozone Curtain Plot
=========================

This example shows how to acquire TOLNet data from UAH and make a curtain plot."""

# %%
# Initialize API and Find Data
# ----------------------------

# python -m pip install git+https://github.com/barronh/pytolnet.git
import pytolnet

api = pytolnet.TOLNetAPI()

# Find newest data from UAH
cldf = api.data_calendar('UAH')
# Choose newest?
data_id = cldf['regular_id'].max()
# Choose specific version
# data_id = 12607

# %%
# Retrieve and Characterize Data
# ------------------------------

ds = api.to_dataset(data_id)

df = ds.to_dataframe().reset_index()
print(df.describe())

# Make a curtain plot
qm = ds['derived_ozone'].T.plot(figsize=(12, 4), vmin=30, vmax=100)
qm.figure.savefig(f'derived_ozone_{data_id}.png')
