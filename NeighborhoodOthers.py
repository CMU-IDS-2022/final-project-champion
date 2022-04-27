import streamlit as st
import altair as alt
import pprint
import pandas as pd

emoji = {'safety': '👮', 'Trans': '🚌', 'income': '💰'}
Year = [2019, 2020, 2021]

def file(city):
    total = pd.read_csv('data/total.csv')
    df = total.loc[total['City'] == city]
    return df

def cityyear(df,x,top):
    df = df.loc[df['Year'] == x]
    trans = alt.Chart(df).mark_bar().encode(
        x=alt.X('Neighborhood:N', sort='-y'),
        y=alt.Y('Transportation:Q'),
        color=alt.Color('Transportation:Q')
    ).transform_window(
        rank='rank(Transportation)',
        sort=[alt.SortField('Transportation', order='descending')]
    ).transform_filter(
        (alt.datum.rank < top)
    ).properties(height=200, width=400)

    crime = alt.Chart(df).mark_bar().encode(
        x=alt.X('Neighborhood:N', sort='-y'),
        y=alt.Y('Safety:Q'),
        color=alt.Color('Safety:Q')
    ).transform_window(
        rank='rank(Safety)',
        sort=[alt.SortField('Safety', order='descending')]
    ).transform_filter(
        (alt.datum.rank < top)
    ).properties(height=200, width=400)

    Income = alt.Chart(df).mark_bar().encode(
        x=alt.X('Neighborhood:N', sort='-y'),
        y=alt.Y('Income(k):Q'),
        color=alt.Color('Income(k):Q')
    ).transform_window(
        rank='rank(Income(k))',
        sort=[alt.SortField('Income(k)', order='descending')]
    ).transform_filter(
        (alt.datum.rank < top)
    ).properties(height=200, width=400)


    return (trans & crime & Income)

def n(df,name):
  #df = df.loc[df['Neighborhood'].isin(name)]
  n1 = alt.Chart(df).mark_bar().encode(
    x='Year:O',
    y='Transportation',
    color='Transportation',
    column = 'Neighborhood'
).transform_filter(
      alt.FieldOneOfPredicate(field='Neighborhood', oneOf=name)
).properties(height=100, width=100)


  n2 = alt.Chart(df).mark_bar().encode(
    x='Year:O',
    y='Safety',
    color='Safety',
    column='Neighborhood'
).transform_filter(
      alt.FieldOneOfPredicate(field='Neighborhood', oneOf=name)
).properties(height=100, width=100)

  n3 = alt.Chart(df).mark_bar().encode(
    x='Year:O',
    y='Income(k)',
    color='Income(k)',
    column='Neighborhood'
).transform_filter(
      alt.FieldOneOfPredicate(field='Neighborhood', oneOf=name)
).properties(height=100, width=100)

  return (n1 & n2 & n3)





def loadOthersNeighborhoodData(citySelection):
    st.header("other neighborhood data")
    Yearselection = st.selectbox("Which year would you like to see?", Year)
    topnumber = st.slider( 'Top N neighborhood you can check', 0, 20)

    df = file(citySelection)
    figure1 = cityyear(df,Yearselection,topnumber)
    st.write(figure1)

    st.subheader("Specific neighborhood visualizations")
    neighborhoodSelections = st.multiselect("Which neighborhood would you like to see?", set(df['Neighborhood']))

    figure2 = n(df, neighborhoodSelections)
    st.write(figure2)







