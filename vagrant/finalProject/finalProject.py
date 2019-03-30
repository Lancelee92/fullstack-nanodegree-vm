from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

#NEW IMPORTS FOR THIS STEP
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import OAuth2Credentials
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def restaurants():
    restaurants = session.query(Restaurant)
    return render_template('restaurants.html', restaurants=restaurants)
    #return "this is my homepage with list of restaurant!"

@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE = state)
	#return "The cuurent session state is %s" %login_session['state']

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #check if the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    #if there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps('error.'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    #verify that the access token is for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID does not match given user ID."), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    
    #Store the access token in the session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    #Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'], 'positive')

    return output

@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuitem = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return render_template('restaurantMenu.html', menus = menuitem, restaurant = restaurant)

    
    #return "specific restaurant and menu"

@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    if request.method == 'POST':
        restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash('Restaurant Edited', 'positive')
        return redirect(url_for('restaurants'))
    else:
        return render_template('editRestaurant.html', restaurant = restaurant)
    #return "edit restaurant"

@app.route('/restaurants/new', methods=['GET','POST'])
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(name = request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash('New Restaurant Created', 'positive')
        return redirect(url_for('restaurants'))
    else:
        return render_template('newRestaurant.html')
    #return "create new restaurant"

@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash('restaurant deleted', 'negative')
        return redirect(url_for('restaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant = restaurant)

@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):

    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash('New Menu Item Created', 'positive')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newMenuItem.html', restaurant_id = restaurant_id)
    #return "create new menu item"

@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/edit', methods = ['GET','POST'])
def editMenuItem(restaurant_id, item_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).filter_by(id = item_id).one()

    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = request.form['price']
        session.add(item)
        session.commit()
        flash("menu item edited!", 'positive')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editMenuItem.html',restaurant=restaurant, menu = item)

    #return "edit menu item"

@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id, item_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuitem = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).filter_by(id = item_id).one()
    
    if request.method == 'POST':
        session.delete(menuitem)
        session.commit()
        flash(" menu item deleted!", 'negative')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html',restaurant=restaurant, item = menuitem)

    #return "delete menu item"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug=True
    app.run(host = '0.0.0.0', port = 5000)