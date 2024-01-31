import time
import pprint
from UPISAS.exemplar import Exemplar
import logging
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class EWS(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = "emergent_web_server"
    def __init__(self, auto_start: "Whether to immediately start the container after creation" =False):
        my_docker_kwargs = {
            "name":  "emergent_web_server", # Container name
            "image": "robertovrf/ews:1.0", # Uncomment for MacOS
            "ports" : {2011: 2011, 2012: 2012}} # Necessary ports
            # "image": "ews-image", # Comment out for MacOS
            # "ports" : {2011: 8080, 2012: 8081}} # Necessary ports

        # super().__init__("http://localhost:8080/meta/get_config", my_docker_kwargs, auto_start)
        super().__init__("http://localhost:2011/meta/get_config", my_docker_kwargs, auto_start)
    

    def start_run(self):
        command1 = 'dana -sp ../repository InteractiveEmergentSys.o'
        command2 = 'cd ../ws_clients && dana ClientTextPattern.o'

        # Set sleep time for ews to start
        sleep_time = 60 # Increase if necessary (for MacOS)

        # Combine commands into a single tmux session
        # combined_command = f"tmux new-session -d {command1} && sleep {sleep_time} && tmux send-keys -t 0 exit Enter"

        self.exemplar_container.exec_run(cmd=["bash", "-c", command1], detach=False, stream=True,stderr=True, stdout=True)
        # time.sleep(sleep_time)
        # self.exemplar_container.exec_run(cmd=["bash", "-c", command2], detach=True, stream=True,stderr=True, stdout=True)



#########################
class FastAPI(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = "fastapi_server"
    def __init__(self, auto_start: "Whether to immediately start the container after creation" =False):
        my_docker_kwargs = {
            "name":  "fastapi_server", # Container name
            "image": "fastapi-image", # Server's image name
            "ports" : {80: 8000}} # Necessary ports

        super().__init__("http://localhost:8000", my_docker_kwargs, auto_start)
    
    def start_run(self):
        pass
