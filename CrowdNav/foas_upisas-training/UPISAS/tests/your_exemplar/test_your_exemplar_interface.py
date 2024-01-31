import unittest
import time

from UPISAS import get_response_for_get_request
from UPISAS.exemplars.your_exemplar import YourExemplar
from UPISAS.strategies.RL_crowd_nav import Adaptive_Planner
from UPISAS.strategies.empty_strategy import EmptyStrategy


class TestYourExemplarInterface(unittest.TestCase):

    def setUp(self):
        self.exemplar = YourExemplar(auto_start=True)
        self.planner = Adaptive_Planner(True,"q_table_500_final.csv")
        self._start_server_and_wait_until_is_up()
        self.strategy = EmptyStrategy(self.exemplar,self.planner)

    def tearDown(self):
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()

    def test_get_adaptation_options_successfully(self):
        self.strategy.get_adaptation_options(with_validation=False)
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options)

    def test_monitor_successfully(self):
        # wait and only start the test after the simulation in CrowdNav is started
        time.sleep(40)
        successful = self.strategy.monitor(with_validation=False)
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.monitored_data, dict())

    def test_execute_successfully(self):
        # added PUT request body pertaining to our exemplar (CrowdNav)
        successful = self.strategy.execute({"maxSpeedAndLengthFactor": 1,"averageEdgeDurationFactor": 1,"freshnessUpdateFactor": 10}, with_validation=False)
        self.assertTrue(successful)

    def test_adaptation_options_schema_endpoint_reachable(self):
        self.strategy.get_adaptation_options_schema()
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options_schema)

    def test_monitor_schema_endpoint_reachable(self):
        self.strategy.get_monitor_schema()
        self.assertIsNotNone(self.strategy.knowledge.monitor_schema)

    def test_execute_schema_endpoint_reachable(self):
        self.strategy.get_execute_schema()
        self.assertIsNotNone(self.strategy.knowledge.execute_schema)

    def test_schema_of_adaptation_options(self):
        self.strategy.get_adaptation_options_schema()
        with self.assertLogs() as cm:
            self.strategy.get_adaptation_options()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options)

    def test_schema_of_monitor(self):
        time.sleep(40)
        self.strategy.get_monitor_schema()
        with self.assertLogs() as cm:
            successful = self.strategy.monitor()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.monitored_data, dict())

    def test_schema_of_execute(self):
        self.strategy.get_execute_schema()
        with self.assertLogs() as cm:
            # added PUT request body pertaining to our exemplar (CrowdNav)
            successful = self.strategy.execute({"maxSpeedAndLengthFactor": 1,"averageEdgeDurationFactor": 1,"freshnessUpdateFactor": 10})
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)

    def _start_server_and_wait_until_is_up(self, base_endpoint="http://localhost:3000"):
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
