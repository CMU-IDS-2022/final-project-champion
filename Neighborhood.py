import streamlit as st
import altair as alt
import pprint
import pandas as pd
import json
import geopandas as gpd
import pyproj
import numpy as np
import matplotlib.pyplot as plt

from vega_datasets import data
from altair import datum
from collections import defaultdict

alt.data_transformers.enable('default', max_rows=None)

top10cities = set(["Boston", "Chicago", "Detroit", "Los Angeles", "New York", "Philadelphia", "Pittsburgh", "San Francisco", "Seattle", "Washington"])

bedroomTypes = {"1 bedroom": "1br", "2 bedrooms" : "2br", "3 bedrooms" :"3br", "4 bedrooms" : "4br", "5 bedrooms" : "5br", "Condominium" : "condo"}

def readCsv(fileName):
  return pd.read_csv(fileName)


################## geoJson section ##################
city_neighborhood_mapping = {
  "Boston": "Neighborhood_ID",
  "SanFrancisco": "nhood",
  "NewYork": "ntaname",
}

def addLatLonGeometry(df):
  df.loc[:, 'lon'] = df.geometry.centroid.x
  df.loc[:, 'lat'] = df.geometry.centroid.y
  return df


def readGeoFile(fileName):
  geoJson = gpd.read_file(fileName)
  return addLatLonGeometry(geoJson)
  # return gpd.read_file(fileName)


# geo json chart
def showGraphChart(geoDf, labelName='nhood'):
  # chart object
  graph1 = alt.Chart(geoDf).mark_geoshape(
    fill='lightgray',
  stroke='white'
  ).encode(
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
  return graph1

################## city level section ##################
# lines for covid
covidLine = alt.Chart(pd.DataFrame({'x': ['2020']})).mark_rule(color='purple').encode(x='x:T')
postCovidLine = alt.Chart(pd.DataFrame({'x': ['2021']})).mark_rule(color='orange').encode(x='x:T')

# text for pandemic
prepandemicText = alt.Chart(pd.DataFrame({'x': ['2019-01'], 'y': ['5250']})).mark_text(text='Pre-pandemic').encode(x='x:T', y='y:Q')
pandemicText = alt.Chart(pd.DataFrame({'x': ['2020-07'], 'y': ['5250']})).mark_text(text='Pandemic').encode(x='x:T', y='y:Q')
postpandemicText = alt.Chart(pd.DataFrame({'x': ['2021-08'], 'y': ['5250']})).mark_text(text='Post-pandemic').encode(x='x:T', y='y:Q')


def getCovidMarkings():
  return covidLine + postCovidLine

def getCovidText():
  return prepandemicText + pandemicText + postpandemicText


def showGeneralNeighborhoodChart(df):
  mostExNeighborhoods = getTopNeighborhoods(df, 5)
  cheapestNeighborhoods = getBottomNeighborhoods(df, 5)

  topNeighborsChart = alt.Chart(df).mark_line().encode(
    x=alt.X('Date:T'),
    y=alt.Y('Prices:Q', scale=alt.Scale(zero=False)),
    color=alt.Color('Neighborhood'),
    tooltip=['Neighborhood', 'Prices']
  ).transform_filter(
      alt.FieldOneOfPredicate(field='Neighborhood', oneOf=cheapestNeighborhoods + mostExNeighborhoods)
  ).properties(
      width=600, height=300,
      title='Top 5 most expensive and cheapest neighborhooods for rents'
  )

  st.altair_chart(topNeighborsChart + getCovidMarkings() + getCovidText())

def showGeneralNeighborhoodPriceChart(df):
  barChart = alt.Chart(df).mark_bar().encode(
    alt.X("Date:T"),
    alt.Y("MeanPriceChange:Q", axis=alt.Axis(format='.0%')),
    color=alt.condition(
        alt.datum.MeanPriceChange > 0,
        alt.value("red"),  # The positive color
        alt.value("green")  # The negative color
    )
  ).properties(width=600).interactive()
  st.altair_chart(barChart + getCovidMarkings())


################## neighborhood level section ##################

# filter df by neighborhood
def filterByNeighborhood(df, neighborhood):
  return df[df['Neighborhood'] == neighborhood]



def getTopNeighborhoods(df, num):
  return df.drop_duplicates(subset=['MeanPrices']).nlargest(num, ['MeanPrices'])['Neighborhood'].tolist()


def getBottomNeighborhoods(df, num):
  return df.drop_duplicates(subset=['MeanPrices']).nsmallest(num, ['MeanPrices'])['Neighborhood'].tolist()


################## general functions section to call other graphs ##################
def visualizeCity(city):
  st.write('showing city:', city)
  # load geojson data from city
  geoFileName = f"GeojsonData/{city}Neighborhoods.geojson"
  # geoFileName = f"ShpData/{city}Neighborhoods.shp"
  geoData = readGeoFile(geoFileName)
  st.write(geoData.sample(5))

  geoData.plot("nhood", figsize = (20, 10)) # legend=True,
  for _, row in geoData.iterrows():
    plt.text(s=row['nhood'], x = row['lon'], y = row['lat'],
           horizontalalignment='center', fontdict = {'size': 10}) # 'weight': 'bold', 

    # plt.text(s='Data: ' + f'{hue:,}', x=row['coords'][0],y = row['coords'][1] - 0.01 ,
    #       horizontalalignment='center', fontdict = {'size': 8})
  st.labels = False
  st.pyplot()

  df = pd.DataFrame(geoData, columns=['lat', 'lon'])
  st.map(df)

  # st.write(geoData.head())
  # st.altair_chart(showGraphChart(geoData, city_neighborhood_mapping[city]))
  # st.write('ab')


def visualizeCityBedroomType(city, bedroom):
  df = readCsv(f"data/{city}/{bedroom}Rental")
  showGeneralNeighborhoodChart(df)
  # TODO: add this to data preprocessing column
  df['Price_change'] = df['Prices'].pct_change()
  df['MeanPriceChange'] = df.groupby('Date')['Price_change'].transform('mean')
  showGeneralNeighborhoodPriceChart(df)


# function to load all the data and interactions
def loadNeighborhoodData():
  citySelection = st.selectbox("Which city would you like to see?", top10cities)
  citySelection = citySelection.replace(' ', '')
  # visualizeCity(citySelection)

  st.subheader("General City Bedroom type visualizations")
  bedroomSelection = st.selectbox("Which bedroom type would you like to see?", bedroomTypes.keys())
  visualizeCityBedroomType(citySelection, bedroomTypes[bedroomSelection])

  st.subheader("Specific neighborhood visualizations")
  
