#Very simple url shortener service
#Doesn't save the shortened urls so it will lose them on service shutdown
#Shortened urls use only 0-9,A-Z,a-z ASCII characters
#
#to shorten urls POST to \shorten with url as 
#Created by Miki Tolonen, splyysh@IRCnet

import http.server as BaseHTTPServer
#functions to parse correct path and query string from url
from urllib.parse import urlparse, parse_qs


PORT = 6660
HOST = "localhost"


#gives the next character from blocks 0-9,A-Z,a-z
def nextChar(char):
  if(char=='9'):
    return 'A'
  elif(char=='Z'):
    return 'a'
  elif(char=='z'):
    return '0'
  else:
    return chr(ord(char)+1)

#gives the next url that is as short as possible
#Urls consist only from ASCII characters 0-9,A-Z,a-Z
def nextUrl(current):
  next=""
  i=0
  #loop over the str
  for i in range(len(current)):
    next += nextChar(current[i])
    #if current character wasn't z, doesn't need to loop forward
    if(current[i]!='z'):
      break
  next += current[i+1:]
  #if the string is all zeroes, string needs to grow
  if(next=="0"*len(next)):
    next+="0"
  return next

#handler for url requests
class shortenerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  #static variables, as they need to be consistent while running.
  #Doesn't check that 2 urls cannot be created at the same key if processes overlap
  #Haven't checked whether BaseHTTPServer does create new processes for each request, so potential risk
  shortenedUrls={}
  lastUrl="0"

  def do_POST(self):
    parsed = urlparse(self.path)
    link = False
    path = parsed.path
    if("application/x-www-form-urlencoded" in self.headers.get("content-type")):
      #check content length for reading
      length = int(self.headers.get('content-length'))
      #read xform variables, try to find first link, as parse_qs produces list of all
      #parse_qs will produce library with query variable names as keys and list of values
      link = parse_qs(self.rfile.read(length).decode('utf-8'), keep_blank_values=1).get("link",[False])[0]
    if(path=="/shorten" and link):
      shortenerHandler.lastUrl = nextUrl(self.lastUrl)
      shortenerHandler.shortenedUrls[shortenerHandler.lastUrl]=link
      self.send_response(200)
      self.send_header("Content-type","text/plain")
      self.end_headers()
      self.wfile.write(shortenerHandler.lastUrl.encode("utf8"))
    #if the POST path wasn't correct, or link parameter wasn't given
    else:
      self.send_error(404)
  def do_GET(self):
    parsed = urlparse(self.path)
    #parse only the path part without even "/"
    path = parsed.path[1:]
    if(path in shortenerHandler.shortenedUrls):
      self.send_response(301)
      self.send_header("Location", shortenerHandler.shortenedUrls[path])
      self.end_headers()
    else:
      self.send_error(404)

if __name__ == '__main__':
  #if file run, run server until interrupted for clean exit
  httpd = BaseHTTPServer.HTTPServer((HOST,PORT), shortenerHandler)
  print("Server started")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    pass
  httpd.server_close()
  print("Server closed")