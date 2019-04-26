# Evacuation Routes

Optimizing Evacuation Routes using Real-Time Traffic Information

## Problem Statement

#### [New Light Technologies](https://www.newlight.com/)

> During disasters, search and rescue teams must be able to search for and get to survivors as fast as possible (in terms of travel time and distance). Current GIS and navigation systems allow responders to calculate travel time and distance between origin and destination and propose an optimal route to the destination. However, many of the current platforms do not rely on real-time data (e.g. road closures, damaged roads etc.) and can produce inaccurate or inefficient results. This project will leverage social media, news feeds and other datasets (e.g. Waze, Here.com) to identify real time road closures or damaged roads, power outages and other blocked routes that may affect traffic lights, travel time, travel safety and more.The system should allow the user (the public or rescue teams) to search for any of these conditions and identify if and where they exist in a specific location (street, neighborhood, city etc.)


## Gathering Data

#### [David Capella](http://davidcapella.com)

> I built a module that interacts with the [HereAPI](https://www.here.com/) for alternative route geolocations and already known flags in the area for each of those alternative routes. In addition, I constructed another module that interacts with the [NewsAPI](https://newsapi.org/) that will gather links according to a search query of a city. Upon gathering the links I scrapped each of those websites and kept anything that had to do with road (or other related words). Then as an added part if it had something to do with closure or danger of some sort. Finally, using the micro web framework, [Flask](http://flask.pocoo.org/), I put my team's modules intergrated together to create a web application. I also had to have Python interact with JavaScript in order for the [MapQuestAPI](https://www.mapquest.com/) to work. 

## Modeling

#### [David Capella](http://davidcapella.com)

> In my part I had no real model. I used word2vec but eventually I would like to create a model that would effortlessly decide what's relevant in order to make the speed faster and take only specific sentences that are neccessary.

## Results

#### [David Capella](http://davidcapella.com)

> In order to run our final pre-deployed project, you need to do a couple of steps:
> * Fork this git repo into your own.
> * Place it somewhere
> `git clone repo`
> * Go into it
> `cd evacuation-routes`
> * Execute it
> `python evacuation_routes.py`
> * Then go to the port it specifies; most likey will be port: http://127.0.0.1:5000

## Built With

* Jupyter Notebook
* Python
* Flask
* JavaScript

## Authors

#### [Haya Toumy](https://hayatoumy.github.io/hayatoumy/)
#### [Christopher Hutchins](https://github.com/cfarhutchins)
#### [Xlegic SinAustin](https://www.linkedin.com/in/xlegic-howard-sin-austin-b64170163/)
#### [David Capella](http://davidcapella.com)

## Acknowledgments

* [NewsAPI](https://newsapi.org/)
* [Here API](https://developer.here.com/)
* Tweepy
* MapQuest API
