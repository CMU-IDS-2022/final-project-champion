import os
import pandas as pd
import numpy

top10cities = set(["Boston", "Chicago", "Detroit", "Los Angeles", "New York", "Philadelphia", "Pittsburgh", "San Francisco", "Seattle", "Washington"])

# create general city ratio index
city_index_df = pd.read_csv("data/top10_cities_index_ratio_updated.csv")
# maps cities to a ratio
city_time_ratio = {}
for i, row in city_index_df.iterrows():
  city_time = f'{row[0]}-{row[1]}'
  city_time_ratio[city_time] = row[2]
city_time_ratio

# filter to leave top 10 cities
def filterTop10Cities(df):
  for index, row in df.iterrows():
    if row['City'] not in top10cities:
      df.drop(index, inplace=True)
  return df

# rename column name to index format
def getNewDateColumns(df):
  newColumns = []
  for column in df:
    if '/' in column:
      res = column.split('/')
      res[0] = res[0] if len(res[0]) == 2 else '0'+res[0]
      newName = f'20{res[2]}-{res[0]}'
      newColumns.append(newName)
    else:
      newColumns.append(column)
  return newColumns

# convert housing price to rental based on index
def convertPriceToRental(df):
  for index, row in df.iterrows():
    city = row['City']
    for column in df:
      city_time = city + '-' + column
      if city_time in city_time_ratio:
        newValue = row[column] * city_time_ratio[city_time]
        df.at[index, column] = newValue
  return df


def reformateColumns(housing_df):
  # reformat data
  columnNames = ['RegionID',  'SizeRank', 'RegionName', 'RegionType', 'StateName',  'State', 'City', 'Metro', 'CountyName']
  housing_df = housing_df.melt(id_vars=columnNames, 
          var_name="Date", 
          value_name="Prices")
  housing_df.rename(columns={'RegionName':'Neighborhood'}, inplace=True)
  return housing_df.dropna()


def splitDataIntoMultipleFiles(housing_df):
  for city, df in housing_df.groupby('City'):
    outdir = "data/" + city.replace(" ", "")
    if not os.path.exists(outdir):
      os.mkdir(outdir)
    # TODO: change to output file name before running script
    df.to_csv(f"{outdir}/condoRental")


if __name__ == "__main__":
  # TODO: change to unprocessed file name before running script
  # housing_df = pd.read_csv("data/neighborhood_1br_rental_price.csv")
  housing_df = pd.read_csv("data/neighborhood_condo_rental_price.csv")

  housing_df = filterTop10Cities(housing_df)

  housing_df.columns = getNewDateColumns(housing_df) # convert columns type

  housing_df = convertPriceToRental(housing_df) # convert prices to rental price

  housing_df = reformateColumns(housing_df) # reformat column names and styles

  # create a meanPrices column
  housing_df['MeanPrices'] = housing_df.groupby('Neighborhood')['Prices'].transform('mean')

  print(housing_df.head())

  # create separate year and month columns
  housing_df[['Year', 'Month']] = housing_df['Date'].str.split('-', expand= True)
  print(housing_df.head())

  splitDataIntoMultipleFiles(housing_df)
