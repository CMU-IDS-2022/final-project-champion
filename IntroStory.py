from turtle import width
import streamlit as st
import altair as alt
import pandas as pd
from PIL import Image

cityStudentMapping = {
  "cities": ["San Francisco", "Pittsburgh", "New York", "Seattle", "Boston", "Washington", "Los Angeles", "Chicago", "Philadelphia", "Detroit"],
  "states": ["CA", "PA", "NY", "WA", "MA", "DC", "CA", "IL", "PA", "MI"],
  "number of students": [2898, 2830, 1320, 846, 526, 502, 292, 256, 142, 114],
}

df = pd.DataFrame(data=cityStudentMapping)

def showStory():
  st.header("Which city in the United States are you heading to after graduation?")

  st.markdown("According to this [CMU webpage](https://www.cmu.edu/career/outcomes/post-grad-dashboard.html), here are the top 10 cities students head to after graduation.")

  col1, col2, col3 = st.columns([1,6,1])
  with col1:
    st.write("")
  with col2:
    image = Image.open('data/top10CMUGradPlaces.png')
    st.image(image, caption='Top 10 cities CMU students go to after graduation', width=800)
  with col3:
    st.write("")

  citiesSelection = st.checkbox("Show data from graph")
  if citiesSelection:
    st.dataframe(df)

  st.subheader("However, covid has brought about many uncertainties in the United States, especially housing rent!")

  st.markdown('''
    For example, as more people are working from home during the pandemic, the rental prices for cities dropped as people start to [rent in suburban areas](https://www.census.gov/library/stories/2021/10/zillow-and-census-bureau-data-show-pandemics-impact-on-housing-market.html#:~:text=working%20from%20home.-,Zillow%20found%20that%20nearly%20two%20million%20renters%20unable%20to%20afford,pandemic%20hit%20the%20United%20States.). 
    With such ongoing changes, young adults like us are unsure where and what price to pay to rent a house to be worth.
  ''')

  st.write("As such, we have decided to analyze how rental prices in housing have changed pre-pandemic, during the pandemic and how it is post pandemic.")

  st.subheader('''
    What price should you pay for rent in those locations based on the housing trends from pre-pandemic, pandemic and post pandemic?
  ''')
     