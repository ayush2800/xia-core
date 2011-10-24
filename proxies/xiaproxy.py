import socket, select
import struct, time, signal, os, sys
import xsocket
from ctypes import *

# Pretend a magic naming service givs us a dag for netloc...
HID0= "HID:0000000000000000000000000000000000000000"
HID1= "HID:0000000000000000000000000000000000000001"
AD0=  "AD:1000000000000000000000000000000000000000"
AD1=  "AD:1000000000000000000000000000000000000001"
RHID0="HID:0000000000000000000000000000000000000002"
RHID1="HID:0000000000000000000000000000000000000003"
CID0= "CID:2000000000000000000000000000000000000001"
SID1= "SID:0f00000000000000000000000000000000000055"


def check_for_and_process_CIDs(message, browser_socket):
    rt = message.find('CID') 
    print rt
    if (rt!= -1):
        http_header = message[0:rt]
        content = requestCID(message[rt+4:rt+44], True)
        browser_socket.send(content)
        return True
    return False

def sendSIDRequest(netloc, payload, browser_socket):
    print "in SID function - net location = " + netloc  

    sock = xsocket.Xsocket()
    if (sock<0):
        print "error opening socket"
        return

    dag = "RE %s %s %s" % (AD1, HID1, SID1) # Need a SID?

    # Connect to service
    xsocket.Xconnect(sock, dag)
    # Send request
    xsocket.Xsend(sock, payload, len(payload), 0)
    # Receive reply
    reply = xsocket.Xrecv(sock, 1024, 0)
    xsocket.Xclose(sock)
    # Pass reply up to browswer if it's a normal HTTP message
    # Otherwise request the CIDs
    contains_CIDs = check_for_and_process_CIDs(reply, browser_socket)
    if not contains_CIDs:
        browser_socket.send(reply)
    
    return

def requestCID(CID, fallback):
    # TODO: fix issue where bare CIDs crash click
    print "in getCID function"  
    print CID

    sock = xsocket.Xsocket()
    if (sock<0):
        print "error opening socket"
        return

    # Request content
    content_dag = 'CID:%s' % CID
    if fallback:
        content_dag = 'RE %s %s %s' % (AD1, HID1, content_dag)
    print 'Retrieving content with ID: \n%s' % content_dag
    xsocket.XgetCID(sock, content_dag, len(content_dag))

    # Get content
    data = xsocket.Xrecv(sock, 1024, 0)
    print 'Retrieved content:\n%s' % data

    xsocket.Xclose(sock)

    return data


def xiaHandler(control, payload, browser_socket):
    xsocket.set_conf("xsockconf_python.ini", "xiaproxy.py")
    xsocket.print_conf()  #for debugging

    if payload.find('GET /favicon.ico') != -1:
                    return
    print "in XIA code\n" + control + "\n" + payload
    control=control[4:]  # remove the 'xia.' prefix
    if control.find('sid') == 0:
        print "SID request"
        print "%.6f" % time.time()
        if control.find('image.jpg') != -1: # TODO: why?
            payload = 'image.jpg'
        sendSIDRequest(control[4:], payload, browser_socket);
    elif control.find('cid') == 0:
        print "cid request"
        num = int(control[4])
        print "num %d" % num
       
        # The browser might be requesting a list of chunks; if so, we'll recombine them into one object
        recombined_content = ''
        for i in range (0, num):
            recombined_content += requestCID(control[6+i*40+i:46+i*40+i], True)  #TODO: don't require fallback
            
        length = len (recombined_content)
        print "recombined_content length %d " % length
        #header = 'HTTP/1.1 200 OK\nETag: "48917-39ed-4990ddae564c"\nAccept-Ranges: bytes\nContent-Length: ' + str(length) + '\nContent-Type: image/jpeg\n\n'  # todo: avoid hard code 
        #header = 'HTTP/1.1 200 OK\nAccept-Ranges: bytes\nCache-Control: no-cache\nContent-Length: 14829\nContent-Type: image/jpeg\n\n'  # todo: avoid hard code 
        #header2 = ''
        #payload_http =  recombined_content

        browser_socket.send(recombined_content)
    return;

