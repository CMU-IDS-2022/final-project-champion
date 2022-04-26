import streamlit as st
import altair as alt
import pprint
import pandas as pd
import json
import geopandas as gpd
import pyproj
import numpy as np
import matplotlib.pyplot as plt
import NeighborhoodOthers

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
def getPrepandemicText(height):
  return alt.Chart(pd.DataFrame({'x': ['2019-01'], 'y': [height]})).mark_text(text='Pre-pandemic').encode(x='x:T', y='y:Q')

def getPandemicText(height):
  return alt.Chart(pd.DataFrame({'x': ['2020-07'], 'y': [height]})).mark_text(text='Pandemic').encode(x='x:T', y='y:Q')

def getPostpandemicText(height):
  return alt.Chart(pd.DataFrame({'x': ['2021-08'], 'y': [height]})).mark_text(text='Post-pandemic').encode(x='x:T', y='y:Q')


def getCovidMarkings():
  return covidLine + postCovidLine

def getCovidText(height):
  return getPrepandemicText(height) + getPandemicText(height) + getPostpandemicText(height)


def showGeneralNeighborhoodChart(df, value):
  mostExNeighborhoods = getTopNeighborhoods(df, value)
  cheapestNeighborhoods = getBottomNeighborhoods(df, value)

  topNeighborsChart = alt.Chart(df).mark_line().encode(
    x=alt.X('Date:T'),
    y=alt.Y('Prices:Q', scale=alt.Scale(zero=False)),
    color=alt.Color('Neighborhood'),
    tooltip=['Neighborhood', 'Prices']
  )

  topExNeighborhoods = topNeighborsChart.transform_filter(
      alt.FieldOneOfPredicate(field='Neighborhood', oneOf=mostExNeighborhoods)
  ).properties(
      title=f'Top {value} most expensive neighborhoods for rents'
  )

  topCheapNeighborhoods = topNeighborsChart.transform_filter(
      alt.FieldOneOfPredicate(field='Neighborhood', oneOf=cheapestNeighborhoods)
  ).properties(
      title=f'Top {value} cheapest neighborhoods for rents'
  )
  # st.write(df)
  highest = max(df['Prices']) * 1.05
  lowest = min(df['Prices']) * 1.9

  finalNeighborsChart = (topExNeighborhoods + getCovidMarkings() + getCovidText(highest)) | (topCheapNeighborhoods + getCovidMarkings() + getCovidText(lowest))

  st.altair_chart(finalNeighborsChart)

def showGeneralNeighborhoodPriceChart(df):
  barChart = alt.Chart(df).mark_bar().encode(
    alt.X("Date:T"),
    alt.Y("MeanPriceChange:Q", axis=alt.Axis(format='.0%')),
    color=alt.condition(
        alt.datum.MeanPriceChange > 0,
        alt.value("red"),  # The positive color
        alt.value("green")  # The negative color
    )
  ).properties().interactive() # width=600

  # st.write(df)
  lineChart = alt.Chart(df).mark_line().encode(
    alt.X("Date:T"),
    alt.Y("mean(MeanPrices):Q", scale=alt.Scale(zero=False)),
    # color = "Neighborhood",
  ).properties().interactive() # width=600

  # the band across lines are too huge to show any difference
  # band = alt.Chart(df).mark_area(
  #   opacity=0.5, color='gray'
  # ).encode(
  #   x=alt.X("Date:T"),
  #   y=alt.Y("min(MeanPrices):Q", scale=alt.Scale(zero=False)),
  #   y2="max(MeanPrices):Q",
  # )

  st.altair_chart(barChart + getCovidMarkings() | lineChart + getCovidMarkings() )


################## neighborhood level section ##################

# filter df by neighborhood
def filterByNeighborhood(df, neighborhood):
  return df[df['Neighborhood'] == neighborhood]

def filterByNeighborhoods(df, neighborhoods):
  return df[df['Neighborhood'].isin(neighborhoods)]

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
  value = st.slider("Select the number of properties to view", 1, len(pd.unique(df['Neighborhood'])), 5)
  # first graph chart
  showGeneralNeighborhoodChart(df, value)
  # TODO: add this to data preprocessing column
  # second graph chart
  df['PriceChange'] = df.groupby('Neighborhood')['Prices'].pct_change()
  df['MeanPriceChange'] = df.groupby('Date')['PriceChange'].transform(np.mean)
  # st.write(df)
  showGeneralNeighborhoodPriceChart(df)
  st.write("interesting trend where the housing rental prices in United States is always increasing.")
  return df


def visualizeCityBedroomNeighborhood(df, neighborhoods):
  # st.write(df)
  line = alt.Chart(df).mark_line(color='blue').encode(
    x="Date:T",
    y=alt.Y('Prices:Q', scale=alt.Scale(zero=False)),
    color='Neighborhood',
    # strokeDash='Neighborhood',
  ).transform_filter(
      alt.FieldOneOfPredicate(field='Neighborhood', oneOf=neighborhoods)
  ).properties(
      width=600, height=300,
      title='General price trend for rents'
  )
  # height = df

  st.altair_chart(line + getCovidMarkings() + getCovidText(4750))

################## Specific functions section to call other graphs ##################
def loadNeighborhoodData():

  citySelection = st.selectbox("Which city would you like to see?", top10cities)
  metric_selection = st.radio(
    'View Metric',
    ('Rental Price','Others')
  )

  if metric_selection == 'Rental Price':
    citySelection = citySelection.replace(' ', '')
    # visualizeCity(citySelection)

    st.subheader("General City Bedroom type visualizations")
    bedroomSelection = st.selectbox("Which bedroom type would you like to see?", bedroomTypes.keys())
    df = visualizeCityBedroomType(citySelection, bedroomTypes[bedroomSelection])

    st.subheader("Specific neighborhood visualizations")
    neighborhoodSelections = st.multiselect("Which neighborhood would you like to see?", set(df['Neighborhood']))
    # st.write(neighborhoodSelections)
    visualizeCityBedroomNeighborhood(df, neighborhoodSelections)

  elif metric_selection == 'Others':
    NeighborhoodOthers.loadOthersNeighborhoodData(citySelection)

