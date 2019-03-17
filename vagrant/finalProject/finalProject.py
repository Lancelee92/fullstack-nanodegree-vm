from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def restaurants():
    restaurants = session.query(Restaurant)
    return render_template('restaurants.html', restaurants=restaurants)
    #return "this is my homepage with list of restaurant!"

@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    menuitem = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    return render_template('restaurantMenu.html', menus = menuitem, restaurant = restaurant)
    #return "specific restaurant and menu"

@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    if request.method == 'POST':
        restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
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
        return redirect(url_for('restaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant = restaurant)

@app.route('/restaurants/<int:restaurant_id>/new')
def newMenuItem(restaurant_id):
    return "create new menu item"

@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/edit')
def editMenuItem(restaurant_id, item_id):
    return "edit menu item"

@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/delete')
def deleteMenuItem(restaurant_id, item_id):
    return "delete menu item"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug=True
    app.run(host = '0.0.0.0', port = 5000)