from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

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
        flash('Restaurant Edited')
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
        flash('New Restaurant Created')
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
        flash('restaurant deleted')
        return redirect(url_for('restaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant = restaurant)

@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):

    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash('New Menu Item Created', 'Success')
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
        flash("menu item edited!")
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
        flash(" menu item deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html',restaurant=restaurant, item = menuitem)

    #return "delete menu item"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug=True
    app.run(host = '0.0.0.0', port = 5000)