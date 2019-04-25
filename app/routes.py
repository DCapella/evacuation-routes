from flask import render_template, request, send_file, url_for, redirect

from app import app, db
from app.models import Address, NewsAPI, HereAPI, LiveTrafficTweets


@app.route('/', methods=['GET', 'POST'])
def index():
    texts = []
    flags = []
    traffic_tweets = []
    geo = {'lat': 0, 'long': 0}
    tweets=[]
    location=[]

    city_name = ''
    city_name_from = ''
    lat_2 = 0
    long_2 = 0
    alt_lat = []
    alt_long = []
    
    if request.form:
        threshold = Address.query.first()
        if threshold is not None:
            for t in Address.query.all():
                db.session.delete(t)

        address = Address(address=request.form.get('address'), address_from=request.form.get('address_from'))

        city_name = address.address
        city_name_from = address.address_from
        # news = NewsAPI()
        # texts = news.main(city_name)

        here = HereAPI()
        here.fit(city_name_from, city_name, 5)
        flags = here.flags
        geo['lat'] = here.lat_2
        geo['long'] = here.long_2
        print('='*100)
        print(here.lat_2)
        print(here.long_2)
        print('='*100)
        alt_lat = list(here.alt_lat)
        alt_long = list(here.alt_long)

        lat_2 = geo['lat']
        long_2 = geo['long']

        tweets_api = LiveTrafficTweets()
        tweets, location = tweets_api.traffic(city_name)

        db.session.add(address)
        db.session.commit()
    return render_template('index.html',
                            city_name=city_name,
                            city_name_from=city_name_from,
                            texts=texts,
                            flags=flags,
                            traffic_tweets=traffic_tweets,
                            geo=geo,
                            lat_2=lat_2,
                            long_2=long_2,
                            alt_lat=alt_lat,
                            alt_long=alt_long,
                            tweets=tweets,
                            location=location)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)