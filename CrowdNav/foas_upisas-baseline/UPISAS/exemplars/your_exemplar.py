import pprint, time
from UPISAS.exemplar import Exemplar
import logging
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class YourExemplar(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    #  add the image name and container name
    _container_name = ""
    def __init__(self, auto_start: "Whether to immediately start the container after creation" =False):
        my_docker_kwargs = {
            "name":  "upisas-crowdnav",    
            "image": "crowd-nav-local", 
            "ports" : {3000: 3000}}             

        super().__init__("http://localhost:3000", my_docker_kwargs, auto_start)
    
    # start the container if the autostart is False
    def start_run(self):
        self.start_container()

    # stop the container if it goes to except 
    def stop(self):
        self.stop_container()