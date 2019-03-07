from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

#http://0.0.0.0:8080
class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # message = ""
                # message += "<html><body>Hello!</body></html>"
                # self.wfile.write(message)
                # print message
                output = ""
                output += "<html><body>Hello!</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/edit"):
                id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter(Restaurant.id == id).one()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = "<html><head><meta charset='UTF-8'></head><body>"
                output += "<h1>Edit Restaurant</h1>"
                output += "<form method='post' enctype='multipart/form-data' action = '/restaurants/"+ str(restaurant.id) +"/edit'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Edit'>"
                output += "</form>"
                output += "<p>Current name: " + restaurant.name + "</p>"
                output += "</body></html>"
                self.wfile.write(output)            
                return

            if self.path.endswith("/delete"):
                
                    id = self.path.split("/")[2]
                    restaurant = session.query(Restaurant).filter(Restaurant.id == id).one()
                    session.delete(restaurant)
                    session.commit()                   

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()                   
                    return

            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                output = "<html><body><h1>restaurants</h1></br>"
                output += "<a href ='/restaurants/new'>Create a New Restaurant Here</a></br></br>"
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()           
                for restaurant in restaurants:
                    output += "<p>" + restaurant.name + "</p>"
                    output += "<p><a href ='restaurants/"+ str(restaurant.id) +"/edit'>" + "Edit" + "</a></p>"
                    output += "<p><a href='restaurants/"+ str(restaurant.id) +"/delete'>" + "Delete" + "</a></p>"
                output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = "<html><head><meta charset='UTF-8'></head><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method='post' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)            
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                
                    #Create new Restaurant class
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', 'restaurants')
                    self.end_headers()
                    return

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                
                if ctype == 'multipart/form-data':
                    id = self.path.split("/")[2]
                    restaurant = session.query(Restaurant).filter(Restaurant.id == id).one()
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                    restaurant.name = messagecontent[0]
                    session.add(restaurant)
                    session.commit()                   

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()                   
                    return

            
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()
