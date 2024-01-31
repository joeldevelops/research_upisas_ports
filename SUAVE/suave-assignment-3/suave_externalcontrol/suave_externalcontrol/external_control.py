import sys
import rclpy
from rclpy.lifecycle import Node
from diagnostic_msgs.msg import DiagnosticArray
from collections import defaultdict
import threading
from suave_msgs.srv import Task
from system_modes_msgs.srv import ChangeMode


class ExternalControl(Node):

    def __init__(self):
        super().__init__('external_control')
        self.diagnostics_sub = self.create_subscription(
            DiagnosticArray,
            '/diagnostics',
            self.diagnostics_cb,
            10
        )
        self.task_request_client = self.create_client(Task, 'task/request')
        self.task_cancel_client = self.create_client(Task, 'task/cancel')
        self.task_req = Task.Request()

        self.f_maintain_motion_client = self.create_client(ChangeMode, 'f_maintain_motion/change_mode')
        self.f_generate_search_path_client = self.create_client(ChangeMode, 'f_generate_search_path/change_mode')
        self.f_follow_pipeline_client = self.create_client(ChangeMode, 'f_follow_pipeline/change_mode')
        self.change_mode_req = ChangeMode.Request()

        self.buffer = {
            "water_visibility": -1,
            "thrusters": {
                "c_thruster_1": True,
                "c_thruster_2": True,
                "c_thruster_3": True,
                "c_thruster_4": True,
                "c_thruster_5": True,
                "c_thruster_6": True
            }
        }
        self.lock = threading.Lock()

    def diagnostics_cb(self, msg):
        for status in msg.status:
            if status.message == "QA status" or status.message == "Component status":
                # self.get_logger().info(f'Diagnostics: {msg}')
                for value in status.values:
                    # Collecting data
                    # TODO(caesar): add buffer timeout (preferably)
                    if value.key == "water_visibility":
                        with self.lock:
                            self.buffer[str(value.key)] = float(value.value)

                    if "c_thruster_" in str(value.key):
                        with self.lock:
                            self.buffer['thrusters'][str(value.key)] = False if str(value.value) == 'FALSE' else True

    def send_task_request(self, task_name):
        self.task_req.task_name = task_name
        # self.future = self.task_request_client.call_async(self.task_req)
        # rclpy.spin_until_future_complete(self, self.future)
        return self.task_request_client.call(self.task_req)
        # return self.future.result()

    def send_task_cancel(self, task_name):
        self.task_req.task_name = task_name
        # self.future = self.task_cancel_client.call_async(self.task_req)
        # rclpy.spin_until_future_complete(self, self.future)
        return self.task_cancel_client.call(self.task_req)
        # return self.future.result()

    def send_f_maintain_motion(self, mode_name):
        self.change_mode_req.mode_name = mode_name
        # self.future = self.f_maintain_motion_client.call_async(self.change_mode_req)
        # rclpy.spin_until_future_complete(self, self.future)
        return self.f_maintain_motion_client.call(self.change_mode_req)
        # return self.future.result()

    def send_f_generate_search_path(self, mode_name):
        self.change_mode_req.mode_name = mode_name
        # self.future = self.f_generate_search_path_client.call_async(self.change_mode_req)
        # rclpy.spin_until_future_complete(self, self.future)
        return self.f_generate_search_path_client.call(self.change_mode_req)
        # return self.future.result()

    def send_f_follow_pipeline(self, mode_name):
        self.change_mode_req.mode_name = mode_name
        # self.future = self.f_follow_pipeline_client.call_async(self.change_mode_req)
        # rclpy.spin_until_future_complete(self, self.future)
        return self.f_follow_pipeline_client.call(self.change_mode_req)
        # return self.future.result()


def main():
    rclpy.init(args=sys.argv)

    external_control_node = ExternalControl()
    rclpy.spin(external_control_node)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
