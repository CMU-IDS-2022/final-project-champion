import os
import pandas as pd
import numpy
import pytrends

from pytrends.request import TrendReq

top10cities = set(["Boston", "Chicago", "Detroit", "Philadelphia", "Pittsburgh", "Seattle", "Washington"]) # "San Francisco", "Los Angeles", "New York", 

# filter to leave top 10 cities
def filterTop10Cities(df):
  for index, row in df.iterrows():
    if row['City'] not in top10cities:
      df.drop(index, inplace=True)
  return df


def writeIntoFile(df, city):
  outdir = "data/" + city.replace(" ", "")
  if not os.path.exists(outdir):
    os.mkdir(outdir)
  # TODO: change to output file name before running script
  df.to_csv(f"{outdir}/googleTrends.csv")


if __name__ == "__main__":
  # TODO: change to unprocessed file name before running script
  # housing_df = pd.read_csv("data/neighborhood_1br_rental_price.csv")
  pytrend = TrendReq(retries=5)

  housing_df = pd.read_csv("data/neighborhood_1br_rental_price.csv")

  housing_df = filterTop10Cities(housing_df)

  city_neighborhood_mapping = {}
  for city in top10cities:
    temp_df = housing_df[housing_df['City'] == city]
    res = temp_df['Neighborhood']
    city_neighborhood_mapping[city] = list(set(res))

  print(city_neighborhood_mapping)

  for k in city_neighborhood_mapping.keys():
    KEYWORDS = city_neighborhood_mapping[k]
    KEYWORDS_CODES = []
    for i in KEYWORDS:
      try:
        suggestion = pytrend.suggestions(keyword=i)
      except:
        print("unable to generate suggestion for keyword:", i)
      if suggestion:
        KEYWORDS_CODES.append(suggestion[0])
    print(KEYWORDS_CODES)

    df_CODES= pd.DataFrame(KEYWORDS_CODES)
    print(df_CODES)
    EXACT_KEYWORDS=df_CODES['mid'].to_list()
    DATE_INTERVAL='2018-01-01 2022-03-01'
    COUNTRY=["US"] #Use this link for iso country code
    CATEGORY=0 # Use this link to select categories
    SEARCH_TYPE='' #default is 'web searches',others include 'images','news','youtube','froogle' (google shopping)

    Individual_EXACT_KEYWORD = list(zip(*[iter(EXACT_KEYWORDS)]*1))
    Individual_EXACT_KEYWORD = [list(x) for x in Individual_EXACT_KEYWORD]
    dicti = {}
    i = 1
    for Country in COUNTRY:
      for keyword in Individual_EXACT_KEYWORD:
        try:
          pytrend.build_payload(kw_list=keyword, 
                                timeframe = DATE_INTERVAL, 
                                geo = Country, 
                                cat=CATEGORY,
                                gprop=SEARCH_TYPE) 
          dicti[i] = pytrend.interest_over_time()
          i+=1
        except:
          print("could not be process keyword:", keyword)

    df_trends = pd.concat(dicti, axis=1)

    result = ['date'] + list(df_CODES['title'])

    df_trends.columns = df_trends.columns.droplevel(0) #drop outside header
    df_trends = df_trends.drop('isPartial', axis = 1) #drop "isPartial"
    df_trends.reset_index(level=0,inplace=True) #reset_index
    result = result[:len(df_trends.columns)]
    df_trends.columns = result

    writeIntoFile(df_trends, k)


