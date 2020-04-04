import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# mess around with the MGDS data

df = pd.read_csv('data/MGDS/plastics.csv')

# Plastic concentration in pieces per km^2
print(df)
print(df.dtypes)
df.astype('float64').dtypes
print(df.dtypes)

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

print(gdf.head())

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
ax = world.plot(
    color='white', edgecolor='black')

# We can now plot our ``GeoDataFrame``.
gdf.plot(ax=ax, color='red')

plt.show()
