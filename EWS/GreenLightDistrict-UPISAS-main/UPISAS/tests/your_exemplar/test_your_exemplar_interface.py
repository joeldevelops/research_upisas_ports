import unittest
import time
import docker


from UPISAS import get_response_for_get_request
from UPISAS.exemplars.your_exemplar import EWS
from UPISAS.strategies.empty_strategy import EmptyStrategy
from UPISAS.exemplars.your_exemplar import FastAPI


class TestYourExemplarInterface(unittest.TestCase):

    def setUp(self):
        

        self.exemplar = EWS(auto_start=True)
        self.server = FastAPI(auto_start=True)

        self.docker_client = docker.from_env()
        self.network = self.docker_client.networks.create("test_network")

        self.network.connect(self.exemplar.exemplar_container)
        self.network.connect(self.server.exemplar_container)

        self._start_server_and_wait_until_is_up()
        self.strategy = EmptyStrategy(self.server)

            
    def tearDown(self):
        if self.exemplar and self.exemplar.exemplar_container:
            self.exemplar.stop_container()
        if self.server and self.server.exemplar_container:
            self.server.stop_container()
        if self.network:
            self.network.remove()

    def test_get_adaptation_options_successfully(self):
        self.strategy.get_adaptation_options(with_validation=False)
        self.assertIsNotNone(self.strategy.knowledge.adaptation_options)

    def test_monitor_successfully(self):
        successful = self.strategy.monitor(with_validation=False)
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.monitored_data, dict())

    def test_execute_successfully(self):
        successful = self.strategy.execute({
    "id": 0,
    "config": "|../repository/TCPNetwork.o,/emergent_web_server/dana/components/net/TCP.o,/emergent_web_server/repository/request/RequestHandler.o,/emergent_web_server/repository/app_protocols/HTTPProtocol.o,/emergent_web_server/repository/http/HTTPHeader1_0.o,/emergent_web_server/repository/http/handler/GET/HTTPGETCMP.o,/emergent_web_server/dana/components/io/File.o,/emergent_web_server/repository/compression/ZLIB.o,/emergent_web_server/dana/components/os/Run.o,/emergent_web_server/dana/components/time/DateUtil.o,/emergent_web_server/repository/http/util/HTTPUtil.o,/emergent_web_server/dana/components/data/StringUtil.o,/emergent_web_server/dana/components/data/adt/List.o|0:net.TCPSocket:1,0:net.TCPServerSocket:1,0:request.RequestHandler:2,2:app_protocols.AppProtocol:3,3:http.HTTPHeader:4,4:http.handler.GET.HTTPGET:5,5:io.File:6,5:compression.Compression:7,7:os.Run:8,7:time.DateUtil:9,7:io.FileSystem:6,4:http.util.HTTPUtil:10,10:io.FileSystem:6,10:data.StringUtil:11,11:data.adt.List:12|"
  }, with_validation=False)
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
        self.strategy.get_monitor_schema()
        with self.assertLogs() as cm:
            successful = self.strategy.monitor()
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)
        self.assertNotEqual(self.strategy.knowledge.monitored_data, dict())

    def test_schema_of_execute(self):
        self.strategy.get_execute_schema()
        with self.assertLogs() as cm:
            successful = self.strategy.execute({
    "id": 0,
    "config": "|../repository/TCPNetwork.o,/emergent_web_server/dana/components/net/TCP.o,/emergent_web_server/repository/request/RequestHandler.o,/emergent_web_server/repository/app_protocols/HTTPProtocol.o,/emergent_web_server/repository/http/HTTPHeader1_0.o,/emergent_web_server/repository/http/handler/GET/HTTPGETCMP.o,/emergent_web_server/dana/components/io/File.o,/emergent_web_server/repository/compression/ZLIB.o,/emergent_web_server/dana/components/os/Run.o,/emergent_web_server/dana/components/time/DateUtil.o,/emergent_web_server/repository/http/util/HTTPUtil.o,/emergent_web_server/dana/components/data/StringUtil.o,/emergent_web_server/dana/components/data/adt/List.o|0:net.TCPSocket:1,0:net.TCPServerSocket:1,0:request.RequestHandler:2,2:app_protocols.AppProtocol:3,3:http.HTTPHeader:4,4:http.handler.GET.HTTPGET:5,5:io.File:6,5:compression.Compression:7,7:os.Run:8,7:time.DateUtil:9,7:io.FileSystem:6,4:http.util.HTTPUtil:10,10:io.FileSystem:6,10:data.StringUtil:11,11:data.adt.List:12|"
  })
            self.assertTrue("JSON object validated by JSON Schema" in ", ".join(cm.output))
        self.assertTrue(successful)

    def _start_server_and_wait_until_is_up(self):
        self.exemplar.start_run()

        # sleep_time = 60 # Same sleep time as the one in the EWS class
        # time.sleep(sleep_time)

        while True:
            time.sleep(1)
            print("trying to connect...")
            # response = get_response_for_get_request("http://localhost:8080/meta/get_config")
            response = get_response_for_get_request("http://localhost:2011/meta/get_config")
            print(response.status_code)
            if response.status_code < 400:
                break
        self.server.start_run()
        while True:
            time.sleep(1)
            print("trying to connect...")
            response = get_response_for_get_request("http://localhost:8000")
            print(response.status_code)
            if response.status_code < 400:
                return

if __name__ == '__main__':
    unittest.main()
