from UPISAS.strategies.empty_strategy import EmptyStrategy


import sys
import docker
from UPISAS.exemplars.your_exemplar import EWS, FastAPI
import time
import csv




# [total, text, image]
client_combinations = [
    [7, 0, 7],
    [7, 2, 5],
    [7, 4, 3],
    [7, 5, 2],
    [7, 7, 0],
    [15, 0, 15],
    [15, 5, 10],
    [15, 8, 7],
    [15, 10, 5],
    [15, 15, 0],
    [30, 0, 30],
    [30, 10, 20],
    [30, 15, 15],
    [30, 20, 10],
    [30, 30, 0],
]



if __name__ == '__main__':

    exemplar = EWS(auto_start=True)
    server = FastAPI(auto_start=True)

    docker_client = docker.from_env()
    network = docker_client.networks.create("test_network")

    network.connect(exemplar.exemplar_container)
    network.connect(server.exemplar_container)

    text_command = "cd ../ws_clients && dana ClientTextPattern.o"
    image_command = "cd ../ws_clients && dana ClientImagePattern.o"

    exemplar.start_run()
    sleep_time = 120 # Same sleep time as the one in the EWS class
    time.sleep(sleep_time)
    server.start_run()

    print("Both containers up and running...")


    strategy = EmptyStrategy(server)
    strategy.get_adaptation_options(with_validation=False)
    configs = list(strategy.knowledge.adaptation_options.get("configs"))

    id = 0
    train_data = []
    for config in configs:
        config_id = config.get("id")
        config_composition = config.get("config")

        print("----------------------------------------------------")
        strategy.execute(config, with_validation=False)
        time.sleep(10)

        for client_combination in client_combinations:
            id += 1

            total_client_count = client_combination[0]
            text_client_count = client_combination[1]
            image_client_count = client_combination[2]
            print(f"Text clients: {text_client_count}, Image clients: {image_client_count}")

            for i in range(text_client_count):
                exemplar.exemplar_container.exec_run(cmd=['timeout', '-s', 'SIGINT', '10s', 'bash', '-c', text_command], detach=True)
            for i in range(image_client_count):
                exemplar.exemplar_container.exec_run(cmd=['timeout', '-s', 'SIGINT', '10s', 'bash', '-c', image_command], detach=True)

            time.sleep(10)

            data = strategy.monitor(with_validation=False)
            metrics = list(data.get("metrics"))
            response_time = metrics[0].get("value")
            counter = metrics[0].get("counter")
            events = list(data.get("events"))
            text_counter = 0
            image_counter = 0
            for event in events:
                if event.get("type") == "text":
                    text_counter = event.get("counter")
                    break
            for event in events:
                if event.get("type") == "image":
                    image_counter = event.get("counter")
                    break

            train_data.append([id, total_client_count, text_client_count, image_client_count, config_id, config_composition, response_time, counter, text_counter, image_counter])


    if exemplar and exemplar.exemplar_container:
        exemplar.stop_container()
    if server and server.exemplar_container:
        server.stop_container()
    if network:
        network.remove()

    # Specify the file path
    csv_file_path = 'train_data.csv'

    # Write data to the CSV file
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Total Clients", "Text Clients", "Image Clients", "Config ID", "Config Composition", "Response Time", "Counter", "Text Counter", "Image Counter"])
        writer.writerows(train_data)

    sys.exit(0)