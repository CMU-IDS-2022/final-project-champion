# Final Project Report

* **Project URL**: https://share.streamlit.io/cmu-ids-2022/final-project-champion/main/app.py
* **Video URL**: [Final video in repo](Champion_IDS_final_video.mov) 
	- Back up link live on [vimeo](https://vimeo.com/704280556)

Short (~250 words) abstract of the concrete data science problem and how the solutions addresses the problem.

## Introduction
The housing prices in the United States have always been fluctuating. There is much attention focused on sales of housing prices but not so much on housing rental cost. This is even more evident in recent years due to the pandemic as more people are working from home, causing the prices for cities to drop as people start to [rent in suburban areas](https://www.census.gov/library/stories/2021/10/zillow-and-census-bureau-data-show-pandemics-impact-on-housing-market.html). With such ongoing changes, young adults like us are unsure where and what price to pay to rent a house to be worth. 

Using the top 10 cities most CMU students will head to after graduation, we have decided to analyze how rental prices in these cities have changed pre-pandemic, during the pandemic and post pandemic days. We also considered other important factors such as safety, transportation and income data. The two main points that made us unique is the low level neighborhood level analysis in cities and having the functionality of all data being visualized on a single platform.

We hope this can allow users to make a more informed decision on where to rent and how much to pay given a preference in a city and type of housing.

## Related Work
The most relevant works we found are from [Zillow research platform](https://www.zillow.com/research/). They have multiple interfaces to show housing trends and monthly housing analysis reports. They are definitely insightful for us to look through and learn more about the housing market. However, Zillow has too much focus on housing prices. Since we are focusing on rental prices, we also checked other sources like [ApartmentList](https://www.apartmentlist.com/research/national-rent-data),  [Rent.com](https://www.rent.com/) and etc. We have also looked at general analysis to understand better about the rental market from websites like [Statista](https://www.statista.com/topics/4465/rental-market-in-the-us/).

Although these works are helpful, all the visualizations and resources mainly exist on the country, state or city wide level. There aren’t many specific visualizations or data on the breakdown in terms of neighborhood level.

Hence, we decided to refer to these visualizations and interfaces and come up with our own design. We collated a number of relevant interfaces (~10) from multiple sources into a [powerpoint](RelatedVisualizationExamples.pdf) for further reference and discussion to enhance them. Most of these visualizations are updated weekly or monthly with lots of informative data but limited functionalities to interact with. That being said, this was a great starting point for us to come up with our own visualizations.

## Methods
There are 2 main important aspects to be covered under methods. The first one is on data collection and analysis while the second one is on the specific implementations based on our initial research question.

### Data Collection and Processing
As mentioned earlier, most housing related data only exists on the city level. For our use case, we wanted to find a breakdown of rental prices on the neighborhood level with multiple bedroom types. We spent a considerable amount of time and effort searching through multiple sources gathering and processing data. The entire process to find what we need and pre-process them for visualizations was both tedious and difficult. As such, we want to dedicate a section explaining them.

#### 1. Neighborhood and Bedroom Level Rental Price Data Over the Years
This is the most difficult data to find and also the foundation of what we want to build. After much effort into our research, we eventually had 2 options; either we scrape data from rental websites or construct estimation of the data based on what is available on [Zillow](https://www.zillow.com/research/data/). Since the former option is both tedious and only provides current year data, we chose the latter option instead. 

### 

## Results

## Discussion

## Future Work
