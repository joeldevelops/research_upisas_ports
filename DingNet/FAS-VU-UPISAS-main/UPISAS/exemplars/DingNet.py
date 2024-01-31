import pprint, time
from UPISAS import get_response_for_get_request
from UPISAS.exemplar import Exemplar
import logging
pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)

class DingNet(Exemplar):
    """
    A class which encapsulates a run of the self-adaptive exemplar DingNet in a docker container.

    Methods
    --------
    start_run(seed=0)
        Starts a run of the DingNet simulation in the created docker container.
    stop_run()
        Stops the current run of the DingNet simulation in the created docker container.
    """
    _container_name = ""
    def __init__(self, auto_start: "Whether to immediately start the container after creation" = False):
        """
        Creates a new DingNet docker container.

        Parameters
        ----------
        auto_start : bool
            Whether to start the container immediately after creation (True) or not (False)
        """
        my_docker_kwargs = {
            "name":  "dingnet",
            "image": "dingnet",
            "ports" : {
                3000: 3000,
                6901: 6901
            },
            "environment": {
                "PORT": "3000",
                "VNC_PW": "password",
            },
            "shm_size": "512m",
        }

        super().__init__("http://localhost:3000", my_docker_kwargs, auto_start)
    
    def start_run(self, seed: int = 0):
        """
        Starts a run of the DingNet simulation in the created docker container.

        Parameters
        ----------
        seed : int, optional
            A seed for the randomized elements in the configuration of the scenario. The default value is 0.
        """
        # Wait for container to fully start
        for _ in range(20):
            time.sleep(1)
            print("Waiting for X server to start")
            if b'KasmVNC environment started' in self.exemplar_container.logs():
                break
        else:
            raise RuntimeError("No response from container")

        # Wait for HTTP server to start
        for _ in range(20):
            time.sleep(1)
            print("Waiting for HTTP server to start")
            if b'Server running' in self.exemplar_container.exec_run('cat out.txt')[1]:
                break
        else:
            raise RuntimeError("No response from container")

        # Start simulation
        response = get_response_for_get_request(f"http://localhost:3000/start_run?seed={seed}")
        print(response.content)

        if response.status_code != 200:
            raise RuntimeError(f"Error starting simulation: {response.content.decode('utf-8')}")
        
        res = get_response_for_get_request(f"http://localhost:3000/monitor").json()

        i = 0

        # Wait until simulation is initialized
        while len(res['moteStates']) == 0:
            res = get_response_for_get_request(f"http://localhost:3000/monitor").json()
            print("Waiting for simulation to initialize")
            time.sleep(1)
            i += 1

            if i % 10 == 0:
                # Retry starting the simulation
                get_response_for_get_request(f"http://localhost:3000/stop_run")
                time.sleep(2)
                get_response_for_get_request(f"http://localhost:3000/start_run?seed={seed}")

    def stop_run(self):
        """
        Stops the current run of the DingNet simulation in the created docker container.

        Raises
        ------
        RuntimeError
            If the endpoint for stopping the simulation returns a status code unequal to 200 OK.
        """
        response = get_response_for_get_request(f"http://localhost:3000/stop_run")

        if response.status_code != 200:
            raise RuntimeError(f"Error stopping simulation: {response.content.decode('utf-8')}")
            
