from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem
import cgi
import re

class RestaurantServerHandler(BaseHTTPRequestHandler):
    session = None
    
    def getSession(self):
        if self.session is None:
            engine = create_engine('sqlite:///restaurantmenu.db')
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            self.session = DBSession()
        return self.session

    def getRestaurantListHTML(self):
        result = self.getSession().query(Restaurant).all()
        html = ''
        html += '<html><body>'
        html += '<h2><a href="restaurants/new">Create new restaurant</a></h2>'
        for r in result:
            html += '<h2>' + r.name + '</h2>'
            html += '<a href="/restaurants/%s/edit">Edit</a> <a href="/restaurants/%s/delete">Delete</a>' % (r.id, r.id)
            html += '<br>'
        html += '</body></html>'

        return html
    
    def do_GET(self):
        try:
            if self.path.endswith('/restaurants'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = self.getRestaurantListHTML()
                self.wfile.write( html )
                print html

            elif self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = '<html><body>'
                html += '<h1>Create new restaurant</h1>'
                html += '''<form method="POST" enctype="multipart/form-data" action="/restaurants/new">
<h2>Enter new restaurant name</h2>
<input name="newRestaurant" type="text">
<input type="submit" value="Submit">
</form>
'''
                self.wfile.write(html)

            elif self.path.endswith('/edit'):
                id = self.path.split('/')[2]
                editRestaurant = self.getSession().query(Restaurant).filter_by(id = id).one()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = '<html><body>'
                html += '<h1>Rename %s</h1>' % editRestaurant.name
                html += '''<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/edit">
<h2>Enter new restaurant name</h2>
<input name="editRestaurant" type="text">
<input type="submit" value="Submit">
</form>
''' % id
                self.wfile.write(html)

            elif self.path.endswith('/delete'):
                id = self.path.split('/')[2]
                deleteRestaurant = self.getSession().query(Restaurant).filter_by(id = id).one()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = '<html><body>'
                html += '<h1>Delete %s?</h1>' % deleteRestaurant.name
                html += '''<form method="POST" enctype="multipart/form-data" action="restaurants/%s/delete">
<h2>Are you sure?</h2>
<input type="submit" value="Delete">
</form>
''' % id
                self.wfile.write(html)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                
                ctype, pdict = cgi.parse_header( self.headers.getheader('content-type') )
                
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurant')

                newRestaurant = Restaurant(name=messagecontent[0])
                session = self.getSession()
                session.add(newRestaurant)
                session.commit()
                
            elif self.path.endswith('/edit'):
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

                id = self.path.split('/')[2]

                ctype, pdict = cgi.parse_header( self.headers.getheader('content-type') )

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('editRestaurant')

                session = self.getSession()
                editRestaurant = session.query(Restaurant).filter_by(id = id).one()
                
                editRestaurant.name = messageContent[0]
                session.add(editRestaurant)
                session.commit()

            elif self.path.endswith('/delete'):
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

                id = self.path.split('/')[2]

                session = self.getSession()
                deleteRestaurant = session.query(Restaurant).filter_by(id = id).one()
                session.delete(deleteRestaurant)
                session.commit()
                
        except Exception as e:
            print type(e)
            print e.args
            print e
            pass


def main():
    try:
        port = 8080
        server = HTTPServer( ('', port), RestaurantServerHandler )
        print 'Restaurant server running on port %s' % port
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C entered, stopping web server...'
        server.socket.close()

if __name__ == '__main__':
    main()
