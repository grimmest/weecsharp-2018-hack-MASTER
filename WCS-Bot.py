#!/usr/bin/python
#test

import json
import socket
import logging
import binascii
import struct
import argparse
import random
import time
import math

class ServerMessageTypes(object):
	TEST = 0
	CREATETANK = 1
	DESPAWNTANK = 2
	FIRE = 3
	TOGGLEFORWARD = 4
	TOGGLEREVERSE = 5
	TOGGLELEFT = 6
	TOGGLERIGHT = 7
	TOGGLETURRETLEFT = 8
	TOGGLETURRETRIGHT = 9
	TURNTURRETTOHEADING = 10
	TURNTOHEADING = 11
	MOVEFORWARDDISTANCE = 12
	MOVEBACKWARSDISTANCE = 13
	STOPALL = 14
	STOPTURN = 15
	STOPMOVE = 16
	STOPTURRET = 17
	OBJECTUPDATE = 18
	HEALTHPICKUP = 19
	AMMOPICKUP = 20
	SNITCHPICKUP = 21
	DESTROYED = 22
	ENTEREDGOAL = 23
	KILL = 24
	SNITCHAPPEARED = 25
	GAMETIMEUPDATE = 26
	HITDETECTED = 27
	SUCCESSFULLHIT = 28
    
	strings = {
		TEST: "TEST",
		CREATETANK: "CREATETANK",
		DESPAWNTANK: "DESPAWNTANK",
		FIRE: "FIRE",
		TOGGLEFORWARD: "TOGGLEFORWARD",
		TOGGLEREVERSE: "TOGGLEREVERSE",
		TOGGLELEFT: "TOGGLELEFT",
		TOGGLERIGHT: "TOGGLERIGHT",
		TOGGLETURRETLEFT: "TOGGLETURRETLEFT",
		TOGGLETURRETRIGHT: "TOGGLETURRENTRIGHT",
		TURNTURRETTOHEADING: "TURNTURRETTOHEADING",
		TURNTOHEADING: "TURNTOHEADING",
		MOVEFORWARDDISTANCE: "MOVEFORWARDDISTANCE",
		MOVEBACKWARSDISTANCE: "MOVEBACKWARDSDISTANCE",
		STOPALL: "STOPALL",
		STOPTURN: "STOPTURN",
		STOPMOVE: "STOPMOVE",
		STOPTURRET: "STOPTURRET",
		OBJECTUPDATE: "OBJECTUPDATE",
		HEALTHPICKUP: "HEALTHPICKUP",
		AMMOPICKUP: "AMMOPICKUP",
		SNITCHPICKUP: "SNITCHPICKUP",
		DESTROYED: "DESTROYED",
		ENTEREDGOAL: "ENTEREDGOAL",
		KILL: "KILL",
		SNITCHAPPEARED: "SNITCHAPPEARED",
		GAMETIMEUPDATE: "GAMETIMEUPDATE",
		HITDETECTED: "HITDETECTED",
		SUCCESSFULLHIT: "SUCCESSFULLHIT"
	}
    
	def toString(self, id):
		if id in self.strings.keys():
			return self.strings[id]
		else:
			return "??UNKNOWN??"


class ServerComms(object):
	'''
	TCP comms handler
	
	Server protocol is simple:
	
	* 1st byte is the message type - see ServerMessageTypes
	* 2nd byte is the length in bytes of the payload (so max 255 byte payload)
	* 3rd byte onwards is the payload encoded in JSON
	'''
	ServerSocket = None
	MessageTypes = ServerMessageTypes()
	
	
	def __init__(self, hostname, port):
		self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ServerSocket.connect((hostname, port))
	
	def readMessage(self):
		'''
		Read a message from the server
		'''
		messageTypeRaw = self.ServerSocket.recv(1)
		messageLenRaw = self.ServerSocket.recv(1)
		messageType = struct.unpack('>B', messageTypeRaw)[0]
		messageLen = struct.unpack('>B', messageLenRaw)[0]
		
		if messageLen == 0:
			messageData = bytearray()
			messagePayload = None
		else:
			messageData = self.ServerSocket.recv(messageLen)
			logging.debug("*** {}".format(messageData))
			messagePayload = json.loads(messageData.decode('utf-8'))
			
		logging.debug('Turned message {} into type {} payload {}'.format(
			binascii.hexlify(messageData),
			self.MessageTypes.toString(messageType),
			messagePayload))
		return messagePayload
		
	def sendMessage(self, messageType=None, messagePayload=None):
		'''
		Send a message to the server
		'''
		message = bytearray()
		
		if messageType is not None:
			message.append(messageType)
		else:
			message.append(0)
		
		if messagePayload is not None:
			messageString = json.dumps(messagePayload)
			message.append(len(messageString))
			message.extend(str.encode(messageString))
			    
		else:
			message.append(0)
		
		logging.debug('Turned message type {} payload {} into {}'.format(
			self.MessageTypes.toString(messageType),
			messagePayload,
			binascii.hexlify(message)))
		return self.ServerSocket.send(message)


# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
parser.add_argument('-H', '--hostname', default='127.0.0.1', help='Hostname to connect to')
parser.add_argument('-p', '--port', default=8052, type=int, help='Port to connect to')
parser.add_argument('-n', '--name', default='RandomBot', help='Name of bot')
args = parser.parse_args()

# Set up console logging
if args.debug:
	logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.DEBUG)
else:
	logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)


# Connect to game server
GameServer = ServerComms(args.hostname, args.port)

# Spawn our tank
logging.info("Creating tank with name '{}'".format(args.name))
GameServer.sendMessage(ServerMessageTypes.CREATETANK, {'Name': args.name})

#key functions
def GetHeading(x1,y1,x2,y2):
	heading = math.degrees(math.atan2(y2-y1,x2-x1))
	heading = (heading - 360) % 360
	#print(heading)
	return int(abs(heading))
	
def GetDistance(x1,y1,x2,y2):
	displacement_x=x2-x1
	displacement_y=y2-y1
	return math.sqrt(displacement_x**2 + displacement_y**2)
	
# Main loop - read game messages, ignore them and randomly perform actions
i=0
names = []
xpos = 0
ypos = 0
enemyxpos = 0
enemyypos = 0
healthxpos=0
healthypos=0
enemies = []
while True:

	message = GameServer.readMessage()
	

	logging.info(message)
	if type(message) == dict:
		print(message)
		if ("Name" in message) and (message["Name"] == 'RandomBot'):
			xpos = message["X"]
			ypos = message["Y"]
		if ("Name" in message) and (message["Type"] == 'Tank') and (message['Name'] != 'RandomBot'):
			enemyname = message["Name"]
			enemyxpos = message["X"]
			enemyypos = message['Y']
			if enemyname in enemies:
				enemies[1] = enemyname
			badguy = [enemyname,enemyxpos,enemyypos]
			#print(enemies)
			enemies.append(badguy)
		if ("Name" in message) and (message["Type"] == 'HealthPickup') and (message['Name'] != 'RandomBot'):
			healthxpos= message['X']
			healthypos=message['Y']

			

			#print(healthxpos)
			#print(healthypos)
		if  ("Name" in message) and (message['Name']=='RandomBot') and  (message['Health']<3):
			
			heading_to_health=GetHeading(xpos,ypos,healthxpos,healthypos)
			distance_to_health=GetDistance(xpos,ypos,healthxpos,healthypos)

			#type(message['HealthPickup'])			

			logging.info("Moving to health pack")
			#while ("Name" in message) and (message['HealthPickup'] != True) :
			GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {"Amount": heading_to_health})
			GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': distance_to_health})
			
		else:
			'''logging.info("Turn 360 degree")
			GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {"Amount": 90})
			GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {"Amount": 90})
			GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {"Amount": 90})
			GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {"Amount": 90})'''
			#print('test')
			heading = GetHeading(xpos,ypos,enemyxpos,enemyypos)
			GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {"Amount": heading})
			#print(enemies)
			#if i == 10:
			#	logging.info("Turning randomly")
			#	GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': random.randint(0, 359)})
			#elif i == 15:
			#	logging.info("Moving randomly")
			GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {"Amount": i})
			GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 100})
			i = i + 5
			if i > 360:
				i = 0




	