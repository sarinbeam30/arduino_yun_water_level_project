#!/usr/bin/python
# This is the Python2 code !! 
from time import localtime
import socket, time, os, json, random
import paho.mqtt.client as mqtt

YUN_LOCAL= "localhost"    # local address to connect to Arduino
YUN_PORT = 6571           # local port to connect to Arduino
YUN_SOCK_TIMEOUT = 20     # socket timeout, in seconds


########### -------------- MQTT SECTION ------------------ ****************
# MQTT Initialize
MQTT_BROKER_URL = "hairdresser.cloudmqtt.com"
MQTT_BROKER_PORT = 17758
MQTT_BROKER_SSL = 27758
MQTT_BROKER_USER = "odbyktmn"
MQTT_BROKER_PWD = "9esnfcLYs5wF"
mqtt.Client.connected_flag=False
client = mqtt.Client("P1")

########### -------------- DATA SECTION ------------------ ****************
# MQTT DATA Initialize
MQTT_TOPIC_ID_OF_SENSOR = "#SENSOR"
MQTT_MSG_LARDKABANG_ID_OF_SENSOR = "1"
MQTT_MSG_BANGKAPI_ID_OF_SENSOR = "2"

MQTT_TOPIC_VALUE = "VALUE"
MQTT_TOPIC_DATE_AND_TIME = "DATE_AND_TIME"

MQTT_TOPIC_LATITUDE = "LATITUDE"
MQTT_MSG_LADKABANG_LATITUDE = "13.7299"
MQTT_MSG_BANGKAPI_LATITUDE = "13.7628"

MQTT_TOPIC_LONGTITUDE = "LONGITUDE"
MQTT_MSG_LARKRABANG_LONGTITUDE = "100.7783"
MQTT_MSG_BANGKAPI_LONGTITUDE = "100.6456"

MQTT_TOPIC_LOCATION = "LOCATION"
MQTT_MSG_LADKRABANG_LOCATION = "KMITL"
MQTT_MSG_BANGKAPI_LOCATION = "BANGKAPI"


########### -------------- DICT SECTION ------------------ ****************
node_1 = node_2 = {}
node_1_dict = node_2_dict = {}


def ConnectToConsole():
  counter = 0
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  while True:
    try:
      destination = (YUN_LOCAL,YUN_PORT)
      sock.connect( destination )
      sock.settimeout( YUN_SOCK_TIMEOUT )
      print("Connected to arduino")
      return sock
    except Exception as e:
      counter += 1
      print ("Error attempt # ", counter, e)
      time.sleep( 1 )
      if counter >= 5:
        print ("Resetting the MCU")
        os.system("reset-mcu")
        time.sleep( 5 )
        counter = 0

def ReadResponse(sock):
  msg = ""
  while True:
    c = sock.recv(1)
    msg = msg + c
    if c == '\n':
      return msg

def on_connect(client, userdata, flags, rc):
  if rc == 0:
    client.connected_flag = True
    print("MQTT CONNECTED")
  else:
    print("Bad connection Returned code=",rc)  

def connect_to_mqtt_broker():
  client.on_connect = on_connect
  client.username_pw_set(username=MQTT_BROKER_USER, password=MQTT_BROKER_PWD)
  client.connect(MQTT_BROKER_URL,port=MQTT_BROKER_PORT,keepalive=60)
  print("CONNECT_TO_BROKER_SUCCESS")

def setLocalTime():
  localtime_str = time.strftime("%d/%m/%Y %H:%M:%S", localtime())
  return str(localtime_str)

def get_water_level():
  s = ConnectToConsole()
  response = ReadResponse(s)
  return str(response)[:-2]

def generate_water_level():
  return random.randint(1,100)

def create_Json_file_node_1():
  node_1 = {}
  node_1[MQTT_TOPIC_ID_OF_SENSOR] = MQTT_MSG_LARDKABANG_ID_OF_SENSOR
  node_1[MQTT_TOPIC_VALUE] = get_water_level()
  node_1[MQTT_TOPIC_DATE_AND_TIME] = setLocalTime()
  node_1[MQTT_TOPIC_LATITUDE] = MQTT_MSG_LADKABANG_LATITUDE
  node_1[MQTT_TOPIC_LONGTITUDE] = MQTT_MSG_LARKRABANG_LONGTITUDE
  node_1[MQTT_TOPIC_LOCATION] = MQTT_MSG_LADKRABANG_LOCATION

  node_1_dict = json.dumps(node_1)
  return node_1_dict

def create_Json_file_node_2():
  node_2 = {}
  node_2[MQTT_TOPIC_ID_OF_SENSOR] = MQTT_MSG_BANGKAPI_ID_OF_SENSOR
  node_2[MQTT_TOPIC_VALUE] = generate_water_level()
  node_2[MQTT_TOPIC_DATE_AND_TIME] = setLocalTime()
  node_2[MQTT_TOPIC_LATITUDE] = MQTT_MSG_BANGKAPI_LATITUDE
  node_2[MQTT_TOPIC_LONGTITUDE] = MQTT_MSG_BANGKAPI_LONGTITUDE
  node_2[MQTT_TOPIC_LOCATION] = MQTT_MSG_BANGKAPI_LOCATION

  node_2_dict = json.dumps(node_2)
  return node_2_dict


def mqtt_publish_encoding(topic_name, value):
  mqtt_topic = "{}".format(topic_name)
  print(str(mqtt_topic) + " : " + str(value))
  time.sleep(2)
  client.publish(topic=topic_name, payload=value, qos=1, retain=True)

def mqtt_publish():
  try:
    while True:
      print("\nPublishing....")
      time.sleep(5)
      mqtt_publish_encoding("/BOARD_1", create_Json_file_node_1())
      time.sleep(2)
      mqtt_publish_encoding("/BOARD_2", create_Json_file_node_2())
      time.sleep(1)
      print("Publish : Done\n")
      time.sleep(3)
  finally:
    client.disconnect()
    print("Disconnected from MQTT server.")

def main():
  
  #MQTT_PART
  connect_to_mqtt_broker()

  while (1):
    mqtt_publish()
    # response = ReadResponse(s)
    # client.publish("WATER_LEVEL_MQTT", str("LEVEL") + response)
    # print("PUBLISH_LEAW_NA")
    # time.sleep(1)   
 
if __name__ == "__main__":
  main()
