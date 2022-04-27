import streamlit as st
import altair as alt
import json
import pandas as pd
import plotly
import plotly.express as px
import geojson

from urllib.request import urlopen

def addLatLonGeometry(df):
  df.loc[:, 'lon'] = df.geometry.centroid.x
  df.loc[:, 'lat'] = df.geometry.centroid.y
  return df


# def readGeoFile(fileName):
#   geoJson = gpd.read_file(fileName)
#   return addLatLonGeometry(geoJson)


def drawGeoGraph(city):
  st.write(city)

  # url json file (not working...)
  # url_geojson = "https://data.sfgov.org/api/views/6ia5-2f8k/rows.json"
  # url_geojson = "https://data.sfgov.org/resource/6ia5-2f8k.json"
  # geoData = alt.Data(url=url_geojson, format=alt.DataFormat(property='data', type='json'))

  # with urlopen("https://data.sfgov.org/resource/6ia5-2f8k.json") as response:
  #   counties = json.load(response)

  # fig = px.choropleth(df, geojson=counties, locations='fip', color=condition_selection,
  #   color_continuous_scale='fall',
  #   range_color=(1, 133),
  #   scope='usa',
  #   hover_name='counties',
  #   labels={'counties':'County Name:'}
  # )

  geoFileName = f"GeojsonData/{city}Neighborhoods.geojson"
  # geoFileName = "https://github.com/CMU-IDS-2022/final-project-champion/blob/main/GeojsonData/SanFranciscoNeighborhoods.geojson"
  # geoFileName = f"ShpData/{city}Neighborhoods.shp"
  # geoData = readGeoFile(geoFileName)

  with open(geoFileName) as f:
    gj = geojson.load(f)
  # geoData = geojson.load(geoFileName)
  
  neighborhoods = []
  for row in gj['features']:
    neighborhoods.append(row['properties']['nhood'])
  st.write(neighborhoods)

  df2 = pd.DataFrame(neighborhoods, columns = ['Neighborhood'])
  
  st.write(len(neighborhoods))

  # geoData.plot("nhood", figsize = (20, 10)) # legend=True,
  # for _, row in geoData.iterrows():
  #   plt.text(s=row['nhood'], x = row['lon'], y = row['lat'],
  #          horizontalalignment='center', fontdict = {'size': 10}) # 'weight': 'bold', 

  #   # plt.text(s='Data: ' + f'{hue:,}', x=row['coords'][0],y = row['coords'][1] - 0.01 ,
  #   #       horizontalalignment='center', fontdict = {'size': 8})
  # st.labels = False
  # st.pyplot()

  # df = pd.DataFrame(geoData, columns=['lat', 'lon'])
  # st.map(df)

  df1 = pd.read_csv(f'data/{city}/1brRental')
  # neighborhoods = findNeighborhoods(sfHousingData)
  st.write(len(set(df1['Neighborhood'])))
  st.write(df1['Neighborhood'])

  st.write(sorted(set(df1['Neighborhood']).difference(set(neighborhoods))))
  st.write(sorted(set(neighborhoods).difference(set(df1['Neighborhood']))))


  # with urlopen('https://github.com/CMU-IDS-2022/final-project-champion/blob/main/GeojsonData/SanFranciscoNeighborhoods.geojson') as response:
  #   counties = json.load(response)

  fig = px.choropleth(
    df1,
    geojson=gj, 
    locations='Neighborhood',
    featureidkey="properties.nhood",
    scope='usa',
    # color=condition_selection,
    # color_continuous_scale='fall',
    # range_color=(1, 133),
    hover_name='Neighborhood',
    # labels={'counties':'County Name:'}
  )
  fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0})
  fig.update_geos(fitbounds='locations', visible=True)
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