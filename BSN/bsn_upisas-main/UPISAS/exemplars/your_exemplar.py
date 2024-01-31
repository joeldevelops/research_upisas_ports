import pprint
from UPISAS.exemplar import Exemplar
import logging

pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class BSN(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""

    def __init__(self, auto_start: "Whether to immediately start the container after creation" = False):
        my_docker_kwargs = {
            "name": "bsn_test_container",
            "image": "bsn_proj",
            "ports": {3000: 5000, 5901: 5901, 6901: 6901}}

        super().__init__("http://localhost:5000", my_docker_kwargs, auto_start)

    def start_run(self):
        pass
        # TODO start a simulation run within the exemplar's container (see swim.py)
