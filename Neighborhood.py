import streamlit as st
import altair as alt
import pprint
import pandas as pd
import json
import pyproj
import numpy as np
import matplotlib.pyplot as plt

import NeighborhoodOthers
import DrawGeoGraph

from vega_datasets import data
from altair import datum
from collections import defaultdict
from wordcloud import WordCloud
from PIL import Image

alt.data_transformers.enable('default', max_rows=None)

top10cities = set(["Boston", "Chicago", "Detroit", "Los Angeles", "New York", "Philadelphia", "Pittsburgh", "San Francisco", "Seattle", "Washington"])

bedroomTypes = {"1 bedroom": "1br", "2 bedrooms" : "2br", "3 bedrooms" :"3br", "4 bedrooms" : "4br", "5 bedrooms" : "5br", "Condominium" : "condo"}

pandemicYearData = ["All data from 2018 to 2022", "Pre-pandemic", "Pandemic", "Post-pandemic"]

def readCsv(fileName):
  return pd.read_csv(fileName)


################## geoJson section ##################

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


def showGeneralNeighborhoodChart(df, value, cost, topNeighborsChart):
  cheapestNeighborhoods = getBottomNeighborhoods(df, value)
  mostExNeighborhoods = getTopNeighborhoods(df, value)

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

  if cost == 'Cheapest':
    st.altair_chart((topCheapNeighborhoods + getCovidMarkings() + getCovidText(lowest)).properties(width=800, height=450))

  elif cost == 'Most expensive':
    st.altair_chart((topExNeighborhoods + getCovidMarkings() + getCovidText(highest)).properties(width=800, height=450))

  else:
    finalNeighborsChart = (topExNeighborhoods + getCovidMarkings() + getCovidText(highest)) | (topCheapNeighborhoods + getCovidMarkings() + getCovidText(lowest))
    st.altair_chart(finalNeighborsChart)

def showGeneralNeighborhoodPriceChart(df, city):

  brush = alt.selection(type='interval', encodings=['x'])

  barChart = alt.Chart(df).mark_bar().encode(
    x=alt.X("Date:T", title='Date (Jan 2018 to Mar 2022)'),
    y=alt.Y("MeanPriceChange:Q", axis=alt.Axis(format='.0%', title='Average Price Changes (%)')),
    color=alt.condition(
        alt.datum.MeanPriceChange > 0,
        alt.value("red"),  # The positive color
        alt.value("green")  # The negative color
    )
  ).properties(
    title=f"Average price changes for {city} month by month"
  ).add_selection(brush)
  # .interactive() # width=600

  # st.write(df)
  lineChart = alt.Chart(df).mark_line().encode(
    x=alt.X("Date:T", title='Date (Jan 2018 to Mar 2022)', scale=alt.Scale(domain=brush)),
    y=alt.Y("TotalMeanPrices:Q", axis=alt.Axis(title='Average Price ($)'), scale=alt.Scale(zero=False)), # format='$', labelFlush=False,
    # color = "Neighborhood",
  ).properties(
    title=f"Average price for {city} from 2018 to March 2022"
  )
  # .interactive() # width=600

  # the band across lines are too huge to show any difference
  # band = alt.Chart(df).mark_area(
  #   opacity=0.5, color='gray'
  # ).encode(
  #   x=alt.X("Date:T"),
  #   y=alt.Y("min(MeanPrices):Q", scale=alt.Scale(zero=False)),
  #   y2="max(MeanPrices):Q",
  # )

  interactData = st.checkbox("Select area to zoom in price graph")
  if interactData:
    st.altair_chart(barChart.add_selection(brush) + getCovidMarkings() + getCovidText(0.025) | lineChart)
  else:
    st.altair_chart(barChart.add_selection(brush) + getCovidMarkings() + getCovidText(0.025) | getCovidMarkings() + lineChart)

  # st.altair_chart(barChart.add_selection(brush)
  #   + getCovidMarkings() | 
  #   lineChart + getCovidMarkings())


  # st.altair_chart(barChart + getCovidMarkings() | lineChart + getCovidMarkings() )


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
  # TODO: add this to data preprocessing column
  # first graph chart
  df['PriceChange'] = df.groupby('Neighborhood')['Prices'].pct_change()
  
  df['MeanPriceChange'] = df.groupby('Date')['PriceChange'].transform(np.mean)
  df['TotalMeanPrices'] = df.groupby('Date')['Prices'].transform(np.mean)
  # st.write(df)
  showGeneralNeighborhoodPriceChart(df, city)
  return df

def visualizeTopCitiesGraph(df):
  legendSelection = alt.selection_multi(fields=['Neighborhood'], bind='legend')

  # second graph chart
  topNeighborsChart = alt.Chart(df).mark_line().encode(
    x=alt.X('Date:T'),
    y=alt.Y('Prices:Q', scale=alt.Scale(zero=False)),
    color=alt.Color('Neighborhood'),
    tooltip=['Neighborhood', 'Prices'],
    opacity=alt.condition(legendSelection, alt.value(1), alt.value(0.2))
  ).add_selection(legendSelection)

  col1, col2 = st.columns(2)
  with col1:
    sliderValue = st.slider("Select the number of neighborhoods to view", 1, len(pd.unique(df['Neighborhood'])), 10)

  with col2:
    cost = st.radio("Show top xx neighborhoods",
      ("Cheapest", "Most expensive", "Both cheapest and most expensive"))

  showGeneralNeighborhoodChart(df, sliderValue, cost, topNeighborsChart)


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
      width=800, height=450,
      title='General price trend for rents'
  )
  # height = df
  # TODO: add neighborhood names for world cloud
    # check if it is possible to show world cloud for a specific neighborhood
  # TODO: add world map graph
  st.altair_chart(line + getCovidMarkings() + getCovidText(4750))

def visualizeWordTrend(df, mask):
  # st.write(df)

  freq = {}
  for column in df.columns[2:]:
    freq[column] = df[column].iloc[-1]
  # st.write(freq)
  wc = WordCloud(mask=mask, background_color="white", contour_width=3, contour_color='steelblue')
  wordcloud = wc.generate_from_frequencies(freq)
  # Generate plot
  plt.figure()
  plt.imshow(wordcloud, interpolation="bilinear")
  plt.axis("off")
  st.pyplot(plt)

  # show graph of all counts --> not useful at the moment cos there are too many
  # neighborhoods = list(df.columns[2:])
  # # st.write(neighborhoods)
  # lineChart = alt.Chart(df).transform_fold(neighborhoods
  #   ).mark_line().encode(
  #   x=alt.X("date:T", title='Date (Jan 2018 to Mar 2022)', scale=alt.Scale(zero=False)),
  #   y='value:Q',#alt.Y("TotalMeanPrices:Q", axis=alt.Axis(title='Average Price ($)'), scale=alt.Scale(zero=False)), # format='$', labelFlush=False,
  #   color = "key:N",
  # ).properties(
  #   title=f"Searches of neighborhoods on Google from 2018 to March 2022"
  # )
  # st.altair_chart(lineChart)

################## Specific functions section to call other graphs ##################
def loadNeighborhoodData():

  col1, col2, col3 = st.columns(3)
  with col1:
    metric_selection = st.radio(
      'View Metric',
      ('Rental Price','Others')
    )
  with col2:
    citySelection = st.selectbox("Which city would you like to see?", top10cities, index=list(top10cities).index('San Francisco'))
  
  with col3:
    bedroomSelection = st.selectbox(
      'Wich bedroom type would you like to see?', bedroomTypes.keys()
    )
    

  if metric_selection == 'Rental Price':
    trimmedCitySelection = citySelection.replace(' ', '')

    # bedroomCol, yearCol = st.columns(2)
    # with bedroomCol:
    #   bedroomSelection = st.selectbox("Which bedroom type would you like to see?", bedroomTypes)
    # with yearCol:
    #   yearTypeSelection = st.selectbox("What type of data year data would you like to see?", pandemicYearData)

    # visualizeCity(trimmedCitySelection)
    DrawGeoGraph.drawGeoGraph(trimmedCitySelection, bedroomSelection)

    st.subheader(f"City level visualizations in {citySelection} based on {bedroomSelection}")
    df = visualizeCityBedroomType(trimmedCitySelection, bedroomTypes[bedroomSelection])
    visualizeTopCitiesGraph(df)

    # show neighborhoods
    # st.write(set(df['Neighborhood']))

    st.subheader("Specific neighborhood visualizations")
    neighborhoodSelections = st.multiselect("Which neighborhood would you like to find out more?", set(df['Neighborhood']))
    # st.write(neighborhoodSelections)
    visualizeCityBedroomNeighborhood(df, neighborhoodSelections)

    if trimmedCitySelection == 'SanFrancisco':
      st.subheader("Running out of ideas? Find out popular neighborhood based on Google trends")

      word_trend_df = pd.read_csv(f"data/{trimmedCitySelection}/googleTrends.csv")
      mask = np.array(Image.open(f"data/generalMask.jpeg"))
      # mask = np.array(Image.open(f"data/{trimmedCitySelection}/map.png"))
      visualizeWordTrend(word_trend_df, mask)


  elif metric_selection == 'Others':
    NeighborhoodOthers.loadOthersNeighborhoodData(trimmedCitySelection)

