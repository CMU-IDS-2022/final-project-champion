import streamlit as st
import altair as alt
from vega_datasets import data
import pprint
import pandas as pd
import json
from altair import datum

from collections import defaultdict

top10cities = set(["Boston", "Chicago", "Detroit", "Los Angeles", "New York", "Philadelphia", "Pittsburgh", "San Francisco", "Seattle", "Washington"])

alt.data_transformers.enable('default', max_rows=None)

def readCsv(fileName):
  return pd.read_csv(fileName)



def loadNeighborhoodData():
	st.write("ABCDefgh")

