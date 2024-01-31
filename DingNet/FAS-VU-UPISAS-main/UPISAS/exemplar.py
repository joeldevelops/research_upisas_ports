import docker
from abc import ABC, abstractmethod
from rich.progress import Progress
from UPISAS import show_progress
import logging
from docker.errors import DockerException
from UPISAS.exceptions import DockerImageNotFoundOnDockerHub

logging.getLogger().setLevel(logging.INFO)


class Exemplar(ABC):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.

    Attributes
    ----------
    exemplar_container : Any
        The docker container of the self-adaptive exemplar.

    Methods
    -------
    start_run()
        Starts the run of the self-adaptive exemplar in the docker container.
    start_container()
        Starts running the docker container made from the given image when constructing this class.
    stop_container(remove=True)
        Stops the docker container made from the given image when constructing this class.
    pause_container()
        Pauses a running docker container made from the given image when constructing this class.
    unpause_container()
        Resumes a paused docker container made from the given image when constructing this class.
    get_container_status():
        Returns the status of the docker container made from the given image when constructing this class.
    """
    _container_name = ""
    def __init__(self, base_endpoint: "string with the URL of the exemplar's HTTP server", \
                 docker_kwargs,
                 auto_start: "Whether to immediately start the container after creation" =False,
                 ):
        """
        Create an instance of the Exemplar class

        Parameters
        ----------
        base_endpoint : string
            The URL of the exemplar's HTTP server.
        docker_kwargs : dictionary
            The keyword arguments of the docker container.
        auto_start : bool
            Whether to start the container immediately after creation (True) or not (False)

        Raises
        ------
        DockerImageNotFoundOnDockerHub
            If the docker image could not be found on docker hub.
        DockerException
            If an exception in the docker container occurred.
        """
        self.base_endpoint = base_endpoint
        image_name = docker_kwargs["image"]
        image_owner = image_name.split("/")[0]
        try:
            docker_client = docker.from_env()
            try:
                docker_client.images.get(image_name)
                logging.info(f"image '{image_name}' found locally")
            except docker.errors.ImageNotFound:
                logging.info(f"image '{image_name}' not found locally")
                images_from_owner = docker_client.images.search(image_owner)
                if image_name.split(":")[0] in [i["name"] for i in images_from_owner]:
                    logging.info(f"image '{image_name}' found on DockerHub, pulling it")
                    with Progress() as progress:
                        for line in docker_client.api.pull(image_name, stream=True, decode=True):
                            show_progress(line, progress)
                else:
                    logging.error(f"image '{image_name}' not found on DockerHub, exiting!")
                    raise DockerImageNotFoundOnDockerHub
            docker_kwargs["detach"] = True
            self.exemplar_container = docker_client.containers.create(**docker_kwargs)
        except DockerException as e:
            # TODO: Properly catch various errors. Currently, a lot of errors might be caught here.
            # Please check the logs if that happens.
            raise e
        if auto_start:
            self.start_container()

    @abstractmethod
    def start_run(self):
        """
        Starts the run of the self-adaptive exemplar in the docker container.

        This method is abstract and has to be implemented in the inheriting exemplar class.
        """
        pass

    def start_container(self):
        """
        Starts running the docker container made from the given image when constructing this class.

        Returns
        -------
        bool
            True if the container could be found. Otherwise, a NotFound docker error is logged.
        """
        try:
            container_status = self.get_container_status()
            if container_status == "running":
                logging.warning("container already running...")
            else:
                logging.info("starting container...")
                self.exemplar_container.start()
            return True
        except docker.errors.NotFound as e:
            logging.error(e)

    def stop_container(self, remove=True):
        """
        Stops the docker container made from the given image when constructing this class.

        Parameters
        -----------
        remove : bool, optional
            Whether to remove the container after stopping (True) or not (False).

        Returns
        -------
        bool
            True if the container could be found. Otherwise, a NotFound docker error is logged.
        """
        try:
            container_status = self.get_container_status()
            if container_status == "exited":
                logging.warning("container already stopped...")
                if remove:
                    self.exemplar_container.remove()
                    self.exemplar_container = None
            else:
                logging.info("stopping container...")
                self.exemplar_container.stop()
                if remove:
                    self.exemplar_container.remove()
                    self.exemplar_container = None
            return True
        except docker.errors.NotFound as e:
            logging.warning(e)
            logging.warning("cannot stop container")

    def pause_container(self):
        """
        Pauses a running docker container made from the given image when constructing this class.

        Returns
        -------
        bool
            True if the container could be found and is running or has already been paused. False if the container
            is not running. If the container could not be found, a NotFound docker error is logged.
        """
        try:
            container_status = self.get_container_status()
            if container_status == "running":
                logging.info("pausing container...")
                self.exemplar_container.pause()
                return True
            elif container_status == "paused":
                logging.warning("container already paused...")
                return True
            else:
                logging.warning("cannot pause container since it's not running")
                return False
        except docker.errors.NotFound as e:
            logging.error(e)
            logging.error("cannot pause container")

    def unpause_container(self):
        """
        Resumes a paused docker container made from the given image when constructing this class.

        Returns
        -------
        bool
            True if the container could be found and is currently paused or running. False if the container
            is not currently paused. If the container could not be found, a NotFound docker error is logged.
        """
        try:
            container_status = self.get_container_status()
            if container_status == "paused":
                logging.info("unpausing container...")
                self.exemplar_container.unpause()
                return True
            elif container_status == "running":
                logging.warning("container already running (why unpause it?)...")
                return True
            else:
                logging.warning("cannot unpause container since it's not paused")
                return False
        except docker.errors.NotFound as e:
            logging.warning(e)
            logging.warning("cannot unpause container")

    def get_container_status(self):
        """
        Returns the status of the docker container made from the given image when constructing this class.

        Returns
        -------
        string
            A string representing the status of the docker container made from the given image when constructing this
            class. If the container has been removed, "removed" is returned.
        """
        if self.exemplar_container:
            self.exemplar_container.reload()
            return self.exemplar_container.status
        return "removed"
