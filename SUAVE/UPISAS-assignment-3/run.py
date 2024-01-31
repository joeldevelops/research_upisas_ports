import logging
import time

from UPISAS.exemplars.suave import Suave
from UPISAS.strategies.suave_strategy import SuaveStrategy
import signal
import sys

if __name__ == '__main__':
    exemplar = Suave(auto_start=True)
    exemplar.start_run()

    try:
        strategy = SuaveStrategy(exemplar)
        while True:
            time.sleep(2)
            strategy.monitor(with_validation=False)
            if strategy.analyze():
                logging.info("Analyzing & Planning with State Machine")
                if strategy.plan():
                    strategy.execute(strategy.knowledge.plan_data)

    except Exception as e:
        print(e)
        sys.exit(0)
