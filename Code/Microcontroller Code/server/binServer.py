#Import the Modules Required
import sys
import datetime
import pytz
import json
import argparse
from mclora import MCLoRa
from threading import Thread
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from numpy import interp, clip
import logging 

logging.basicConfig(level=logging.INFO)

TIME_ZONE = "Asia/Kolkata"

binMapping = {
	"25046B" : 1,
	"25046A" : 2
}

pnconfig = PNConfiguration()
 
pnconfig.subscribe_key = 'sub-c-62fed8bc-2d10-11e8-a27a-a2b5bab5b996'
pnconfig.publish_key = 'pub-c-002fbba1-6de1-410b-8c9e-ff75720aaa49'
 
pubnub = PubNub(pnconfig)

#System Variables
port = " "
loraM = " "

def my_publish_callback(envelope, status):
	# Check whether request successfully completed or not
	if not status.is_error():
		print "Successfully Sent"
		# Message successfully published to specified channel.
	else:
		pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];

class MySubscribeCallback(SubscribeCallback):
	def presence(self, pubnub, presence):
		pass  # handle incoming presence data
 	
	def status(self, pubnub, status):
		if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
			pass  # This event happens when radio / connectivity is lost
 
		elif status.category == PNStatusCategory.PNConnectedCategory:
			pass
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            # pubnub.publish().channel("awesomeChannel").message("hello!!").async(my_publish_callback)
		elif status.category == PNStatusCategory.PNReconnectedCategory:
			pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
		elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
			pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.
 
	def message(self, pubnub, message):
		print message

 
'''****************************************************************************************
Function Name 		:	obtain_port
Description			:	Obtain the Serial Port from argument 
Parameters 			:	none
****************************************************************************************'''
def obtain_port():
	global port
	#obtain the Port from the Argument 
	descStr = "Traffic Controller: Enter the LoRa Port"
	parser = argparse.ArgumentParser(description=descStr)
	parser.add_argument('--port', dest='serial_port', required=True)
	args = parser.parse_args()
	if args.serial_port:
		port = args.serial_port

def scale(value, src_min, src_max, dst_min, dst_max, round_=False):
    """
    Scale a value from one range to another.

    :param value: Input value
    :param src_min: Min value of input range
    :param src_max: Max value of input range
    :param dst_min: Min value of output range
    :param dst_max: Max value of output range
    :param round_: True if the scale value should be rounded to an integer

    :return: The scaled value
    """
    scaled = interp(clip(value, src_min, src_max), [src_min, src_max], [dst_min, dst_max])
    if round_:
        scaled = int(round(scaled))

    return scaled 

'''****************************************************************************************
Function Name 		:	loraReceive
Description			:	Receives the LoRa Data
Parameters 			:	none
****************************************************************************************'''
def loraReceive():
	global loraM, pubnub
	count  = 0
	while True:
		print "LoRa Packet Receive Start"
		try:
			loraData = str(loraM.recv())
			if loraData != "['radio_err']":
				loraList = loraData.split("2C")
				distanceReceived = scale(int(loraList[1],16), 0, 250, 100, 0)
				loraPacket = {
					"binId" : binMapping[loraList[0]],
					"binData" : {
						"fillLevel" : int(distanceReceived),
						"batteryLevel" : int(loraList[2],16), 
						"timeStamp": str(datetime.datetime.now(pytz.timezone(TIME_ZONE)).strftime('%m-%d %H:%M'))
					}
				}
				print loraPacket
				print pubnub.publish().channel("binData").message(loraPacket).async(my_publish_callback)
				# 25046B2C00B42C62
			else:
				print "No Data Received"

		except Exception as error:
			print error 

'''****************************************************************************************
Function Name 		:	systemInit
Description			:	Initiazie the LoRa and Twilio Client 
Parameters 			:	None
****************************************************************************************'''
def systemInit():
	global port, loraM, pubnub
	obtain_port()

	#loraM handles all the loraEvents 
	loraM = MCLoRa(port)
	success = loraM.testOK()
	if success:
		print "Bin Management Init Success"
		print (success)
	else:
		print("Bin Management Init Failure")
	loraM.pause()

	pubnub.add_listener(MySubscribeCallback())
	pubnub.subscribe().channels('binData').execute()

if __name__ == "__main__":
    systemInit()
    loraThread = Thread(target = loraReceive)
    loraThread.setDaemon(True)
    loraThread.start()

    print("Bin Management Started ...\n")

    while True:
        try:
            pass
        except KeyboardInterrupt:
            sys.exit(0)


#End of the Script 
##*****************************************************************************************************##
