# from launch import LaunchDescription
# from launch_ros.actions import Node
# from launch.actions import ExecuteProcess
#
#
# def generate_launch_description():
#
#     http_server = ExecuteProcess(
#         cmd=['python', '~/suave_ws/src/suave/suave_externalcontrol/suave_externalcontrol/http_server.py'],
#         name='http_server',
#         output='screen',
#         shell=True
#     )
#
#     # external_control_node = Node(
#     #     package='suave_externalcontrol',
#     #     # executable=,
#     #     name='',
#     #     # parameters=[mission_config, {
#     #     #     'adaptation_manager': adaptation_manager,
#     #     # }],
#     #     # condition=LaunchConfigurationEquals('result_filename', '')
#     # )
#
#     return LaunchDescription([
#         http_server,
#     ])
