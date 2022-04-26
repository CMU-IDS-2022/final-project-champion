import streamlit as st
import altair as alt
import pprint
import pandas as pd
import json
import geopandas as gpd

from vega_datasets import data
from altair import datum
from collections import defaultdict

alt.data_transformers.enable('default', max_rows=None)

top10cities = set(["Boston", "Chicago", "Detroit", "Los Angeles", "New York", "Philadelphia", "Pittsburgh", "San Francisco", "Seattle", "Washington"])

bedroomTypes = set(["1br", "2br", "3br", "4br", "5br", "condo"])

def readCsv(fileName):
  return pd.read_csv(fileName)


################## geoJson section ##################
city_neighborhood_mapping = {
	"Boston": "Neighborhood_ID",
	"SanFrancisco": "nhood",
}

def addLatLonGeometry(df):
  df.loc[:, 'lon'] = df.geometry.centroid.x
  df.loc[:, 'lat'] = df.geometry.centroid.y
  return df


@st.cache
def readGeoFile(fileName):
  geoJson = gpd.read_file(fileName)
  return addLatLonGeometry(geoJson)


# geo json chart
def showGraphChart(geoDf, labelName='nhood'):
  # chart object
  graph1 = alt.Chart(geoDf).mark_geoshape().encode(
      color=labelName,
      tooltip=labelName,
  ).properties( 
      width=500,
      height=500
  ).project(
      type='identity', reflectY=True
  )

  labels = alt.Chart(geoDf).mark_text().encode(
      longitude='lon',
      latitude='lat',
      text=labelName,
      size=alt.value(8),
      opacity=alt.value(0.6)
  )
  return graph1+labels

################## city level section ##################
# filter df by city
def filterByCity(df, city):
  return df[df['City'] == city]


################## neighborhood level section ##################

# filter df by neighborhood
def filterByNeighborhood(df, neighborhood):
  return df[df['Neighborhood'] == neighborhood]



def getTopNeighborhoods(df, num):
  return df.drop_duplicates(subset=['MeanPrices']).nlargest(num, ['MeanPrices'])['Neighborhood'].tolist()


def getBottomNeighborhoods(df, num):
  return df.drop_duplicates(subset=['MeanPrices']).nsmallest(num, ['MeanPrices'])['Neighborhood'].tolist()



# lines for covid
covidLine = alt.Chart(pd.DataFrame({'x': ['2020']})).mark_rule(color='red').encode(x='x:T')
postCovidLine = alt.Chart(pd.DataFrame({'x': ['2021']})).mark_rule(color='orange').encode(x='x:T')

# text for pandemic
prepandemicText = alt.Chart(pd.DataFrame({'x': ['2019-01'], 'y': ['5250']})).mark_text(text='Pre-pandemic').encode(x='x:T', y='y:Q')
pandemicText = alt.Chart(pd.DataFrame({'x': ['2020-07'], 'y': ['5250']})).mark_text(text='Pandemic').encode(x='x:T', y='y:Q')
postpandemicText = alt.Chart(pd.DataFrame({'x': ['2021-08'], 'y': ['5250']})).mark_text(text='Post-pandemic').encode(x='x:T', y='y:Q')

# line chart for top neighborhood
# alt.Chart(temp_df).mark_line().encode(
#     x=alt.X('Date:T'),
#     y=alt.Y('Prices:Q', scale=alt.Scale(zero=False)),
#     color=alt.Color('Neighborhood'),
#     tooltip=['Neighborhood', 'Prices']
# ).transform_filter(
#     alt.FieldOneOfPredicate(field='Neighborhood', oneOf=topNeighbors + bottomNeighbors)
# ).properties(
#     width=600, height=300,
#     title='Top 5 most expensive and cheapest neighborhooods for rents'
# )

def visualizeCity(city):
	st.write('showing city:', city)
	# load geojson data from city
	geoFileName = f"GeojsonData/{city}Neighborhoods.geojson"
	geoData = readGeoFile(geoFileName)
	st.write(showGraphChart(geoData, city_neighborhood_mapping[city]))



# function to load all the data and interactions
def loadNeighborhoodData():
	citySelection = st.selectbox("Which city would you like to see?", top10cities)
	visualizeCity(citySelection.replace(' ', ''))
