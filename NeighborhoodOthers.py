import streamlit as st
import altair as alt
import pprint
import pandas as pd

emoji = {'safety': '👮', 'transport': '🚌', 'income': '💰'}

def loadOthersNeighborhoodData(citySelection):
  st.header("other neighborhood data")
  