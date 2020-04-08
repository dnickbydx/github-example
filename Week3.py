#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

#!conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

get_ipython().system("conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab")
import folium # map rendering library

print('Libraries imported.')


# # Part 1

# In[3]:


import requests
from bs4 import BeautifulSoup

res = requests.get("https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M")
soup = BeautifulSoup(res.content,'lxml')
table = soup.find_all('table')[0] 
df = pd.read_html(str(table))
table_rows = table.find_all('tr')

res = []
for tr in table_rows:
    td = tr.find_all('td')
    row = [tr.text.strip() for tr in td if tr.text.strip()]
    if row:
        res.append(row)


# In[4]:


df = pd.DataFrame(res, columns=["Postal code", "Borough", "Neighborhood"])
indexboro = df[ df['Borough']=='Not assigned'].index
df.drop(indexboro , inplace=True)
df['Neighborhood'] = df['Neighborhood'].str.replace('/',',')


# 1. Download and obtain dataframe
# 2. Remove rows with Borough = Not assigned
# 3. Replace '/' with ',' 

# In[5]:


df.head(12)


# In[6]:


df.shape


# # Part 2

# In[7]:


get_ipython().system("wget -q -O 'Geospatial_Coordinates.csv' https://cocl.us/Geospatial_data")
print('Data downloaded!')
gcdf = pd.read_csv('Geospatial_Coordinates.csv')


# In[8]:


gcdf.head()


# In[9]:


#Sort by postal code to match  
df.sort_values(by=['Postal code'], inplace=True)
df = df.reset_index(drop=True)
df.head()


# In[10]:


dfa = df
dfa['Latitude'] = gcdf['Latitude']
dfa['Longitude'] = gcdf['Longitude']
dfa.head(12)


# # Part 3

# In[12]:


# Restrict to boroughs which contains "Toronto"
dft = dfa[dfa["Borough"].str.contains("Toronto")]


# In[16]:


# set number of clusters
kclusters = 5

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(dft[['Latitude','Longitude']])
dfk = dft
dfk['Cluster'] = kmeans.fit_predict(dft[['Latitude','Longitude']])
dfk.head()


# In[18]:


address = 'Toronto'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[27]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=12)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(dfk['Latitude'], dfk['Longitude'], dfk['Neighborhood'], dfk['Cluster']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[ ]:




