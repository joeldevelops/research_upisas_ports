import signal
from UPISAS.exemplars.DingNet import DingNet
from UPISAS.exemplars.swim import SWIM
from UPISAS.strategies.demo_strategy import DemoStrategy
from UPISAS.strategies.dingnet_strategy import DingnetDQNStrategy
from UPISAS.tests.swim.test_swim_interface import TestSWIMInterface
import sys
import logging
import time

import matplotlib.pyplot as plt

logging.getLogger().setLevel(logging.ERROR)

MIN_ITERATION_DELAY = 1.25
SEED = 42 # The answer to life, the universe and everything

def get_history(monitored_data, property, mote_index = 0):
    return [x[mote_index][property] for x in monitored_data['moteStates']]

def do_run(adaptation: bool, iters: int = 150, seed: int = SEED):
    try:
        exemplar = DingNet(auto_start=True)
        signal.signal(signal.SIGINT, lambda sig, frame: exemplar.stop_container() and sys.exit(0))
        exemplar.start_run(seed)
        strategy = DingnetDQNStrategy(exemplar)
        i = 0

        while strategy.knowledge.monitored_data['isRunning'][-1] and i < iters:
            start = time.perf_counter()
            strategy.monitor(with_validation=False)
            if adaptation and strategy.analyze():
                strategy.plan()

            # Theoretical optimum for testing seed
            # if not adaptation:
            #     strategy.execute({
            #         'items': [
            #             {
            #                 'id': 0,
            #                 'adaptations': [
            #                     {
            #                         'name': 'spreading_factor',       
            #                         'value': 7 if i < 50 else 12
            #                     }
            #                 ]
            #             }
            #         ]
            #     }, with_validation=False)

            i += 1

            # Every 50 iterations, stop the run and start a new one with a new seed
            if (i % 50 == 0):
                exemplar.stop_run()
                seed += 1
                time.sleep(5)
                exemplar.start_run(seed)
                print(f"Completed {i} iterations")


            # Make each iteration take the same amount of time
            iteration_time = time.perf_counter() - start
            if (iteration_time > MIN_ITERATION_DELAY):
                print(f"Warning: iteration took longer than {MIN_ITERATION_DELAY} seconds ({iteration_time} seconds)")
                continue
            time.sleep(MIN_ITERATION_DELAY - iteration_time)
        
        exemplar.stop_container()

        return strategy.knowledge.monitored_data
    except Exception as e:
        exemplar.stop_container()
        raise RuntimeError(e)

if __name__ == '__main__':
    iterations = 100
    monitored_data_with_adaptation = do_run(True, iterations)
    monitored_data_without_adaptation = do_run(False, iterations)

    packet_loss_history_with_adaptation = [x for i, x in enumerate(get_history(monitored_data_with_adaptation, 'packetLoss')) if i % 2 == 0]
    packet_loss_history_without_adaptation = get_history(monitored_data_without_adaptation, 'packetLoss')
    spreading_factor_history_with_adaptation = [x for i, x in enumerate(get_history(monitored_data_with_adaptation, 'sf')) if i % 2 == 0]
    spreading_factor_history_without_adaptation = get_history(monitored_data_without_adaptation, 'sf')

    # Create the plots
    fig = plt.figure(constrained_layout=True,figsize=(20,10))
    subplots = fig.subfigures(2, 2)

    subplots[0, 0].suptitle('Spreading factor and packet loss over time with adaptation')
    subplots[0, 1].suptitle('Spreading factor and packet loss over time without adaptation')

    min_packet_loss = min(min(packet_loss_history_with_adaptation), min(packet_loss_history_without_adaptation))
    max_packet_loss = max(max(packet_loss_history_with_adaptation), max(packet_loss_history_without_adaptation))

    axis1_with_adaptation = subplots[0, 0].subplots()
    axis1_with_adaptation.set_xlabel('Iteration')
    axis1_with_adaptation.set_xticks(range(0, iterations + 1, 10))
    axis1_with_adaptation.set_ylabel('Packet loss')
    axis1_with_adaptation.set_ylim([min_packet_loss, max_packet_loss])
    axis1_with_adaptation.plot(packet_loss_history_with_adaptation, color='blue', label='Packet loss')
    axis1_with_adaptation.tick_params(axis='y')

    axis2_with_adaptation = axis1_with_adaptation.twinx()
    axis2_with_adaptation.set_ylabel('Spreading factor')
    axis2_with_adaptation.set_yticks(range(7, 13))
    axis2_with_adaptation.step(range(0, iterations + 1), spreading_factor_history_with_adaptation, label='Spreading factor', color='orange')
    axis2_with_adaptation.tick_params(axis='y')

    axis1_without_adaptation = subplots[0, 1].subplots()
    axis1_without_adaptation.set_xlabel('Iteration')
    axis1_without_adaptation.set_xticks(range(0, iterations + 1, 10))
    axis1_without_adaptation.set_ylabel('Packet loss')
    axis1_without_adaptation.set_ylim([min_packet_loss, max_packet_loss])
    axis1_without_adaptation.plot(packet_loss_history_without_adaptation, color='blue', label='Packet loss')
    axis1_without_adaptation.tick_params(axis='y')

    axis2_without_adaptation = axis1_without_adaptation.twinx()
    axis2_without_adaptation.set_ylabel('Spreading factor')
    axis2_without_adaptation.set_yticks(range(7, 13))
    axis2_without_adaptation.step(range(0, iterations + 1), spreading_factor_history_without_adaptation, label='Spreading factor', color='orange')
    axis2_without_adaptation.tick_params(axis='y')

    axis1_comparison = subplots[1, 0].subplots()
    axis1_comparison.set_xlabel('Iteration')
    axis1_comparison.set_xticks(range(0, iterations + 1, 10))
    axis1_comparison.set_ylabel('Packet loss')
    axis1_comparison.set_ylim([min_packet_loss, max_packet_loss])
    axis1_comparison.plot(packet_loss_history_with_adaptation, color='blue', label='Packet loss with adaptation')
    axis1_comparison.plot(packet_loss_history_without_adaptation, color='orange', label='Packet loss without adaptation')

    subplots[0, 0].legend(bbox_to_anchor = (0.9, 0.25))
    subplots[0, 1].legend(bbox_to_anchor = (0.9, 0.25))
    subplots[1, 0].legend(bbox_to_anchor = (0.9, 0.25))
    plt.show()

    print(f"With adaptation: avg_packet_loss={monitored_data_with_adaptation['moteStates'][-1][0]['packetLoss']}")
    print(f"Without adaptation: avg_packet_loss={monitored_data_without_adaptation['moteStates'][-1][0]['packetLoss']}")
