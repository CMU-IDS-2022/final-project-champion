# url_geojson = "https://data.sfgov.org/api/views/6ia5-2f8k/rows.json"
	# url_geojson = "https://data.sfgov.org/resource/6ia5-2f8k.json"
	# geoData = alt.Data(url=url_geojson, format=alt.DataFormat(property='data', type='json'))

	# graph = alt.Chart(geoData).mark_geoshape(
	# ).encode(
	#     color="data.name:N"
	# ).project(
	#     type='identity', reflectY=True
	# )
	# st.write(graph)

	# st.write(geoData)

	# url_geojson = "https://github.com/vega/vega-datasets/edit/master/data/us-10m.json"
	# geoData = alt.Data(url=url_geojson, format=alt.DataFormat(property='feature', type='json'))

	# graph = alt.Chart(geoData).mark_geoshape(
	# ).encode(
	#     color="properties.name:N"
	# ).project(
	#     type='identity', reflectY=True
	# )
	# st.write(graph)

	# st.altair_chart(showGraphChart(geoData, city_neighborhood_mapping[city]))


	states = alt.topo_feature(data.us_10m.url, feature='states')

	graph = alt.Chart(states).mark_geoshape(
	    fill='lightgray',
	    stroke='white'
	).project('albersUsa').properties(
	    width=500,
	    height=300
	)
	st.write(graph)