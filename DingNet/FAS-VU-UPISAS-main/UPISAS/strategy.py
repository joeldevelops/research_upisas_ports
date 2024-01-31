from abc import ABC, abstractmethod
import requests
import pprint

from UPISAS.exceptions import EndpointNotReachable, ServerNotReachable
from UPISAS.knowledge import Knowledge
from UPISAS import validate_schema, get_response_for_get_request
import logging

pp = pprint.PrettyPrinter(indent=4)


class Strategy(ABC):
    """
    A class which implements an adaptation strategy for a self-adaptive exemplar.

    Attributes
    ----------
    exemplar : Any
        The exemplar to adapt.
    knowledge : UPISAS.knowledge
        The knowledge base used for the adaptation.

    Methods
    -------
    ping()
        Pings the base endpoint of the exemplar and logs the result.
    monitor(endpoint_suffix="monitor", with_validation=True)
        Monitors the exemplar and its environment.
    execute(adaptation, endpoint_suffix="execute", with_validation=True)
        Applies a given adaptation to the exemplar.
    get_adaptation_options(endpoint_suffix="adaptation_options", with_validation=True)
        Retrieves the available adaptation options of the exemplar and enters them into the knowledge base.
    get_monitor_schema(endpoint_suffix="monitor_schema")
        Retrieves the JSON schema for validating the response of the monitor endpoint and enters it into the
        knowledge base.
    get_execute_schema(endpoint_suffix="execute_schema")
        Retrieves the JSON schema for validating the response of the execute endpoint and enters it into the
        knowledge base.
    get_adaptation_options_schema(endpoint_suffix="adaptation_options_schema")
        Retrieves the JSON schema for validating the response of the adaptation options endpoint and enters it into the
        knowledge base.
    _perform_get_request(endpoint_suffix)
        Performs an HTTP request to the given API endpoint of the base endpoint and returns the response as JSON.
    analyze()
        Analyzes the adaptation options of the exemplar.
    plan()
        Plans the adaptation to be applied to the exemplar.
    """
    def __init__(self, exemplar):
        """
        Creates a new instance of a Strategy for a given exemplar.

        Parameters
        ----------
        exemplar : Any
            The exemplar to adapt.
        """
        self.exemplar = exemplar
        self.knowledge = Knowledge(dict(), dict(), dict(), dict(), dict(), dict(), dict())

    def ping(self):
        """
        Pings the base endpoint of the exemplar and logs the result.
        """
        ping_res = self._perform_get_request(self.exemplar.base_endpoint)
        logging.info(f"ping result: {ping_res}")

    def monitor(self, endpoint_suffix="monitor", with_validation=True):
        """
        Monitors the exemplar and its environment.

        This method implements the Monitor step of the MAPE-K reference model.

        Parameters
        -----------
        endpoint_suffix : string, optional
            The URL suffix of the monitor endpoint. The default value is "monitor".
        with_validation : bool
            Whether to validate the response of the monitor endpoint with a JSON schema (True) or not (False).

        Returns
        -------
        bool
            Whether the monitor step was completed successfully (True) or not (False).
        """
        fresh_data = self._perform_get_request(endpoint_suffix)
        logging.info("[Monitor]\tgot fresh_data: " + str(fresh_data))
        if with_validation:
            validate_schema(fresh_data, self.knowledge.monitor_schema)
        data = self.knowledge.monitored_data
        for key in list(fresh_data.keys()):
            if key not in data:
                data[key] = []
            data[key].append(fresh_data[key])
        logging.info("[Knowledge]\tdata monitored so far: " + str(self.knowledge.monitored_data))
        return True

    def execute(self, adaptation, endpoint_suffix="execute", with_validation=True):
        """
        Applies a given adaptation to the exemplar.

        This method implements the Execute step of the MAPE-K reference model.

        Parameters
        -----------
        adaptation : dict
            The adaptation options to be applied as JSON.
        endpoint_suffix : string, optional
            The URL suffix of the execute endpoint. The default value is "execute".
        with_validation : bool
            Whether to validate the given adaptation options with a JSON schema (True) or not (False).

        Returns
        -------
        bool
            Whether the execute step was completed successfully (True) or not (False).

        Raises
        -------
        EndpointNotReachable
            If the execute endpoint could not be reached and the status code 404 was returned.
        """
        if with_validation:
            validate_schema(adaptation, self.knowledge.execute_schema)
        url = '/'.join([self.exemplar.base_endpoint, endpoint_suffix])
        response = requests.put(url, json=adaptation)
        logging.info("[Execute]\tposted configuration: " + str(adaptation))
        if response.status_code == 404:
            logging.error("Cannot execute adaptation on remote system, check that the execute endpoint exists.")
            raise EndpointNotReachable
        return True

    def get_adaptation_options(self, endpoint_suffix: "API Endpoint" = "adaptation_options", with_validation=True):
        """
        Retrieves the available adaptation options of the exemplar and enters them into the knowledge base.

        Parameters
        -----------
        endpoint_suffix : string, optional
            The URL suffix of the adaptation options endpoint. The default value is "adaptation_options".
        with_validation : bool
            Whether to validate the response of the adaptation options endpoint with a JSON schema (True) or not (False).
        """
        self.knowledge.adaptation_options = self._perform_get_request(endpoint_suffix)
        if with_validation:
            validate_schema(self.knowledge.adaptation_options, self.knowledge.adaptation_options_schema)
        logging.info("adaptation_options set to: ")
        logging.info(pp.pformat(self.knowledge.adaptation_options))

    def get_monitor_schema(self, endpoint_suffix = "monitor_schema"):
        """
        Retrieves the JSON schema for validating the response of the monitor endpoint and enters it into the
        knowledge base.

        Parameters
        -----------
        endpoint_suffix : string, optional
            The URL suffix of the monitor schema endpoint. The default value is "monitor_schema".
        """
        self.knowledge.monitor_schema = self._perform_get_request(endpoint_suffix)
        logging.info("monitor_schema set to: ")
        logging.info(pp.pformat(self.knowledge.monitor_schema))

    def get_execute_schema(self, endpoint_suffix = "execute_schema"):
        """
        Retrieves the JSON schema for validating the response of the execute endpoint and enters it into the
        knowledge base.

        Parameters
        -----------
        endpoint_suffix : string, optional
            The URL suffix of the execute schema endpoint. The default value is "execute_schema".
        """
        self.knowledge.execute_schema = self._perform_get_request(endpoint_suffix)
        logging.info("execute_schema set to: ")
        logging.info(pp.pformat(self.knowledge.execute_schema))

    def get_adaptation_options_schema(self, endpoint_suffix: "API Endpoint" = "adaptation_options_schema"):
        """
        Retrieves the JSON schema for validating the response of the adaptation options endpoint and enters it into the
        knowledge base.

        Parameters
        -----------
        endpoint_suffix : string, optional
            The URL suffix of the adaptation options schema endpoint. The default value is "adaptation_options_schema".
        """
        self.knowledge.adaptation_options_schema = self._perform_get_request(endpoint_suffix)
        logging.info("adaptation_options_schema set to: ")
        logging.info(pp.pformat(self.knowledge.adaptation_options_schema))

    def _perform_get_request(self, endpoint_suffix: "API Endpoint"):
        """
        Performs an HTTP request to the given API endpoint of the base endpoint and returns the response as JSON.

        Parameters
        -----------
        endpoint_suffix : string, optional
            The API endpoint to direct the request to.

        Returns
        --------
        dict (JSON)
            The response of the HTTP request as JSON.

        Raises
        -------
        EndpointNotReachable
            If the endpoint could not be reached and the status code 404 was returned.
        """
        url = '/'.join([self.exemplar.base_endpoint, endpoint_suffix])
        response = get_response_for_get_request(url)
        if response.status_code == 404:
            logging.error("Please check that the endpoint you are trying to reach actually exists.")
            raise EndpointNotReachable
        return response.json()

    @abstractmethod
    def analyze(self):
        """
        Analyzes the adaptation options of the exemplar.

        This method represents the Analyze step of the MAPE-K reference model.

        This is an abstract method and has to be implemented by the inheriting class.
        """
        """ ... """
        pass

    @abstractmethod
    def plan(self):
        """
        Plans the adaptation to be applied to the exemplar.

        This method represents the Plan step of the MAPE-K reference model.

        This is an abstract method and has to be implemented by the inheriting class.
        """
        """ ... """
        pass

