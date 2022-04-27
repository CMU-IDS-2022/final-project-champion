from multiprocessing.spawn import import_main_path

from colorama import Style
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
# !pip install geocoder
import geocoder
from vega_datasets import data

import Neighborhood



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
url_city_housing_price="https://raw.githubusercontent.com/CMU-IDS-2022/final-project-champion/main/data/top10_cities_housing_price.csv"
url_city_index="https://raw.githubusercontent.com/CMU-IDS-2022/final-project-champion/main/data/top10_cities_all_index.csv"

top10_stats = load_dateset(url_city_statistics)
top10_rental = load_dateset(url_city_rental_price)
top10_housing = load_dateset(url_city_housing_price)
top10_indices = load_dateset(url_city_index)


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
#     g=geocoder.bing(city, key='USE Your Bing Map API Key')
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

top10_alldata_graph = pd.merge(left=top10_housing,right=top10_indices,how="left", on=['City','date'])
top10_alldata_graph['housing_price_over_housing_index']=top10_alldata_graph['housing_price']/top10_alldata_graph['housing_p_index']

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
    ('Data Processing', 'US National Wide', 'City Wide')
)

# Data process and validate the assumption
if page_selection == "Data Processing":
    st.subheader("How to estimate rental price for each roomtype and neighborhood")
    st.markdown('''
    **HOME VALUES**  
    Zillow Home Value Index (ZHVI): A **smoothed, seasonally adjusted measure** of the typical home value and market changes across a given region and housing type. It reflects the typical value for homes in the 35th to 65th percentile range. The raw version of that mid-tier ZHVI time series is also available.  
    Zillow publishes top-tier ZHVI (\$, typical value for homes within the 65th to 95th percentile range for a given region) and bottom-tier ZHVI (\$, typical value for homes that fall within the 5th to 35th percentile range for a given region).  
    Zillow also publishes ZHVI for all single-family residences (\$, typical value for all single-family homes in a given region), for condo/coops (\$), for all homes with 1, 2, 3, 4 and 5+ bedrooms (\$), and the ZHVI per square foot (\$, typical value of all homes per square foot calculated by taking the estimated home value for each home in a given region and dividing it by the home’s square footage). Check out this overview of ZHVI and a deep-dive into its methodology.   

    Here’s a handy ZHVI User Guide for information about properly citing and making calculations with this metric.   
    '''
    )
    st.markdown(
        '''
        **HOME VALUES FORECASTS**

        The Zillow Home Value Forecast (ZHVF) is the month-ahead, quarter-ahead and year-ahead forecast of the Zillow Home Values Index (ZHVI).  
        ZHVF is created using the all homes, mid-tier cut of ZHVI and is available both raw and smoothed, seasonally adjusted.
        
        **RENTALS**

        Zillow Observed Rent Index (ZORI): A **smoothed measure** of the typical observed market rate rent across a given region.  
        ZORI is a repeat-rent index that is weighted to the rental housing stock to ensure representativeness across the entire market, not just those homes currently listed for-rent.  
        The index is dollar-denominated by computing the mean of listed rents that fall into the 40th to 60th percentile range for all homes and apartments in a given region, which is once again weighted to reflect the rental housing stock. Details available in ZORI methodology.
        
        **Our Approach**  
        We can gather the housing price's fluctuation but hard to archive historical changes of rent price over years. 
        So, we establish the housing price - rent price conversion rate based Zillow Value Index on Home Value and Rentals.
        The problem is rental price was made of the weighted average price of all list in specific period, but we want to show each period each type's rental price.  
        To do this, we calculate Rental Price Index for each housing type(1bed, 2bed, etc.) with weighted average housing price index(forecast, all home) and weighted average rental price index(all home).
        
        '''        
    )
    st.latex(r'''
             \widehat{\text{Rental Price}} = \text{House Price} * \frac{\text{Index}_{\text{rental}}}{\text{Index}_{\text{housing(fcst)}}}

             ''')
    show_data = st.checkbox("Show data validation process")
    if show_data:
        # show selected city's room type graph
        city_list = list(top10_rental_sum['City'].unique())
        city_selection = st.selectbox(
        'City', city_list,
        index=len(city_list)-3
        )

        ###################################################################
        shared_width=600
        big_height=400
        small_height=150

        ####################################################################
        highlight = alt.selection(type='single', on='mouseover',fields=['roomtype'], nearest=True)
        brush = alt.selection(type='interval', encodings=['x'])
        df=top10_alldata_graph[top10_alldata_graph['City']==city_selection]
        price_base=alt.Chart(df).encode(
            x=alt.X("date:T", axis=alt.Axis(title=None)),
            y=alt.Y("housing_price:Q",scale=alt.Scale(zero=False),axis=alt.Axis(title=None)),
            color=alt.condition(brush, alt.Color("roomtype:N"),alt.value("lightgray")) ,
            # color="roomtype:N"
        )
        price_points = price_base.mark_circle().encode(
            opacity=alt.value(0),
            tooltip=[
            'City',
            alt.Tooltip('yearmonth(date):T'),
            alt.Tooltip('roomtype',title="Room Type"),
            alt.Tooltip('housing_price:Q',format='$,d',title="Housing Price")
            ],
        ).properties(
            width=shared_width,
            height=big_height,
            title="Housing Price for each Room Type"
        ).add_selection(
            highlight,
            brush
        )

        price_lines = price_base.mark_line().encode(
            size=alt.condition(~highlight, alt.value(1), alt.value(3)),
            # color=alt.condition(brush, alt.Color("roomtype:N"),alt.value("lightgray"))
        ).transform_filter(brush)
        graph_housing_price=price_points+price_lines

        housing_index=alt.Chart(df).mark_line(
            strokeDash=[5, 5],
            point={
                "filled":True,
                "fill":"black",
                "size":20
                }
            ).encode(
            x=alt.X("date:T", axis=alt.Axis(title=None)),
            y=alt.Y("mean(housing_p_index):Q",scale=alt.Scale(zero=False),axis=alt.Axis(title=None)),
            color=alt.condition(brush,alt.value("black"),alt.value("lightgray")),
            tooltip=[
            'City',
            alt.Tooltip('yearmonth(date):T'),
            alt.Tooltip('housing_p_index:Q',format='.2f',title="Housing Price Index")
            ],
            
        ).properties(
            width=shared_width,
            height=small_height,
            title="Housing Price Index"
        ).transform_filter(brush)

        price_over_index_base=alt.Chart(df).encode(
            x=alt.X("date:T", axis=alt.Axis(title=None)),
            y=alt.Y("housing_price_over_housing_index:Q",scale=alt.Scale(zero=False),axis=alt.Axis(title=None)),
            # color=alt.condition(brush, alt.Color("roomtype:N"),alt.value("lightgray")) ,
            color=alt.Color("roomtype:N")
        ).transform_filter(brush)

        price_over_index_points = price_over_index_base.mark_circle().encode(
            opacity=alt.value(0),
            tooltip=[
            'City',
            alt.Tooltip('yearmonth(date):T'),
            alt.Tooltip('roomtype',title="Room Type"),
            alt.Tooltip('housing_price_over_housing_index:Q',format='.2f',title="Unit Housing Price")
            ],
        ).properties(
            width=shared_width,
            height=big_height,
            title="Housing unit Price for each Room Type"
        ).add_selection(
            highlight
        )

        price_over_index_lines = price_over_index_base.mark_line().encode(
            size=alt.condition(~highlight, alt.value(1), alt.value(3)),
        )
        graph_housing_unit_price=price_over_index_points+price_over_index_lines

        ##############################################


        highlight2 = alt.selection(type='single', on='mouseover',
                                fields=['roomtype'], nearest=True)
        brush2 = alt.selection(type='interval', encodings=['x'])
        city_selection = "San Francisco"
        price_over_index_base2=alt.Chart(df).encode(
            x=alt.X("date:T", axis=alt.Axis(title=None)),
            y=alt.Y("housing_price_over_housing_index:Q",scale=alt.Scale(zero=False),axis=alt.Axis(title=None)),
            color=alt.condition(brush2, alt.Color("roomtype:N"),alt.value("lightgray")) ,
            # color=alt.Color("roomtype:N")
        )

        price_over_index_points2 = price_over_index_base2.mark_circle().encode(
            opacity=alt.value(0),
            tooltip=[
            'City',
            alt.Tooltip('yearmonth(date):T'),
            alt.Tooltip('roomtype',title="Room Type"),
            alt.Tooltip('housing_price_over_housing_index:Q',format='.2f',title="Unit Housing Price")
            ],
        ).properties(
            width=shared_width,
            height=big_height,
            title="Housing unit Price for each Room Type-1"
        ).add_selection(
            highlight2,
            brush2
        )
        price_over_index_lines2 = price_over_index_base2.mark_line().encode(
            size=alt.condition(~highlight2, alt.value(1), alt.value(3)),
        ).transform_filter(brush2)
        graph_housing_unit_price2=price_over_index_points2+price_over_index_lines2

        rental_index=alt.Chart(df).mark_line(
            color="red",
            strokeDash=[5, 5],
            point={
                "filled":True,
                "fill":"red",
                "size":20
                }
            ).encode(
            x=alt.X("date:T", axis=alt.Axis(title=None)),
            y=alt.Y("mean(rental_p_index):Q",scale=alt.Scale(zero=False),axis=alt.Axis(title=None)),
            tooltip=[
            'City',
            alt.Tooltip('yearmonth(date):T'),
            alt.Tooltip('rental_p_index:Q',format='.2f',title="Rental Price Index")
            ],
        ).properties(
            width=shared_width,
            height=small_height,
            title="Rental Price Index"
        ).transform_filter(brush2)


        df2 = top10_rental[top10_rental['City']==city_selection]
        rental_base=alt.Chart(df2).encode(
            x=alt.X("date:T", axis=alt.Axis(title=None)),
            y=alt.Y("rental_price:Q",scale=alt.Scale(zero=False),axis=alt.Axis(title=None)),
            color=alt.Color("roomtype:N"),
        ).transform_filter(brush2)
        rental_points = rental_base.mark_circle().encode(
            opacity=alt.value(0),
            tooltip=[
            'City',
            alt.Tooltip('yearmonth(date):T'),
            alt.Tooltip('roomtype',title="Room Type"),
            alt.Tooltip('rental_price:Q',format='$,d',title="Rental Price")
            ],
        ).properties(
            width=shared_width,
            height=big_height,
            title="Rental Price for each Room Type"
        )

        rental_lines = rental_base.mark_line().encode(
            size=alt.condition(~highlight2, alt.value(1), alt.value(3))
        )
        graph_rental_price=rental_points+rental_lines
        graph_col1, graph_col2 = st.columns(2)
        with graph_col1:
            st.write(alt.vconcat(graph_housing_price, housing_index, graph_housing_unit_price))
        with graph_col2:
            st.write(alt.vconcat(graph_housing_unit_price2, rental_index, graph_rental_price))

        raw_data = st.checkbox("Show raw dataset")
        if raw_data:
        
            raw_col1, raw_col2 = st.columns(2)
            with raw_col1:
                st.write("Housing Price and Index Data")
                st.write(top10_alldata_graph)
            with raw_col2:
                st.write("Estimated Rental Price Data")
                st.write(top10_rental)
    
# Visualization Dashboard
elif page_selection == "US National Wide":
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
    index=len(city_list)-3
    )
    
    st.text("Add range selection for bottom two graph")
    
    # room trend type of city
    df = top10_rental[top10_rental['City']==city_selection]
    df.rename(columns={"date":"YearMonth","rental_price":"RentalPrice","roomtype":"RoomType"},inplace=True)
    lines = alt.Chart(df).mark_line(
        point={
            "filled":True,
            # "fill":"white",
            "size":20
            }
    ).encode(
        x=alt.X('YearMonth:T',
                axis=alt.Axis(title=None, grid=False)),
        y=alt.Y('RentalPrice:Q',
                scale=alt.Scale(zero=False),
                axis=alt.Axis(title=None, grid=False)),
        color=alt.Color('RoomType:O', scale=alt.Scale(scheme='tableau10'),
                        legend=alt.Legend( title=None)),
        tooltip=[
            'City',
            alt.Tooltip('yearmonth(YearMonth):O',title="YearMonth"),
            'RoomType',
            alt.Tooltip('RentalPrice:Q',format='$,d')    
        ]
    )
    pandemic_location=pd.DataFrame({
            'YearMonth':['2020-01','2021-01'],
            'Color':['red','orange'],
            'Text':['Pandemic Start','Pandemic End']
        })
    pandemic = alt.Chart(pandemic_location).mark_rule().encode(
            x=alt.X('yearmonth(YearMonth):T'),
            color=alt.Color('Color:N',scale=None)
        
    )
    text = pandemic.mark_text(
        dx=0,dy=-100, 
        align='center',
        fontStyle='bold',
        color='black').encode(
        alt.Text('Text:N',),
        color=alt.Color()
        # opacity=alt.condition(~hover, alt.value(0), alt.value(1))
    )

    graph = (lines+pandemic+text).properties(
        width=900,
        height=250
    )
    st.write(graph)
    
    df = top10_rental_graph[(top10_rental_graph['City']==city_selection)&(top10_rental_graph['Year']==year_selection)]
    main=alt.Chart(df).mark_bar().encode(
        x=alt.X("RoomType:O", axis=alt.Axis(ticks=False, domain=False,
                                                     labelAngle=-45,
                                                     offset=5,title=None,labelFontStyle='bold')),
        # y=alt.Y("CrimeType:N",sort='-x',axis=alt.Axis(title=None,)),
        y=alt.Y("mean(RentalPrice)",axis=None),
        color=alt.Color("mean(RentalPrice):Q", 
                        scale=alt.Scale(scheme='lightgreyteal'),
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
        y=alt.Y("mean(Rate):Q",axis=None),
        color=alt.Color("mean(Rate):Q", sort='y',
                        scale=alt.Scale(scheme='goldred'),
                        legend=None),   
    ).properties(
        width=300,
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
    
    
    
    # last line chart
    # if roomtype_selection not in roomtypes:
    #     rt_selection = '1bed'
    # else:
    #     rt_selection = roomtype_selection
    rt_selection = '1bed'
    df=top10_rental_graph[(top10_rental_graph['City']==city_selection) & (top10_rental_graph['RoomType']==rt_selection)]

    period_list = list(top10_rental_graph['Period'].unique())
    input_dropdown = alt.binding_select(options=period_list)
    pandemic_selection=st.radio(
        'Pandemic Period',
        ['Post-Pandemic','Pandemic','Pre-Pandemic']
        )
    st.write(pandemic_selection)
    graph_trend=alt.Chart(df).mark_line(
        point={
            "filled":False,
            "fill":"white"
            }).encode(
        x=alt.X('Month',scale=alt.Scale(zero=False),axis=alt.Axis(title=None, labelAngle=0, labelFontStyle='bold')),
        y=alt.Y('RentalPrice',scale=alt.Scale(zero=False),axis=alt.Axis(title=None, grid=False, labelFontStyle='bold')),
        # color=alt.condition(pandemic_selection, alt.Color('Period:O',legend=None),alt.value('lightgray')),
        tooltip=[
            'City',
            'Year',
            'Month',
            'RoomType',
            alt.Tooltip('RentalPrice:Q',format='$,d')
            ]
    ).properties(
        width=400,
        height=150,
    # ).add_selection(
    #     pandemic_selection
    )
    st.write(graph_trend)
# draw neighborhood level data
elif page_selection == "City Wide":
    Neighborhood.loadNeighborhoodData()
        
    
    