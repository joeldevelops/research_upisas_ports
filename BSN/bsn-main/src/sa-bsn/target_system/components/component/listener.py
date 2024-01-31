#!/usr/bin/env python

import numpy as np
import rospy
import roslib.message as ros_msg
from rospy.msg import AnyMsg
import json
import requests
from genson import SchemaBuilder
from flask import Flask, jsonify, request
from publisher import publisher

app = Flask(__name__)
app.register_blueprint(publisher)
database = {}


def monitor_get():
    return json.loads(json.dumps(database))

def monitor_get_schema():
    builder = SchemaBuilder()
    builder.add_object(monitor_get())
    return builder.to_schema()


def adaptation_options_get():
    return json.loads(json.dumps({
            "topic": [
                "/reconfigure_/g3t1_1",
                "/reconfigure_/g3t1_2",
                "/reconfigure_/g3t1_3",
                "/reconfigure_/g3t1_4",
                "/reconfigure_/g3t1_5", 
                "/reconfigure_/g3t1_6"], 
            "target": [
                "g3t1_1", 
                "g3t1_2", 
                "g3t1_3", 
                "g3t1_4", 
                "g3t1_5", 
                "g3t1_6"],
            "action": "freq=[0.0-1.0]"
        }))

def adaptation_options_schema_get():
    builder = SchemaBuilder()
    builder.add_object(adaptation_options_get())
    return builder.to_schema()


@app.route('/monitor_schema', methods=['GET'])
def monitor_schema():
    try:
        return monitor_get_schema()
    except json.decoder.JSONDecodeError as e:
        print("Error decoding JSON data:", e)
        return 'Invalid JSON data', 400

    except Exception as e:
        # Logerror for debugging
        print("Error processing request: {}".format(e))
        return 'Internal Server Error', 500


@app.route('/monitor', methods=['GET'])
def monitor():
    try:
        return jsonify(monitor_get())

    except json.decoder.JSONDecodeError as e:
        print("Error decoding JSON data:", e)
        return 'Invalid JSON data', 400

    except Exception as e:
        # Logerror for debugging
        print("Error processing request: {}".format(e))
        return 'Internal Server Error', 500


@app.route('/adaptation_options_schema', methods=['GET'])
def adaptation_options_schema():
    try:
        return jsonify(adaptation_options_schema_get())

    except json.decoder.JSONDecodeError as e:
        print("Error decoding JSON data:", e)
        return 'Invalid JSON data', 400

    except Exception as e:
        # Logerror for debugging
        print("Error processing request: {}".format(e))
        return 'Internal Server Error', 500


@app.route('/adaptation_options', methods=['GET'])
def adaptation_options():
    try:
        return jsonify(adaptation_options_get())

    except json.decoder.JSONDecodeError as e:
        print("Error decoding JSON data:", e)
        return 'Invalid JSON data', 400

    except Exception as e:
        # Logerror for debugging
        print("Error processing request: {}".format(e))
        return 'Internal Server Error', 500


@app.route('/', methods=['GET'])
def index():
    return 'OK', 200


class AnyMsgSubscriber: 
    def __init__(self, topic):
        self.sub = rospy.Subscriber(topic, AnyMsg, self.callback)
        self.topic = topic
  
    # Callback function which stores the data from each ros topic in a dictionary
    def callback(self, msg): 
        msg_type = msg._connection_header['type'].split('/')
        msg_class = ros_msg.get_message_class(msg_type[0] + '/' + msg_type[1])
        msg_obj = msg_class().deserialize(msg._buff)

        if msg_type[1] != 'SensorData':
            return
        
        database[self.topic] = json.loads(json.dumps({
            'type': msg_obj.type, 
            'data': msg_obj.data,  
            'risk': msg_obj.risk, 
            'batt': msg_obj.batt}))

  
def main(): 
    # Advertise ROS Node
    rospy.init_node('anymsg_subscriber', anonymous=True)

    # Create Subscribers
    thermometer =  AnyMsgSubscriber('/thermometer_data')
    ecg = AnyMsgSubscriber('/ecg_data')
    abpd = AnyMsgSubscriber('/abpd_data')
    abps = AnyMsgSubscriber('/abps_data')
    oximeter = AnyMsgSubscriber('/oximeter_data')
    glucose = AnyMsgSubscriber('/glucosemeter_data')

    # Start the Flask server and keep spinning the ROS node
    app.run(host='0.0.0.0', debug=True, port=3000)
    rospy.spin()

  
if __name__ == '__main__': 
    try: 
        main() 
    except rospy.ROSInterruptException: 
        pass


    
