# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 10:39:23 2021

@author: stijn
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import googlemaps
import time
import osmnx as ox

#%% Plot map of Amsterdam city center by using OSMnx

#Boundaries of Amsterdam city center
boundaries = [52.3869, 52.3565, 4.8614, 4.9356]

graph = ox.graph_from_bbox(boundaries[0], boundaries[1], boundaries[2], boundaries[3])   
nodes, edges = ox.graph_to_gdfs(graph)

fig, ax = plt.subplots(figsize=(15,15), dpi=300)
plt.title('Amsterdam city center')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
edges.plot(ax=ax, linewidth=1, edgecolor='grey', alpha=0.5)
nodes.plot(ax=ax, color='lightblue', markersize=5)

#%% Make a grid of coordinates for the city center of Amsterdam

#define number of steps
steps = 6

#define coordinates of upper left and upper right corner
upper_left_long   = 4.87724749320942
upper_right_long  = 4.92159689032779
stepsize_x = (upper_right_long - upper_left_long)/steps

coordinate_x = upper_left_long

#define coordinates of points on x-axis (longitudes)
step = 1
li_x = [upper_left_long]
while step <= steps:
    coordinate_x = coordinate_x + stepsize_x
    li_x.append(coordinate_x)
    step = step + 1
    
List_longitudes = li_x

#define coordinates of lower left and lower right corner
upper_left_lat    = 52.38482611025085
lower_left_lat    = 52.35776879819587
stepsize_y = (lower_left_lat - upper_left_lat)/steps

coordinate_y = upper_left_lat

#define coordinates of points on y-axis (latitudes)
step = 1
li_y = [upper_left_lat]
while step <= steps:
    coordinate_y = coordinate_y + stepsize_y
    li_y.append(coordinate_y)
    step = step + 1
    
List_latitudes = li_y

#make a grid
li_xx = []
li_yy = []
for x in List_longitudes:
    for y in List_latitudes:
        li_xx.append(x)
        li_yy.append(y)

#remove points outside the city center (manually)
delete = [6, 21, 28, 29, 35, 36, 41, 42, 43, 48]
for i in delete:
    li_xx[i] = 0
    li_yy[i] = 0

li_xx = [i for i in li_xx if i != 0]
li_yy = [i for i in li_yy if i != 0]

#plot
fig, ax = plt.subplots(dpi=300)
plt.scatter(li_xx,li_yy, c='purple')
plt.show

#list with all coordinates
points = (tuple([x, y] for x, y in zip(li_yy, li_xx)))

#dataframe with all coordinates
df = pd.DataFrame(points)

#%% Plot grid of coordinates with radius on top of the OSMnx graph 

latitudes = df[0].tolist()
longitudes = df[1].tolist()

fig, ax = plt.subplots(figsize=(15,15), dpi=300)
plt.title('Amsterdam city center with grid')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
edges.plot(ax=ax, linewidth=1, edgecolor='grey', alpha=0.5)
nodes.plot(ax=ax, color='lightblue', markersize=5)

ax.scatter(longitudes, latitudes, c='purple')

for i in range(len(longitudes)):
    circle = plt.Circle((longitudes[i], latitudes[i]), 0.004, color='purple', alpha=0.2)
    ax.add_artist(circle)

a = 0.005

plt.xlim([boundaries[2]-a, boundaries[3]+a])
plt.ylim([boundaries[1]-a, boundaries[0]+a])

ax.add_artist(circle)
plt.show()

#%% Use grid coordinates as an input for Google Places API

#define the API KEY
API_KEY = open('C:/Users/stijn/Dropbox/Stijn/Research Project/Python/02 Python_scripts/Google_maps_API_with_python/API_KEY.txt').read()

#define our client
map_client = googlemaps.Client(API_KEY)

search_strings = ['hotel', 'restaurant', 'cafe']

list_hotel = []
list_restaurant = []
list_cafe = []

for i in range(len(search_strings)):
    
    total_list = []
    g = globals()
    
    locations = points

    for location in locations:
    
        search_string = search_strings[i]
        radius_km = 0.2
        distance = radius_km * 1000
        search_list = []
        
        response = map_client.places_nearby(
            location=location,
            keyword=search_string,
            radius=distance
            )
        
        search_list.extend(response.get('results'))
        next_page_token = response.get('next_page_token')
        
        while next_page_token:
            time.sleep(4)
            response = map_client.places_nearby(
                location=location,
                keyword=search_string,
                radius=distance,
                page_token=next_page_token)
            
            search_list.extend(response.get('results'))
            next_page_token = response.get('next_page_token')
            
            selection = pd.DataFrame(search_list, columns = ['name', 'geometry', 'vicinity'])
            
            total_list.append(selection)

    total_list = pd.concat(total_list, ignore_index=True)
    
    total_list['geometry'] = total_list['geometry'].astype(str)
    
    g['list_{0}'.format(search_strings[i])] = total_list
   
#%% Filter duplicates, keep the first one

list_hotel.drop_duplicates(subset='name', keep='first', inplace=True, ignore_index=True)
list_restaurant.drop_duplicates(subset='name', keep='first', inplace=True, ignore_index=True)
list_cafe.drop_duplicates(subset='name', keep='first', inplace=True, ignore_index=True)

#%% Change geometry to long and lat

list_hotel['latitudes'] = list_hotel['geometry'].str.split(", 'lng': ").str[0]
list_hotel['latitudes'] = list_hotel['latitudes'].str.split("lat': ").str[1]
list_hotel['longitudes'] = list_hotel['geometry'].str.split("}, 'viewport").str[0]
list_hotel['longitudes'] = list_hotel['longitudes'].str.split("lng': ").str[1]
list_hotel['latitude'] = list_hotel['latitudes']
list_hotel['longitude'] = list_hotel['longitudes']
selection0 = pd.DataFrame(list_hotel, columns = ['name', 'latitude', 'longitude', 'vicinity'])
list_hotel = pd.DataFrame(selection0)

list_restaurant['latitudes'] = list_restaurant['geometry'].str.split(", 'lng': ").str[0]
list_restaurant['latitudes'] = list_restaurant['latitudes'].str.split("lat': ").str[1]
list_restaurant['longitudes'] = list_restaurant['geometry'].str.split("}, 'viewport").str[0]
list_restaurant['longitudes'] = list_restaurant['longitudes'].str.split("lng': ").str[1]
list_restaurant['latitude'] = list_restaurant['latitudes']
list_restaurant['longitude'] = list_restaurant['longitudes']
selection1 = pd.DataFrame(list_restaurant, columns = ['name', 'latitude', 'longitude', 'vicinity'])
list_restaurant = pd.DataFrame(selection1)

list_cafe['latitudes'] = list_cafe['geometry'].str.split(", 'lng': ").str[0]
list_cafe['latitudes'] = list_cafe['latitudes'].str.split("lat': ").str[1]
list_cafe['longitudes'] = list_cafe['geometry'].str.split("}, 'viewport").str[0]
list_cafe['longitudes'] = list_cafe['longitudes'].str.split("lng': ").str[1]
list_cafe['latitude'] = list_cafe['latitudes']
list_cafe['longitude'] = list_cafe['longitudes']
selection2 = pd.DataFrame(list_cafe, columns = ['name', 'latitude', 'longitude', 'vicinity'])
list_cafe = pd.DataFrame(selection2)

#%% Plot city center of Amsterdam with all horeca businesses

latitudes_hotel         = [float(x) for x in list_hotel['latitude'].tolist()]
longitudes_hotel        = [float(x) for x in list_hotel['longitude'].tolist()]
latitudes_restaurant    = [float(x) for x in list_restaurant['latitude'].tolist()]
longitudes_restaurant   = [float(x) for x in list_restaurant['longitude'].tolist()]
latitudes_cafe          = [float(x) for x in list_cafe['latitude'].tolist()]
longitudes_cafe         = [float(x) for x in list_cafe['longitude'].tolist()]

graph = ox.graph_from_bbox(boundaries[0], boundaries[1], boundaries[2], boundaries[3])   

nodes, edges = ox.graph_to_gdfs(graph)

fig, ax = plt.subplots(figsize=(15,15))
plt.title('HoReCa businesses in Amsterdam')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
edges.plot(ax=ax, linewidth=1, edgecolor='black', alpha=0.5)
nodes.plot(ax=ax, color='lightblue', markersize=5)

ax.scatter(longitudes_hotel, latitudes_hotel, c='g', label='hotel')
ax.scatter(longitudes_restaurant, latitudes_restaurant, c='b', label='restaurant')
ax.scatter(longitudes_cafe, latitudes_cafe, c='r', label='cafe')

#plot legend without duplicates
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())

#%% Export list of horeca business to excel

writer = pd.ExcelWriter('C:/Users/stijn/Dropbox/Stijn/Research Project/Python/03 Final models/Google API/Horeca_business_data.xlsx')
list_hotel.to_excel(writer, 'hotels', header=True, index=False)
list_restaurant.to_excel(writer, 'restaurants', header=True, index=False)
list_cafe.to_excel(writer, 'cafes', header=True, index=False)
writer.save()









 
