import streamlit as st
import altair as alt
import json
import pandas as pd
import plotly
import plotly.express as px
import geojson

from urllib.request import urlopen
import Neighborhood

def addLatLonGeometry(df):
  df.loc[:, 'lon'] = df.geometry.centroid.x
  df.loc[:, 'lat'] = df.geometry.centroid.y
  return df

city_neighborhood_mapping = {
  "Boston": "Neighborhood_ID",
  "SanFrancisco": "nhood",
  "NewYork": "ntaname",
  "Detroit": "name",
  "Chicago": "pri_neigh",
  "Philadelphia": "name",
  "LosAngeles": "name",
  "Pittsburgh": "hood",
  "Seattle": "S_HOOD",
  "Washington": "NBH_NAMES"
}

# def readGeoFile(fileName):
#   geoJson = gpd.read_file(fileName)
#   return addLatLonGeometry(geoJson)


def drawGeoGraph(city, bedroomSelection):
  # st.write(city)
  featureName = city_neighborhood_mapping.get(city, '')
  # st.write(featureName)

  geoFileName = f"GeojsonData/{city}Neighborhoods.geojson"

  with open(geoFileName) as f:
    geoJson = geojson.load(f)

  neighborhoods = []
  for row in geoJson['features']:
    neighborhoods.append(row['properties'][featureName])

  df2 = pd.DataFrame(neighborhoods, columns = ['Neighborhood'])
  
  # st.write(len(neighborhoods))

  # geoData.plot("nhood", figsize = (20, 10)) # legend=True,
  # for _, row in geoData.iterrows():
  #   plt.text(s=row['nhood'], x = row['lon'], y = row['lat'],
  #          horizontalalignment='center', fontdict = {'size': 10}) # 'weight': 'bold', 

  #   # plt.text(s='Data: ' + f'{hue:,}', x=row['coords'][0],y = row['coords'][1] - 0.01 ,
  #   #       horizontalalignment='center', fontdict = {'size': 8})
  # st.labels = False
  # st.pyplot()

  # st.write(neighborhoods)

  df1 = pd.read_csv(f'data/{city}/{Neighborhood.bedroomTypes[bedroomSelection]}Rental')
  # neighborhoods = findNeighborhoods(sfHousingData)
  # st.write(len(set(df1['Neighborhood'])))
  # st.write(df1['Neighborhood'])

  # code to check mappings

  # missingGeoListA = sorted(set(df1['Neighborhood']).difference(set(neighborhoods)))
  # missingGeoListB = sorted(set(neighborhoods).difference(set(df1['Neighborhood'])))
  # st.write('more important set:', missingGeoListA)
  # st.write('b set:', missingGeoListB)

  # st.map(pd.DataFrame(list(missingGeoListA) + list(missingGeoListB), columns=['Neighborhood']))


  # with urlopen('https://github.com/CMU-IDS-2022/final-project-champion/blob/main/GeojsonData/SanFranciscoNeighborhoods.geojson') as response:
  #   counties = json.load(response)

  # mapbox_style="carto-positron", zoom=9, # used for choropleth_mapbox
  df1 = df1[df1['Date'] == '2022-03']
  # st.write(df1)

  st.subheader(f'Price distribution for neighborhoods in {city} on March 2022')
  fig = px.choropleth(
    df1,
    geojson=geoJson, 
    locations='Neighborhood',
    featureidkey=f"properties.{featureName}",
    # scope='usa',
    projection='mercator',
    color='Prices',
    # color=condition_selection,
    # color_continuous_scale='fall',
    # range_color=(1, 133), # shows the limit of what to show based on the rent
    hover_name='Neighborhood',
    # hover_data=["Year"],
    labels={'Prices' : 'Rental cost'}
  )
  fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0})
  fig.update_geos(fitbounds='locations', visible=False)
  st.write(fig)

  # fig=px.choropleth(df1,
  #   geojson="https://github.com/CMU-IDS-2022/final-project-champion/blob/main/GeojsonData/SanFranciscoNeighborhoods.geojson",
  #   featureidkey='properties.nhood',   
  #   locations='Neighborhood',        #column in dataframe
  #   # animation_frame='Date',       #dataframe
  #   # color='Rape_Cases_Reported',  #dataframe
  #   # color_continuous_scale='Inferno',
  #   title='Rape cases across the states' ,  
  #   height=700
  # )
  # fig.update_geos(fitbounds="locations", visible=True)
  # fig.show()


  # graph = alt.Chart(geoData).mark_geoshape(
  # ).encode(
  #     color="data.name:N"
  # ).project(
  #     type='identity', reflectY=True
  # )
  # st.write(graph)

  # st.write(geoData)

  # url_geojson = "https://github.com/vega/vega-datasets/edit/master/data/us-10m.json"
  # geoData = alt.Data(url=url_geojson, format=alt.DataFormat(property='feature', type='json'))

  # graph = alt.Chart(geoData).mark_geoshape(
  # ).encode(
  #     color="properties.name:N"
  # ).project(
  #     type='identity', reflectY=True
  # )
  # st.write(graph)

  # st.altair_chart(showGraphChart(geoData, city_neighborhood_mapping[city]))


  # states = alt.topo_feature(data.us_10m.url, feature='states')

  # graph = alt.Chart(states).mark_geoshape(
  #     fill='lightgray',
  #     stroke='white'
  # ).project('albersUsa').properties(
  #     width=500,
  #     height=300
  # )
  # st.write(graph)