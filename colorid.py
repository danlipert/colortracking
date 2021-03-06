import cv2
import numpy as np
import simplejson
import colorsys

def getthresholdedimg(hsv, objects):
    thresholds = None
    for eachObject in objects:
        lowerLimit = (eachObject['lowerLimit']['h'], eachObject['lowerLimit']['s'], eachObject['lowerLimit']['v'])
        upperLimit = (eachObject['upperLimit']['h'], eachObject['upperLimit']['s'], eachObject['upperLimit']['v'])     
        objectRange = cv2.inRange(hsv, np.array(lowerLimit), np.array(upperLimit))
        if thresholds == None:
            thresholds = objectRange
        else:
            thresholds = cv2.add(thresholds, objectRange)
    return thresholds

def averageHSV(objectDictionary):
    o = objectDictionary
    return ((o['lowerLimit']['h'] + o['upperLimit']['h']) / 2, (o['lowerLimit']['s'] + o['upperLimit']['s'])/2, (o['lowerLimit']['v'] + o['upperLimit']['v'])/2)

c = cv2.VideoCapture('/home/dan/hyperlayer/colortrack/IMG_0059.MOV')
width,height = c.get(3),c.get(4)
print "frame width and height : ", width, height

# load objects
file_handler = open('./data/IMG_0059/objects.json')
data = simplejson.load(file_handler)
file_handler.close()
objects = data["data"]

while(1):
    _,f = c.read()
    f = cv2.flip(f,1)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    thresholded = getthresholdedimg(hsv, objects)
    erode = cv2.erode(thresholded,None,iterations = 3)
    dilate = cv2.dilate(erode,None,iterations = 10)

    contours,hierarchy = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        cx,cy = x+w/2, y+h/2
        
        for eachObject in objects:
            if eachObject['lowerLimit']['h'] < hsv.item(cy, cx, 0) < eachObject['upperLimit']['h']:
                hue, sat, val = averageHSV(eachObject)
                rgb = colorsys.hsv_to_rgb(hue/180.0, sat/255.0, val/255.0)
                bgr = (rgb[2]*255, rgb[1]*255, rgb[0]*255)
                cv2.rectangle(f, (x, y), (x+w, y+h), bgr, 2)
                cv2.putText(f, eachObject['name'], (x-5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, bgr)
        
    cv2.imshow('img',f)

    if cv2.waitKey(25) == 27:
        break

cv2.destroyAllWindows()
c.release()
