from multiprocessing.spawn import import_main_path
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
# !pip install geocoder
import geocoder
from vega_datasets import data




# =========================== Part 0 =============================== 
# data preprocessing
# for speed issue, we will store preprocessed data and import them for visualization
# we can check the data processing code in this link:
# we use Zillow Research Data to convert housing and rental data for US cities and neighborhoods.



# Read data
def load_dateset(url, encode="utf-8"):
    return pd.read_csv(url, encoding=encode)

url_city_statistics = "https://raw.githubusercontent.com/CMU-IDS-2022/final-project-champion/main/data/top10_cities_statistics.csv"
url_city_rental_price="https://raw.githubusercontent.com/CMU-IDS-2022/final-project-champion/main/data/top10_cities_rental_price.csv"

top10_stats = load_dateset(url_city_statistics)
top10_rental = load_dateset(url_city_rental_price)

# we can get any city's coordinate by using MS Bing geocoder API, but in here API key is muted
# therefore we will import pre-process city's coordinates insteam of below code
# you can get top ten citie's coordinate(lat, lng)

# cities = top10_stats['City'].unique()
# lats = [0] * len(cities)
# lngs = [0] * len(cities)
# for idx, city in enumerate(cities):
#     if city=="Washington":
#         city="Washington D.C."
#     # because of privacy issue, API is muted
#     g=geocoder.bing(city, key='Right Down Your API Key')
#     results = g.json
#     lats[idx]=results['lat']
#     lngs[idx]=results['lng']
# city_coords = pd.DataFrame(cities)
# city_coords['latitude']=lats
# city_coords['longitude']=lngs
# city_coords.rename(columns={0:'City'},inplace=True)
# city_coords.to_csv("./city_coordinates.csv",index=None)

url_city_coords = "https://raw.githubusercontent.com/CMU-IDS-2022/final-project-champion/main/data/city_coordinates.csv"
city_coords=load_dateset(url_city_coords)

# download states, and cities information to visualize
states = alt.topo_feature(data.us_10m.url, 'states')
cities = alt.topo_feature(data.us_10m.url, 'cities')

# generate top 10 city rental sum dataset for visualization
top10_rental['Year']=top10_rental['date'].apply(lambda x:x[:4])
temp=top10_rental.groupby(by=['City','Year','roomtype'],as_index=False)['rental_price'].mean()
top10_rental_sum=pd.merge(temp, city_coords, how="inner",on="City")
top10_rental_sum.rename(columns={"roomtype":"Room Type","rental_price":"RentalPrice"},inplace=True)
top10_rental_sum['Year']=top10_rental_sum['Year'].astype('int64')
top10_rental_sum['RentalPrice']=np.round(top10_rental_sum['RentalPrice'])
top10_rental_sum=top10_rental_sum[['City','Year','Room Type', 'RentalPrice','latitude','longitude']]
# generate top 10 city crime statistics dataset for visualization
temp = pd.merge(left=top10_stats[top10_stats['Year']>=2018], right=city_coords, how='inner', on='City')
# temp['Murder']=temp['Murder'].astype('float64')
temp.rename(columns={'Median Income':'MedianIncome'}, inplace=True)
temp['Crime Score'] = np.round(temp['Violent']/temp['Violent'].mean()+\
                        temp['Murder']/temp['Murder'].mean()+\
                        temp['Rape']/temp['Rape'].mean()+\
                        temp['Robbery']/temp['Property'].mean()+\
                        temp['Assault']/temp['Assault'].mean(),2)
top10_stats_final = temp[['City','latitude','longitude','Year','MedianIncome','Crime Score',\
                            'Violent','Murder','Rape','Robbery','Assault','Property','Burglary','Larceny','Auto']]

temp = top10_stats_final[['City','Year','Violent','Murder','Rape','Robbery','Assault']]
top10_crime_stats_graph=temp.melt(id_vars=['City','Year'], value_vars=['Violent','Murder','Rape','Robbery','Assault'],var_name="CrimeType", value_name='Rate',ignore_index=True)

def period_for_pandemic(x):
    if x<2020:
        return 'Pre-Pandemic'
    elif x>2020:
        return "Post-Pandemic"
    else:
        return "Pandemic"

top10_rental_graph=top10_rental.rename(columns={'roomtype':'RoomType','rental_price':'RentalPrice'})
top10_rental_graph['Year']=top10_rental_graph['date'].apply(lambda x:x[:4])
top10_rental_graph['Year']=top10_rental_graph['Year'].astype('int64')
top10_rental_graph['Month']=top10_rental_graph['date'].apply(lambda x:x[5:])
top10_rental_graph['Period']=top10_rental_graph['Year'].apply(lambda x:period_for_pandemic(int(x)))



# =========================== Part 1 =============================== 
# visualization streamlit page configuration
st.set_page_config(
    page_title = "The favorable city to work after CMU graduation",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=None,
    
)

st.title("Find Your Next Destination after CMU")


# =========================== Part 2 =============================== 
# visualization for national wide view
# side bar
st.sidebar.header("Select View Level")
page_selection = st.sidebar.radio(
    'View Level',
    ('US National Wide', 'City Wide')
)

# Visualization Dashboard
if page_selection == "US National Wide":
    st.subheader("Select Metrics to view")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_selection = st.radio(
        'View Metric',
        ('Rental Price','Crime')
        )
    with col2:
        year_list = list(top10_rental_sum['Year'].unique())
        year_selection = st.selectbox(
        'Year', year_list,
        index=4
        )
    
    
    # median income for all cities
    df = top10_stats_final[top10_stats_final['Year']==year_selection]
    bars=alt.Chart(df).mark_bar().encode(
        # y=alt.Y("City", sort='-x',axis=alt.Axis(ticks=False, domain=False,offset=5,title=None,labelFontStyle='bold')),
        y=alt.Y("City",sort='-x',axis=None),
        x=alt.X("MedianIncome",axis=None),
        color=alt.Color("City", sort='x',
                        scale=alt.Scale(scheme='greenblue'),
                        legend=None),   
    ).transform_window(
        rank='rank()',
        sort=[alt.SortField("MedianIncome", order='descending')]
    # ).transform_filter(
        # alt.datum.rank<=5
    ).properties(
        width=200,
        height=350
    )
    text_city=bars.mark_text(
        align='left',
        baseline='middle',
        fontStyle='bold',
        # color='black',
        dx=5
    ).encode(
        text='City',
        color=alt.Color()
    )
    text_num = bars.mark_text(
        align='right',
        baseline='middle',
        fontStyle='bold',
        color='white',
        dx=-5,
    ).encode(
        # x=alt.value(5),
        # text='RentalPrice',
        text='label:N',
        color=alt.Color()
    ).transform_calculate(label=f'format(datum.MedianIncome,"$,")')
    
    graph_medianincome=bars+text_city+text_num
    
    if metric_selection=="Rental Price":
        with col3:
            roomtypes = list(top10_rental_sum['Room Type'].unique())
            roomtype_selection = st.selectbox(
                'Room Type', roomtypes
            )
        st.subheader("US City Average Rental Price of "+roomtype_selection+" at "+str(year_selection))
        city_selection = alt.selection_single(nearest=True, fields=['City'], empty='all')
        df = top10_rental_sum[(top10_rental_sum['Room Type']==roomtype_selection) & (top10_rental_sum['Year']==year_selection)]
        background = alt.Chart(states).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).project('albersUsa')
        # background
        cities = alt.Chart(df).encode(
            longitude='longitude:Q',
            latitude='latitude:Q',   
        )
        text = cities.mark_text(dx=0,dy=20, align='center').encode(
            alt.Text('City', type='nominal'),
            # opacity=alt.condition(~hover, alt.value(0), alt.value(1))
        )
        point = cities.mark_point(filled=True).encode(
            size=alt.Size('RentalPrice:Q',
                        scale=alt.Scale(range=[0,1000]),
                        legend=None
                        ),
            # size=alt.Size(10),
            color=alt.condition(city_selection,'RentalPrice:Q',alt.value('gray'),type="quantitative",
                            scale=alt.Scale(scheme='yelloworangered',),
                            legend=None),
            tooltip=[
            'City',
            'Year',
            'Room Type',
            alt.Tooltip('RentalPrice:Q',format='$,d')
            ],
                            
        ).add_selection(
            city_selection
        )
        graph_rentalprice=(background+point+text).properties(
            width=550,
            height=350,
            )
        # show Map + median income graph
        st.write(graph_rentalprice | graph_medianincome)
        
        
        
    elif metric_selection=="Crime":
        st.subheader("US City Average Crime Score at "+str(year_selection))
        # US states background
        city_selection = alt.selection_single(nearest=True)
        df = top10_stats_final[top10_stats_final['Year']==year_selection]
        background = alt.Chart(states).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).properties(
            width=600,
            height=350,
        ).project('albersUsa')
        # background
        cities = alt.Chart(df).encode(
            longitude='longitude:Q',
            latitude='latitude:Q',   
        )
        text = cities.mark_text(dx=0,dy=20, align='center').encode(
            alt.Text('City', type='nominal'),
            # opacity=alt.condition(~hover, alt.value(0), alt.value(1))
        )
        point = cities.mark_point(filled=True).encode(
            tooltip=[
            'City',
            'Year',
            alt.Tooltip('Crime Score:Q',format='.1f')
            ],
            size=alt.Size('Crime Score',type="quantitative",
                        scale=alt.Scale(range=[0,1000]),
                        legend=None),
            # size=alt.Size(10),
            color=alt.condition(city_selection,'Crime Score',alt.value('gray'),
                            scale=alt.Scale(scheme='yelloworangered',),
                            legend=None), 
        ).add_selection(
            city_selection
        )
        graph_crime = background+point+text
        st.write(graph_crime | graph_medianincome)
        
        
        
    # show selected city's room type graph
    city_list = list(top10_rental_sum['City'].unique())
    city_selection = st.selectbox(
    'City', city_list,
    index=len(city_list)-4
    )
    
    st.text(city_selection)
    
    
    df = top10_rental_graph[(top10_rental_graph['City']==city_selection)&(top10_rental_graph['Year']==year_selection)]
    main=alt.Chart(df).mark_bar().encode(
        x=alt.X("RoomType:O", sort='y',axis=alt.Axis(ticks=False, domain=False,
                                                     labelAngle=-45,
                                                     offset=5,title=None,labelFontStyle='bold')),
        # y=alt.Y("CrimeType:N",sort='-x',axis=alt.Axis(title=None,)),
        y=alt.Y("mean(RentalPrice)",axis=None),
        color=alt.Color("mean(RentalPrice):Q", sort='y',
                        scale=alt.Scale(scheme='goldred'),
                        legend=None),   
    )
    bars=main
    text_num = main.mark_text(
        align='center',
        baseline='middle',
        fontStyle='bold',
        color='black',
        dy=10,
    ).encode(
        # x=alt.value(5),
        # text='RentalPrice',
        text=alt.Text('mean(RentalPrice):Q',format='$,d'),
        color=alt.Color()
    )
    graph_rentalprice_detail=(bars+text_num).properties(
        width=350,
        height=280,
    )
    # draw crime detail
    df = top10_crime_stats_graph[(top10_crime_stats_graph['City']==city_selection)&(top10_crime_stats_graph['Year']==year_selection)]
    bars=alt.Chart(df).mark_bar().encode(
        x=alt.X("CrimeType:N", sort='y',axis=alt.Axis(ticks=False, labelAngle=0, domain=False,offset=0,title=None,labelFontStyle='bold')),
        # y=alt.Y("CrimeType:N",sort='-x',axis=alt.Axis(title=None,)),
        y=alt.Y("Rate",axis=None),
        color=alt.Color("Rate:Q", sort='y',
                        scale=alt.Scale(scheme='goldred'),
                        legend=None),   
    ).properties(
        width=250,
        height=200,
    ).add_selection(
        # city_selection, year_selection
    )
    text_num = bars.mark_text(
        align='center',
        baseline='middle',
        fontStyle='bold',
        color='black',
        dy=-5,
    ).encode(
        # x=alt.value(5),
        # text='RentalPrice',
        text='label:N',
        color=alt.Color()
    ).transform_calculate(label=f'format(datum.Rate,"d")')
    graph_crime_detail = bars+text_num
    colgraph1, colgraph2 = st.columns(2)
    with colgraph1:
        st.write(graph_rentalprice_detail)
    with colgraph2:
        st.write(graph_crime_detail)
    
    
    
    city = 'New York'
    room = '4beds'
    df=top10_rental_graph[(top10_rental_graph['City']==city) & (top10_rental_graph['RoomType']==room)]

    period_list = list(top10_rental_graph['Period'].unique())
    input_dropdown = alt.binding_select(options=period_list)
    selection = alt.selection_single(fields=['Period'],bind=input_dropdown, name='Pandemic')

    graph_trend=alt.Chart(df).mark_line(
        point={
            "filled":False,
            "fill":"white"
            }).encode(
        x=alt.X('Month',scale=alt.Scale(zero=False),axis=alt.Axis(title=None, labelAngle=0, labelFontStyle='bold')),
        y=alt.Y('RentalPrice',scale=alt.Scale(zero=False),axis=alt.Axis(title=None, grid=False, labelFontStyle='bold')),
        color=alt.condition(selection, alt.Color('Year:N',legend=None),alt.value('lightgray')),
        tooltip=[
            'City',
            'Year',
            'Month',
            'RoomType',
            alt.Tooltip('RentalPrice:Q',format='$,d')
            ]
        # emphosize pandemic
    ).add_selection(
        selection
    ).properties(
        width=400,
        height=150,
        title="Average Price of "+room+" at " +city
    )
    st.write(graph_trend)
# draw neighborhood level data
elif page_selection == "City Wide":
    st.write("ABCD")        
        
    
    