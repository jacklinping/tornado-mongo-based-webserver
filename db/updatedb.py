import mongo

mongo.feed.update({}, {'$set': 
    {'ua': '', 'email': ''}
    }, multi=True, safe=True)

