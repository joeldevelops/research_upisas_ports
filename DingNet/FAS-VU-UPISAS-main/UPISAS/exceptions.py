class UPISASException(Exception):
    """
    A class representing a general UPISAS exception.
    """
    pass


class DockerImageNotFoundOnDockerHub(UPISASException):
    """
    A class representing the UPISAS exception that a docker image was not found on docker hub.
    """
    pass


class ServerNotReachable(UPISASException):
    """
    A class representing the UPISAS exception that a server is not reachable.
    """
    pass


class EndpointNotReachable(UPISASException):
    """
    A class representing the UPISAS exception that an endpoint is not reachable.
    """
    pass


class IncompleteJSONSchema(UPISASException):
    """
    A class representing the UPISAS exception that a given JSON schema is incomplete.
    """
    pass
