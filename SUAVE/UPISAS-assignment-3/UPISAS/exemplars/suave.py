import os
import pprint, time
from UPISAS.exemplar import Exemplar
import logging

pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class Suave(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """

    def __init__(self, auto_start: "Whether to immediately start the container after creation" = False,
                 container_name="suave-container"):
        # We are not using the implementation provided by original UPISAS
        # You might ask: why?
        # Because original implementation is buggy and actually not fully implemented
        # Instead, we are using docker-compose to manage the container lifecycle
        # Refer to README.md for more details

        if os.environ.get("SUAVE_PROD", False):
            logging.info("Running in production mode. Containers are managed by Docker Compose.")
            self.base_endpoint = "http://suave:3000"
            logging.info('SUAVE instantiated')
        else:
            logging.info("Running in debug mode. Containers are managed manually.")
            my_docker_kwargs = {
                "name": container_name,
                "image": "ghcr.io/caesarw/suave-custom:main",
                "ports": {3000: 3000}
            }

            super().__init__("http://localhost:3000", my_docker_kwargs, auto_start)

    def start_run(self):
        # The startup script is already defined with the Docker entrypoint, so there's no point of calling explicitly
        logging.info("Waiting for the container to be ready...")
        time.sleep(30)
        # self.exemplar_container.exec_run(cmd=' sh -c "~/suave_ws/src/suave/runner/runner-custom.sh" ', detach=True)
