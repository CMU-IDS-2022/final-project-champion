# Final Project Proposal

**GitHub Repo URL**: https://github.com/CMU-IDS-2022/final-project-champion

**Question**: Which location in the United States and what price should young adults these days pay for rental based on housing trends from pre-pandemic, pandemic and post pandemic prices predictions?

The housing prices in the United States have always been fluctuating. There is much attention focused on sales of housing prices but not so much on housing rental cost. This is even more evident in recent years due to the pandemic as more people are working from home, causing the prices for cities to drop as people start to [rent in suburban areas](https://www.census.gov/library/stories/2021/10/zillow-and-census-bureau-data-show-pandemics-impact-on-housing-market.html#:~:text=working%20from%20home.-,Zillow%20found%20that%20nearly%20two%20million%20renters%20unable%20to%20afford,pandemic%20hit%20the%20United%20States.). With such ongoing changes, young adults like us are unsure where and what price to pay to rent a house to be worth. As such, we have decided to analyze how rental prices in housing have changed pre-pandemic, during the pandemic and even possibly use machine learning algorithms to forecast how it would be in post pandemic days. Our goal is to provide an all in one rental cost visualization platform for users to make a more informed decision on where to rent and how much to pay if given a preference in location and the characteristics of housing.

With many general trends of housing rentals online in the United States, we want to focus more on the granularity data in deciding where to rent. Hence, we decided to use a bottom up approach in our analysis. We will sieve out the top 10 cities which students who graduated from CMU go to based on the data [here](https://www.cmu.edu/career/outcomes/post-grad-dashboard.html). Then, focusing on each city in neighborhood level, we will try to analyze the housing rental cost across the years, through the pandemic periods accounting for various types of housing and different characteristics of the locations, like crime rate, neighborhood, safety etc. We will share a range of acceptable rental prices for the user who wants to rent in that area. After analyzing on the neighborhood level, we will zoom up in analyzing analyze the general trends on the city rental cost to the state and finally across states in the United States.

In terms of data, we have found many recent rental datas of various characteristics on the [Zillow website](https://www.zillow.com/research/data/) that is up to date to this year. We also found other sources of data from the [government](https://www.fhfa.gov/DataTools/Downloads/Pages/House-Price-Index-Datasets.aspx). Given the wide topic of housing rental cost, we believe we are able to find more datasets on other characteristics if needed.

After we finish the visualization aspect of the project using existing data, we hope to make use of the data to run some simple machine learning models to predict future rental housing prices based on certain assumptions. As we believe that this project can be scoped further to provide more information to the users in deciding where to rent. If time allows, we would want to add in some analysis to possible reasons as to why the prices have changed in value or even cost of living data to help the users.

----------------
## Start of Data Processing

### How to Estimate Rental Price for each zip code  

This is how Zillow makes their metrics according to housing price, index, and rental index. But the problem is that we do not have zipcode level of rental price for each room type(1 bed, 2 bed, studio, ...). So, we try to estimate rental price values by using Zillow's dataset like below. 

This data and decription comes from Zillow research dataset [link](https://www.zillow.com/research/data/)  

### HOME VALUES

Zillow Home Value Index (ZHVI): A **smoothed, seasonally adjusted measure** of the typical home value and market changes across a given region and housing type. It reflects the typical value for homes in the 35th to 65th percentile range. The raw version of that mid-tier ZHVI time series is also available.

Zillow publishes top-tier ZHVI (\$, typical value for homes within the 65th to 95th percentile range for a given region) and bottom-tier ZHVI ($, typical value for homes that fall within the 5th to 35th percentile range for a given region).

Zillow also publishes ZHVI for all single-family residences (\$, typical value for all single-family homes in a given region), for condo/coops (\$), for all homes with 1, 2, 3, 4 and 5+ bedrooms (\$), and the ZHVI per square foot (\$, typical value of all homes per square foot calculated by taking the estimated home value for each home in a given region and dividing it by the home’s square footage). Check out this overview of ZHVI and a deep-dive into its methodology. 

Here’s a handy ZHVI User Guide for information about properly citing and making calculations with this metric.

### HOME VALUES FORECASTS

The Zillow Home Value Forecast (ZHVF) is the month-ahead, quarter-ahead and year-ahead forecast of the Zillow Home Values Index (ZHVI). ZHVF is created using the all homes, mid-tier cut of ZHVI and is available both raw and smoothed, seasonally adjusted.

**RENTALS**

Zillow Observed Rent Index (ZORI): A **smoothed measure** of the typical observed market rate rent across a given region. ZORI is a repeat-rent index that is weighted to the rental housing stock to ensure representativeness across the entire market, not just those homes currently listed for-rent. The index is dollar-denominated by computing the mean of listed rents that fall into the 40th to 60th percentile range for all homes and apartments in a given region, which is once again weighted to reflect the rental housing stock. Details available in ZORI methodology.

We can gather the housing price's fluctuation but hard to archive historical changes of rent price over years.  
So, we establish the housing price - rent price conversion rate based Zillow Value Index on Home Value and Rentals.  
The problem is rental price was made of the weighted average price of all list in specific period, but we want to show each period each type's rental price.  
To do this, we calculate Rental Price Index for each housing type(1bed, 2bed, etc.) with weighted average housing price index(forecast, all home) and weighted average rental price index(all home).

![image](https://user-images.githubusercontent.com/79838132/163627104-e83e8411-7da0-41ff-b4d1-976349d8c9e4.png)

Here is the housing price and estimated rental data as we proceed the estimatioin by following the logic.  
![image](https://user-images.githubusercontent.com/79838132/163627250-3b30736f-6789-420a-a987-7ce96b75f1b7.png)

![image](https://user-images.githubusercontent.com/79838132/163627279-12d5db8d-4268-40a6-838f-62c769163744.png)


Even this estimated value it not the exact value of rental price in that area, at least we can track the historical variation of rental price within the city and provide students to point out which place to start with for their next destination in detail.  

----------------------------------------------------------------
**Visualizations**
The first page with a map shows the top 10 cities CMU students go to when they graduate.Its the start of exploration process.

<img width="550" alt="WX20220415-225459@2x" src="https://user-images.githubusercontent.com/97925469/163658837-ad662ff5-04c1-4759-bdbb-4fd45e783e01.png">

Then there is a nation map.Students could choose some virables and cites their want to know about.
1.Show each room type rent YoY rate over year
2.Show top N faller and riser city for rental price 
3.Compare Each year Rent trend on selected city(includes:House Price,House Index,Rent Index,Estimated Rent Price)
4.Show cirme rate chart every 100k person
5.Show average income level change in selected cities.
Next part is specific city analysis.
This slides shows an example of price.Users can choose which part district of specific cities they want to know and the district information will show up. Neighbour breakdown for a city with name and current price with different colors. Then there is a menu of current time to choose.The second part have price / listings in current year and bed types for prices to vary accordingly. The third bar chart shows median price across neighborhoods with highlight accordingly based on the neighborhood selected.

<img width="575" alt="WX20220415-230949@2x" src="https://user-images.githubusercontent.com/97925469/163659273-f1846302-c165-4c09-b4df-86c431f36d6e.png">

This slide is very similar to the pervious slides but with additional option to select time frame based on pandemic. The chart highlight accordingly based on the neighborhood selected with and price fluctuates in percentage across time in each neighborhood.

<img width="567" alt="WX20220415-233024@2x" src="https://user-images.githubusercontent.com/97925469/163659961-55200245-a76a-4aaa-8cf2-4693f6dd7960.png">

Ref: [powerpoint visualization](https://docs.google.com/presentation/d/1knz1n-LBvtL3ET3bLN5FyZnN-cmNViw0l_zkHrjORmM/edit?usp=sharing)
