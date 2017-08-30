from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

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
        for r in result:
            html += '<h2>' + r.name + '</h2>'
            html += '<a href="#">Edit</a> <a href="#">Delete</a>'
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

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


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
