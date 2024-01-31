import sys
import docker
from UPISAS.exemplars.your_exemplar import EWS, FastAPI
import time
import csv

from UPISAS.strategies.contextual_bandit_strategy import ContextualBanditStrategy

# [total, text, image]
client_combinations = [
    [40, 0, 40],
    [40, 10, 30],
    [40, 20, 20],
    [40, 30, 10],
    [40, 40, 0],
    [50, 0, 50],
    [50, 15, 35],
    [50, 25, 25],
    [50, 35, 15],
    [50, 50, 0],
    [60, 0, 60],
    [60, 15, 45],
    [60, 30, 30],
    [60, 45, 15],
    [60, 60, 0],
    [70, 0, 70],
    [70, 20, 50],
    [70, 35, 35],
    [70, 50, 20],
    [70, 70, 0],
    [80, 0, 80],
    [80, 20, 60],
    [80, 40, 40],
    [80, 60, 20],
    [80, 80, 0],
    [90, 0, 90],
    [90, 25, 65],
    [90, 45, 45],
    [90, 65, 25],
    [90, 90, 0],
    [100, 0, 100],
    [100, 25, 75],
    [100, 40, 60],
    [100, 60, 40],
    [100, 75, 25],
    [100, 100, 0],
]

def extract_metrics(data):
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
    return response_time, counter, text_counter, image_counter


# signal.signal(signal.SIGINT, signal_handler)
if __name__ == '__main__':

    exemplar = EWS(auto_start=True)
    server = FastAPI(auto_start=True)

    docker_client = docker.from_env()
    network = docker_client.networks.create("test_network")

    network.connect(exemplar.exemplar_container)
    network.connect(server.exemplar_container)

    strategy = ContextualBanditStrategy(server)
    strategy.train_model()
    print("Training model...")

    text_command = "cd ../ws_clients && dana ClientTextPattern.o"
    image_command = "cd ../ws_clients && dana ClientImagePattern.o"

    exemplar.start_run()
    sleep_time = 500 # Same sleep time as the one in the EWS class
    time.sleep(sleep_time)
    server.start_run()

    print("Both containers up and running...")

    strategy.get_adaptation_options(with_validation=False)

    strategy.get_execute_schema()

    id = 0
    results = []

    for client_combination in client_combinations:
        id += 1

        total_client_count = client_combination[0]
        text_client_count = client_combination[1]
        image_client_count = client_combination[2]

        print("=====================================================")
        print(f"Text clients: {text_client_count}, Image clients: {image_client_count}")

        for i in range(text_client_count):
            exemplar.exemplar_container.exec_run(cmd=['timeout', '-s', 'SIGINT', '10s', 'bash', '-c', text_command], detach=True)
        for i in range(image_client_count):
            exemplar.exemplar_container.exec_run(cmd=['timeout', '-s', 'SIGINT', '10s', 'bash', '-c', image_command], detach=True)

        time.sleep(10)

        response_time, counter, text_counter, image_counter = extract_metrics(strategy.monitor(with_validation=False))
        strategy.knowledge.monitored_data = {
            'Text Clients': text_client_count,
            'Image Clients': image_client_count,
            'Total Clients': total_client_count,
            'Response Time': response_time,
            'Counter': counter,
            'Text Counter': text_counter,
            'Image Counter': image_counter,
        }
        config = strategy.current_config
        avg_response_time = response_time/counter
        print(f"Config: {config}, Response time: {avg_response_time}")

        results.append([id, total_client_count, text_client_count, image_client_count, config, avg_response_time])

        if strategy.analyze():
            if strategy.plan():
                strategy.execute(strategy.knowledge.plan_data)
                time.sleep(5)


    if exemplar and exemplar.exemplar_container:
        exemplar.stop_container()
    if server and server.exemplar_container:
        server.stop_container()
    if network:
        network.remove()


    # Specify the file path
    algorithm_name = "adaptive_greedy"
    csv_file_path = f'results/results_{algorithm_name}.csv'

    # Write data to the CSV file
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Total_Clients", "Text_Clients", "Image_Clients", "Config", "Avg_Response_Time"])
        writer.writerows(results)

    sys.exit(0)