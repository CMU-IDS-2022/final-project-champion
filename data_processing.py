# import library
import pandas as pd
import numpy as np
import os  
os.makedirs('./result', exist_ok=True)  

# part 1: get conversion index rate between housing price index and rental price index

# housing_index : house price data for zip code level across the US
# rental_index : rental price data for zip code level across the US
# we will estimate the rental price by converting the detail housing price with these two price index
# reason : low-level rental price is not provided from any real estate company(Zillow also shot down its data access)

# melt dates column data into row
def melt_dataset(date_col_start_index, val_name, df):
    columns = list(df.columns)
    cols = columns[:date_col_start_index]
    dates = columns[date_col_start_index:]
    new_df = df.melt(id_vars=cols, var_name="date", value_vars=dates, value_name=val_name)
    new_df['date']=pd.to_datetime(new_df['date'],infer_datetime_format=True)
    return new_df

# select dates from the entire data set
def date_selection(df,date_after):
    df['date']=df['date'].astype(str)
    # substring date as "yyyy-mm"
    df['date'] = df['date'].apply(lambda x:x[:7])    
    # select date after input value
    df_f = df[df['date']>=date_after]
    return df_f

# load data as dataframe 
df_housing_index = pd.read_csv("Zip_housing_forecasting_index.csv")
df_rental_index = pd.read_csv("Zip_rental_index.csv")
# melt data and select date after Jan, 2018
df_housing_index_melt = melt_dataset(9,"housing_p_index",df_housing_index)
df_housing_index_f = date_selection(df_housing_index_melt, "2018-01")
df_rental_index_melt = melt_dataset(4,"rental_p_index",df_rental_index)
df_rental_index_f = date_selection(df_rental_index_melt,"2018-01")
# join data rental_p_index and housing_p_index
df_index_merged = pd.merge(left = df_housing_index_f[['City','RegionID','date','housing_p_index']], right=df_rental_index_f[['RegionID','date','rental_p_index']]\
            ,how='inner', on=['RegionID','date'])
df_index_merged.dropna(inplace=True)
df_index_merged['index_ratio']=df_index_merged['rental_p_index']/df_index_merged['housing_p_index']
# df_index_merged.head()
df_index = df_index_merged[['City','RegionID','date','index_ratio']]

# select top ten city to have deep dive
# top 10 cities are selected based on Carnegie Mellon University student's work place after graduation
# reference : https://www.cmu.edu/career/outcomes/post-grad-dashboard.html
def select_top_ten_cities(df):
    topcities = ['San Francisco','Pittsburgh','New York','Seattle',\
                'Boston','Washington','Los Angeles','Chicago','Philadelphia','Detroit']
    df_selected=df[df['City'].isin(topcities)]
    return df_selected
    
# select top 10 cities from original data
df_top10_index_merged=select_top_ten_cities(df_index_merged)
df_top10_city_index=df_top10_index_merged.groupby(by=['City','date'],as_index=False)['index_ratio'].mean()
# save the process file
df_top10_city_index.to_csv('./result/top10_cities_index.csv',index=False)

################################################################
# part2 : calculate rental price with calculated City level index
# calculate rental price using city index
def get_city_rental_price(df_housing_price_type):
    # melt table
    df_melt = melt_dataset(9,"housing_price",df_housing_price_type)
    # select date after "2015-01"
    df_melt = date_selection(df_melt,"2018-01")
    df_melt = select_top_ten_cities(df_melt)
    # this is inner join, each there is no matching data either table, then ignore the record
    df_merge=pd.merge(df_melt, df_index, how='inner',on=['City','RegionID','date'])
    df_merge['rental_price'] = df_merge['housing_price']*df_merge['index_ratio']
    df_final = df_merge[['City','date','rental_price']].groupby(by=['City','date'])['rental_price'].mean().reset_index()
    return df_final

# import housing price data for each room type form Zillow Research Data
df_1bed = pd.read_csv("Zip_housing_1bed.csv")
df_2bed = pd.read_csv("Zip_housing_2bed.csv")
df_3bed = pd.read_csv("Zip_housing_3bed.csv")
df_4bed = pd.read_csv("Zip_housing_4bed.csv")
df_5bed = pd.read_csv("Zip_housing_5bed.csv")
df_single_f_home = pd.read_csv("Zip_housing_single_f_home.csv")
# calculate rental price for each room type
df_1bed_city = get_city_rental_price(df_1bed)
df_2bed_city = get_city_rental_price(df_2bed)
df_3bed_city = get_city_rental_price(df_3bed)
df_4bed_city = get_city_rental_price(df_4bed)
df_5bed_city = get_city_rental_price(df_5bed)
df_single_f_home_city = get_city_rental_price(df_single_f_home)
# store roomtype information for each data
df_1bed_city['roomtype'] = '1bed'
df_2bed_city['roomtype'] = '2beds'
df_3bed_city['roomtype'] = '3beds'
df_4bed_city['roomtype'] = '4beds'
df_5bed_city['roomtype'] = '5beds'
df_single_f_home_city['roomtype']='single_family_home'
# concatenate all room type dataset to single dataset
df_final=pd.concat([df_1bed_city,df_2bed_city,df_3bed_city,\
                    df_4bed_city,df_5bed_city,df_single_f_home_city],ignore_index=True)
# store the final data
df_final.to_csv('./result/top10_cities_rental_price.csv',index=False)
