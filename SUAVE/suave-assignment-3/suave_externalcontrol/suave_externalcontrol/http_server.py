import sys
import rclpy
from flask import Flask
from flask import request
from external_control import ExternalControl
import threading


class HttpInterfaceServer:
    def __init__(self, host="0.0.0.0", port=3000):
        # Setting up web server
        self.app = Flask(__name__)
        self.host = host
        self.port = port

        # All the endpoints
        self.app.add_url_rule('/', 'ack', view_func=self.ack, methods=['GET'])

        self.app.add_url_rule('/monitor', 'monitor', view_func=self.monitor, methods=['GET'])
        self.app.add_url_rule('/execute', 'execute', view_func=self.execute, methods=['PUT'])
        self.app.add_url_rule('/adaptation_options', 'adaptation_options', view_func=self.adaptation_options,
                              methods=['GET'])

        self.app.add_url_rule('/monitor_schema', 'monitor_schema', view_func=self.monitor_schema, methods=['GET'])
        self.app.add_url_rule('/execute_schema', 'execute_schema', view_func=self.execute_schema, methods=['GET'])
        self.app.add_url_rule('/adaptation_options_schema', 'adaptation_options_schema',
                              view_func=self.adaptation_options_schema, methods=['GET'])

        # Setting up ROS node
        rclpy.init(args=sys.argv)
        self.external_control_node = ExternalControl()
        self.external_control_node_thread = threading.Thread(target=lambda: rclpy.spin(self.external_control_node))
        self.external_control_node_thread.start()
        # rclpy.spin(self.external_control_node)

        # Start web server in a new thread
        # self.http_server_thread = threading.Thread(
        #     target=lambda: self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False))
        # self.http_server_thread.start()
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.external_control_node.destroy_node()
        self.external_control_node_thread.join()
        rclpy.shutdown()

    def ack(self):
        return '', 204

    def monitor(self):
        return self.external_control_node.buffer

    def monitor_schema(self):
        # TODO(caesar): consider standard RESTful implementation
        # { "status": "ok", "payload": schema }
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "water_visibility": {"type": "number"},
                "thrusters": {
                    "type": "object",
                    "properties": {
                        "c_thruster_1": {"type": "boolean"},
                        "c_thruster_2": {"type": "boolean"},
                        "c_thruster_3": {"type": "boolean"},
                        "c_thruster_4": {"type": "boolean"},
                        "c_thruster_5": {"type": "boolean"},
                        "c_thruster_6": {"type": "boolean"}
                    },
                    "required": ["c_thruster_1", "c_thruster_2", "c_thruster_3", "c_thruster_4", "c_thruster_5", "c_thruster_6"]
                }
            },
            "required": ["water_visibility", "thrusters"]
        }
        return schema

    def execute(self):
        # {"adaptation": "/task/cancel", "option": "search_pipeline"}
        try:
            body = request.get_json()
            response = None
            # Python does not have switch-case, we stick to this for the time being
            # Will do better next time
            if body['adaptation'] == "/task/request":
                response = self.external_control_node.send_task_request(body['option'])
            elif body['adaptation'] == "/task/cancel":
                response = self.external_control_node.send_task_cancel(body['option'])
            elif body['adaptation'] == "/f_maintain_motion/change_mode":
                response = self.external_control_node.send_f_maintain_motion(body['option'])
            elif body['adaptation'] == "/f_generate_search_path/change_mode":
                response = self.external_control_node.send_f_generate_search_path(body['option'])
            elif body['adaptation'] == "/f_follow_pipeline/change_mode":
                response = self.external_control_node.send_f_follow_pipeline(body['option'])
            return {"status": "success", "message": response.success}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 405

    def execute_schema(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "adaptation": {
                    "type": "string"
                },
                "option": {
                    "type": "string"
                }
            },
            "required": [
                "adaptation",
                "option"
            ]
        }
        return schema

    def adaptation_options(self):
        options = {
            "tasks": {
                "operations": ["/task/cancel", "/task/request"],
                "adaptation_options": ["search_pipeline", "inspect_pipeline"]
            },
            "f_maintain_motion": {
                "operations": ["/f_maintain_motion/change_mode"],
                "adaptation_options": ["__DEFAULT__", "fd_all_thrusters", "fd_recover_thrusters", "fd_unground"]
            },
            "f_generate_search_path": {
                "operations": ["/f_generate_search_path/change_mode"],
                "adaptation_options": ["__DEFAULT__", "fd_spiral_high", "fd_spiral_low", "fd_spiral_medium",
                                       "fd_unground"]
            },
            "f_follow_pipeline": {
                "operations": ["/f_follow_pipeline/change_mode"],
                "adaptation_options": ["__DEFAULT__", "fd_follow_pipeline", "fd_unground"]
            }
        }
        return options

    def adaptation_options_schema(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "object",
                    "properties": {
                        "operations": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                }
                            ]
                        },
                        "adaptation_options": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                }
                            ]
                        }
                    },
                    "required": [
                        "operations",
                        "adaptation_options"
                    ]
                },
                "f_maintain_motion": {
                    "type": "object",
                    "properties": {
                        "operations": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "string"
                                }
                            ]
                        },
                        "adaptation_options": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                }
                            ]
                        }
                    },
                    "required": [
                        "operations",
                        "adaptation_options"
                    ]
                },
                "f_generate_search_path": {
                    "type": "object",
                    "properties": {
                        "operations": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "string"
                                }
                            ]
                        },
                        "adaptation_options": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                }
                            ]
                        }
                    },
                    "required": [
                        "operations",
                        "adaptation_options"
                    ]
                },
                "f_follow_pipeline": {
                    "type": "object",
                    "properties": {
                        "operations": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "string"
                                }
                            ]
                        },
                        "adaptation_options": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "string"
                                }
                            ]
                        }
                    },
                    "required": [
                        "operations",
                        "adaptation_options"
                    ]
                }
            },
            "required": [
                "tasks",
                "f_maintain_motion",
                "f_generate_search_path",
                "f_follow_pipeline"
            ]
        }
        return schema


def main():
    http_interface_server = HttpInterfaceServer()


if __name__ == '__main__':
    main()
