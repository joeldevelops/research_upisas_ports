#!/usr/bin/env python

import numpy as np
import rospy
import roslib.message as ros_msg
from archlib.msg import AdaptationCommand
from messages.msg import SensorData
from time import sleep
import json
from genson import SchemaBuilder
from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError

publisher = Blueprint('publisher', __name__)

class AdaptationPublisher:
    def __init__(self, topic):
        self.pub = rospy.Publisher(topic, AdaptationCommand, queue_size=10)
        self.topic = topic

    def publish(self, source, target, action):
        msg = AdaptationCommand()
        msg.Header.frame_id = ''
        msg.Header.seq = 0
        msg.Header.stamp.nsecs = 0
        msg.Header.stamp.secs = 0
        msg.source = source
        msg.target = target
        msg.action = action
        self.pub.publish(msg)


@publisher.route('/execute_schema', methods=['GET'])
def execute_schema():
    builder = SchemaBuilder()
    builder.add_object({"topic": "/reconfigure_/g3t1_1", "target": "g3t1_1", "action": "freq=0.999"})
    return builder.to_schema()


@publisher.route('/execute', methods=['PUT'])
def execute():
    data_json = json.loads(request.data.decode())
    
    try:
        validate(instance=data_json, schema=execute_schema())
    except ValidationError:
        return "Incorrect schema, please follow this format: " + str(execute_schema() + '\n')

    topic = data_json['topic']
    target = data_json['target']
    action = data_json['action']

    # Create Publisher
    pub = AdaptationPublisher(topic)
    pub.publish(topic, target, action)
    return 'Success\n'


def main(): 
    # Advertise ROS Node
    rospy.init_node('talker', anonymous=True)

    # Keep Spinning
    rospy.spin()

  
if __name__ == '__main__': 
    try: 
        main() 
    except rospy.ROSInterruptException: 
        pass

