import json
import time

from numpy import median
from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.swim import SWIM
import signal
import sys

from UPISAS.exemplars.your_exemplar import YourExemplar
from UPISAS.strategies.empty_strategy import EmptyStrategy
from UPISAS.strategies.RL_crowd_nav import Adaptive_Planner

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
exploit = False
amount_of_runs = 1000

if __name__ == '__main__':
    rounds = 0
    planner = Adaptive_Planner()
    exemplar = YourExemplar(auto_start=True)
    exemplar.start_run()
    time.sleep(30)
    
    # add try and catch for conditions when an endpoint might not be repsonsive for a time
    try:
        strategy = EmptyStrategy(exemplar,planner)
        median_saved = []
        while rounds<=amount_of_runs+1:
            
            time.sleep(4)
            count = 0
            rounds+=1
            print(f"--------------- NEW ROUND {rounds} ---------------")
            try:
                print("before monitor")
                strategy.monitor(with_validation=False)
                time.sleep(0.5)
                # analyze the monitored data 
                print("before analyse")
                if strategy.analyze():
                    print("before plan")
                    # planning phase 
                    state,action_schema, action,reward,median_plan = strategy.plan(rounds)
                    # execute phase
                    print("before execute")
                    strategy.execute(action_schema, with_validation=False)

            
            except json.JSONDecodeError as json_error:
                print(f"JSON decoding error: {json_error}")
                for attempt in range(MAX_RETRIES):
                    print(f"Retrying in {RETRY_DELAY} seconds (attempt {attempt + 1}/{MAX_RETRIES})...")
                    time.sleep(RETRY_DELAY)
                    try:
                        print("before monitor (retry)")
                        strategy.monitor(with_validation=False)
                        time.sleep(0.5)
                        print("before analyse (retry)")
                        if strategy.analyze():
                            print("before plan (retry)")
                            state,action_schema, action,reward,median_plan = strategy.plan(rounds)
    
                        # execute phase
                        strategy.execute(action_schema, with_validation=False)
            
                        break  # Break out of the retry loop if successful
                        
                    except json.JSONDecodeError as retry_json_error:
                        print(f"JSON decoding error on retry: {retry_json_error}")
                                
                else:
                    print("Max retries reached. Going back to main try")
                    
    except Exception as e:
        print(e)         
        exemplar.stop()
        sys.exit(0)