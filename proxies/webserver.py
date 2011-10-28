#!/usr/bin/python

import socket
import sys
import struct
import time
import os
import xsocket
from ctypes import *
import hashlib

chunksize = 1200
#CID = ['0000000000000000000000000000000000000000', '0000000000000000000000000000000000000001', '0000000000000000000000000000000000000010','0000000000000000000000000000000000000011','0000000000000000000000000000000000000100', '0000000000000000000000000000000000000101', '0000000000000000000000000000000000000110','0000000000000000000000000000000000000111','0000000000000000000000000000000000001000', '0000000000000000000000000000000000001001', '0000000000000000000000000000000000001010', '0000000000000000000000000000000000001011']
#cid_i = -1
length = 0

# Pretend a magic naming service gives us XIDs...
from xia_address import *

CID_SIMPLE_HTML = ""  # we set this when we 'put' the hmtl page
CID_DEMO_HTML = ""  # we set this when we 'put' the hmtl page

def putCID(chunk):
    #global cid_i
    #cid_i += 1

    # Hash the content to get CID
    m = hashlib.sha1()
    m.update(chunk)
    cid = m.hexdigest()

    sock = xsocket.Xsocket()
    if (sock<0):
        print "error opening socket"
        return
    
    # Put the content chunk
    content_dag = 'RE %s %s CID:%s' % (AD1, HID1, cid)
    xsocket.XputCID(sock, chunk, len(chunk), 0, content_dag, len(content_dag))

    print 'put content %s (length %s)' % (content_dag, len(chunk))
    xsocket.Xclose(sock)

    return cid

def serveSIDRequest(request, sock):
    # Respond with either CID_DEMO_HTML or CID_DEMO_HTML
    # TODO: This code should be better
    
    # To prevent cid referenced before assignment
    cid = CID_SIMPLE_HTML
    if request.find('simple.html') >= 0:
        cid = CID_SIMPLE_HTML
    elif request.find('xia.html') >= 0:  
        cid = CID_DEMO_HTML
    
    response = 'HTTP/1.1 200 OK\nDate: Sat, 08 Jan 2011 22:25:07 GMT\nServer: Apache/2.2.17 (Unix)\nAccess-Control-Allow-Origin: *\nCache-Control: no-cache\nConnection: close\nContent-Type: text/html\n\n'+ cid
    print 'Response:\n%s' % response
    xsocket.Xsend(sock, response, len(response), 0)
    return

def main():
    global AD1, HID1, SID1
    global length
    global CID_SIMPLE_HTML, CID_DEMO_HTML

    # Set up connection with click via Xsocket API
    xsocket.set_conf("xsockconf_python.ini", "webserver.py")
    xsocket.print_conf()  #for debugging

    # Put content 'image.jpg' and make a corresponding list of CIDs
    # (if image is chunked it might have multiple CIDs)
    image_cid_list = []
    f = open("image.jpg", 'r')
    chunk = f.read(chunksize)
    while chunk != '':
        image_cid_list.append(putCID(chunk))
        chunk = f.read(chunksize)
    f.close()

    # Build 'simple.html' file
    num_image_chunks = len(image_cid_list)
    image_cid_list_string = ''

    for cid in image_cid_list:
        image_cid_list_string += cid
    f = open("simple.html", 'w')
    f.write('<html><body><h1>It works!</h1>\n<h2><img src="http://xia.cid.%s.%s" /></h2><ul class="left-nav">\n\n</body></html>' % (num_image_chunks, image_cid_list_string))

    # Put content 'simple.html'
    # TODO: Silly to write file then read it again; we do it
    # for now so we can see the actual file for debugging
    print "simple.html"
    f = open("simple.html", 'r')
    chunk = f.read(chunksize)

    while chunk != '':
        cid = putCID(chunk)
        CID_SIMPLE_HTML += 'CID:' 
	CID_SIMPLE_HTML  += cid
        chunk = f.read(chunksize)
    f.close()
    print "end simple.html"

    # Put content 'demo.html'
    print "demo.html"
    f = open("demo.html", 'r')
    chunk = f.read(chunksize)

    while chunk != '':
        cid = putCID(chunk)
        CID_DEMO_HTML += 'CID:' 
	CID_DEMO_HTML  += cid
	CID_DEMO_HTML  += '\t'
        chunk = f.read(chunksize)
    f.close()
    
    print "end demo.html"
    
    # Put content 'plane.jpg'
    print "plane.jpg"
    f = open("plane.jpg", 'r')
    chunk = f.read(chunksize)

    while chunk != '':
        cid = putCID(chunk)
        chunk = f.read(chunksize)
    f.close()
    print "end plane.jpg"

    time.sleep(1) #necessary?

    # Now listen for connections from clients
    listen_sock = xsocket.Xsocket()
    if (listen_sock<0):
        print 'error opening socket'
        return
    dag = "RE %s %s %s" % (AD1, HID1, SID1) # dag to listen on
    xsocket.Xbind(listen_sock, dag)
    print 'Listening on %s' % dag

    while True:
        xsocket.Xaccept(listen_sock)
        incoming_data = xsocket.Xrecv(listen_sock, 1024, 0)
        print incoming_data
        serveSIDRequest(incoming_data, listen_sock)
    


if __name__ ==  '__main__':
    main()

