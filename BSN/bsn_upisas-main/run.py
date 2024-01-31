from UPISAS.strategies.bsn_strategy import BSNStrategy, plot
from UPISAS.exemplars.your_exemplar import BSN
from signal import signal, SIGINT
from time import sleep
import sys


def signal_handler(sig, _):
    print(f"Received signal {sig}. Exiting.")
    exemplar.stop_container()
    sys.exit(0)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    signal(SIGINT, signal_handler)
    exemplar = BSN(auto_start=True)
    exemplar.start_run()

    history = {key: [] for key in ['/ecg_data', '/abpd_data', '/abps_data', '/thermometer_data', '/oximeter_data',
                                   '/glucosemeter_data']}

    try:
        sleep(5) # Sleep to wait for HTTP-Endpoint to start
        strategy = BSNStrategy(exemplar)
        print('[PREAMBLE]\t Started strategy...')

        # Validation is disabled. The http endpoint also uses the jsonschema module, not sure why they are not equal
        while True:
            strategy.monitor(with_validation=False)
            if strategy.analyze():
                if strategy.plan():
                    for adaptation in strategy.knowledge.plan_data.values():
                        strategy.execute(adaptation, with_validation=False)
            if 'target_frequencies' in strategy.knowledge.analysis_data:
                plot(history, strategy.knowledge.analysis_data['target_frequencies'])
            sleep(0.1)

    except Exception as e:
        print("System has hit " + type(e).__name__ + ": " + str(e))
    finally:
        exemplar.stop_container()
        sys.exit(0)
