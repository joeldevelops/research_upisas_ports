import unittest
import time

from UPISAS import get_response_for_get_request
from UPISAS.exemplars.DingNet import DingNet
from UPISAS.strategies.empty_strategy import EmptyStrategy


class TestDingNetInterface(unittest.TestCase):
    """
    A class which implements unit tests for the adaptation of a DingNet exemplar.

    Attributes
    ----------
    EXECUTE_INPUT : dict (JSON)
        An example input for the execute endpoint of the Dingnet Exemplar.
    exemplar : Upisas.exemplars.DingNet
        The exemplar to test.
    strategy : UPISAS.strategy.Strategy
        An adaptation strategy to apply.

    Methods
    -------
    setUp()
        Sets up the DingNet exemplar, starts the server and instantiates an empty adaptation strategy.
    tearDown()
        Stops and removes the docker container containing the DingNet exemplar.
    test_get_adaptation_options_successfully()
         Tests the retrieval of adaptation options and its incorporation into the knowledge base.
    test_monitor_successfully()
        Tests the retrieval of monitored data and its incorporation into the knowledge base.
    test_execute_successfully()
        Tests the execution of an adaptation.
    test_adaptation_options_schema_endpoint_reachable()
        Tests the retrieval of the adaptation options schema and its incorporation into the knowledge base.
    test_monitor_schema_endpoint_reachable()
        Tests the retrieval of the monitor schema and its incorporation into the knowledge base.
    test_execute_schema_endpoint_reachable()
        Tests the retrieval of the execute schema and its incorporation into the knowledge base.
    test_schema_of_adaptation_options()
        Tests the validation of the adaptation options by means of the adaptation options schema.
    test_schema_of_monitor()
        Tests the validation of the monitored data by means of the monitor schema.
    test_schema_of_execute()
        Tests the validation of the execute input by means of the execute schema.
    _start_server_and_wait_until_is_up(base_endpoint="http://localhost:3000")
        Starts the exemplar and waits until the HTTP server is reachable.
    """
    EXECUTE_INPUT = {
        "items": [
            {
                "id": 0,
                "adaptations": [
                    {
                        "name": "power",
                        "value": 10
                    },
                    {
                        "name": "sampling_rate",
                        "value": 100
                    }
                ]
            },
            {
                "id": 1,
                "adaptations": [
                    {
                        "name": "power",
                        "value": 5
                    },
                    {
                        "name": "spreading_factor",
                        "value": 16
                    }
                ]
            }
        ]
    }

    def setUp(self):
        """
        Sets up the DingNet exemplar, starts the server and instantiates an empty adaptation strategy.
        """
        self.exemplar = DingNet(auto_start=True)
        self._start_server_and_wait_until_is_up()
        self.strategy = EmptyStrategy(self.exemplar)

    def tearDown(self):
        """
        Stops and removes the docker container containing the DingNet exemplar.
        """
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()

    def test_get_adaptation_options_successfully(self):
        """
        Tests the retrieval of adaptation options and its incorporation into the knowledge base.
        """
        self.strategy.get_adaptation_options(with_validation=False)
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options)

    def test_monitor_successfully(self):
        """
        Tests the retrieval of monitored data and its incorporation into the knowledge base.
        """
        successful = self.strategy.monitor(with_validation=False)
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.monitored_data, dict())

    def test_execute_successfully(self):
        """
        Tests the execution of an adaptation.
        """
        successful = self.strategy.execute(self.EXECUTE_INPUT, with_validation=False)
        self.assertTrue(successful)

    def test_adaptation_options_schema_endpoint_reachable(self):
        """
        Tests the retrieval of the adaptation options schema and its incorporation into the knowledge base.
        """
        self.strategy.get_adaptation_options_schema()
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options_schema)

    def test_monitor_schema_endpoint_reachable(self):
        """
        Tests the retrieval of the monitor schema and its incorporation into the knowledge base.
        """
        self.strategy.get_monitor_schema()
        self.assertIsNotNone(self.strategy.knowledge.monitor_schema)

    def test_execute_schema_endpoint_reachable(self):
        """
        Tests the retrieval of the execute schema and its incorporation into the knowledge base.
        """
        self.strategy.get_execute_schema()
        self.assertIsNotNone(self.strategy.knowledge.execute_schema)

    def test_schema_of_adaptation_options(self):
        """
        Tests the validation of the adaptation options by means of the adaptation options schema.
        """
        self.strategy.get_adaptation_options_schema()
        with self.assertLogs() as cm:
            self.strategy.get_adaptation_options()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options)

    def test_schema_of_monitor(self):
        """
        Tests the validation of the monitored data by means of the monitor schema.
        """
        self.strategy.get_monitor_schema()
        with self.assertLogs() as cm:
            successful = self.strategy.monitor()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.monitored_data, dict())

    def test_schema_of_execute(self):
        """
        Tests the validation of the execute input by means of the execute schema.
        """
        self.strategy.get_execute_schema()
        with self.assertLogs() as cm:
            successful = self.strategy.execute(self.EXECUTE_INPUT)
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)

    def _start_server_and_wait_until_is_up(self, base_endpoint="http://localhost:3000"):
        """
        Starts the exemplar and waits until the HTTP server is reachable.

        Parameters
        ---------
        base_endpoint : string, optional
            The URL of the HTTP server. Defaults to "http://localhost:3000".
        """
        self.exemplar.start_run()
        while True:
            time.sleep(1)
            print("trying to connect...")
            response = get_response_for_get_request(base_endpoint)
            print(response.status_code)
            if response.status_code < 400:
                return


if __name__ == '__main__':
    unittest.main()
