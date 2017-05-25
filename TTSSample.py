#! /usr/bin/env python3

# -*- coding: utf-8 -*-

###
#Copyright (c) Microsoft Corporation
#All rights reserved. 
#MIT License
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the ""Software""), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# build on ubuntu 16.04
# requires pydub: pip3 install pydub
# and ffmpeg

###
import http.client, urllib.parse, json
import time
import os
from xml.etree import ElementTree
from pydub import AudioSegment

#Note: The way to get api key:
#Free: https://www.microsoft.com/cognitive-services/en-us/subscriptions?productId=/products/Bing.Speech.Preview
#Paid: https://portal.azure.com/#create/Microsoft.CognitiveServices/apitype/Bing.Speech/pricingtier/S0
apiKey = ""

def getToken(apiKey):
	# Connect to server to get the Access Token
	print ("Connect to server to get the Access Token")
	AccessTokenHost = "api.cognitive.microsoft.com"
	path = "/sts/v1.0/issueToken"
	params = ""
	headers = {"Ocp-Apim-Subscription-Key": apiKey}
	conn = http.client.HTTPSConnection(AccessTokenHost)
	conn.request("POST", path, params, headers)
	response = conn.getresponse()
	print(response.status, response.reason)
	data = response.read()
	conn.close()
	accesstoken = data.decode("UTF-8")
	return accesstoken;

def getWAV(accesstoken,text):
	body = ElementTree.Element('speak', version='1.0')
	body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
	voice = ElementTree.SubElement(body, 'voice')
	voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
	voice.set('{http://www.w3.org/XML/1998/namespace}gender', 'Female')
	voice.set('name', 'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)')
	voice.text = text

	headers = {"Content-type": "application/ssml+xml", 
				"X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm", 
				"Authorization": "Bearer " + accesstoken, 
				"X-Search-AppId": "07D3234E49CE426DAA29772419F436CA", 
				"X-Search-ClientID": "1ECFAE91408841A480F00935DC390960", 
				"User-Agent": "TTSForPython"}
	#Connect to server to synthesize the wave
	#print ("\nConnect to server to synthesize the wave")
	conn = http.client.HTTPSConnection("speech.platform.bing.com")
	conn.request("POST", "/synthesize", ElementTree.tostring(body), headers)
	response = conn.getresponse()
	print(response.status, response.reason)
	data = response.read()
	conn.close()
	print("The synthesized wave length: %d" %(len(data)))
	print("Forcing sleep to ensure api TOS")
	time.sleep(0.2); #5 Requests per second for free / 20 for paid
	return data;

accesstoken = getToken(apiKey);
print ("Access Token: " + accesstoken)
print ("Input.txt read and split.")
text_file= open("input.txt",'r')
data=text_file.read()
listOfSentences = data.split(".")
print ("Create empty mp3.")
track = AudioSegment.empty()
print ("Looping Input...")
for idx,sentence in enumerate(listOfSentences):
	print("Convert Sentence: %s" % sentence)
	data = getWAV(accesstoken,sentence + ".");
	tmpfile = open("tmp-"+str(idx)+".wav","wb")
	tmpfile.write(data)
	tmpfile.close()
	print("typecast to audio segment")
	spokensentence = AudioSegment.from_file("tmp-"+str(idx)+".wav", format="wav")
	print("append to track")
	track += spokensentence
	print("delete tmp file")
	os.remove("tmp-"+str(idx)+".wav")

print ("concatenating parts and converting to mp3")
track.export("result.mp3", format="mp3", bitrate="192k")


#	file = open("result.mp3","wb")
#	file.write(data)
#	file.close()
