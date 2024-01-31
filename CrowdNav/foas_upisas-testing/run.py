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
# if exploit = true, the Q-table will be used for actions, otherwise random actions (or predefined learing exploration rate) will be used
exploit = True
amount_of_runs = 300
file_to_save_median_values = "q_table_500.json"
filename = "q_table_500.csv"

if __name__ == '__main__':
    rounds = 0
    planner = Adaptive_Planner(exploit,filename)
    exemplar = YourExemplar(auto_start=True)
    exemplar.start_run()
    time.sleep(30)
    
    # add try and catch for conditions when an endpoint might not be repsonsive for a time
    try:
        strategy = EmptyStrategy(exemplar,planner)
        median_saved = []
        
        while rounds<amount_of_runs+1:
            
            time.sleep(4)
            count = 0
            rounds+=1
            print(f"--------------- NEW ROUND {rounds} ---------------")
            try: 
                # monitor the values until there are 30 values for calculating median trip overhead
                while(count<30):
                    print("before monitor")
                    if count == 0:
                        strategy.monitor(with_validation=False, new_data=True)
                    else:
                        strategy.monitor(with_validation=False)
                    time.sleep(0.5)
            
                    try:
                        count = len(strategy.knowledge.monitored_data["tripOverhead"])
                        print("waiting until 30 values have been gathered: ",count)
                    except:
                        count = 0
                        
                # analyze the monitored data 
                print("before analyse")
                if strategy.analyze():
                    print("before plan")
                    # planning phase 
                    state,action_schema, action,reward,median_plan = strategy.plan(rounds)
                    median_saved.append(median_plan)
                    print("median trip overhead: ", median(median_saved))
                    # exploring and updating the q values
                    if(not exploit):
                        print("before execute")
                        strategy.execute(action_schema, with_validation=False)
                        q_value = strategy.calculate_previous_Q_value(state, action, reward,0.1,0.1)
                        print("q_value for this action: ", q_value)
                    else:
                        print("Exploit")
                        strategy.execute(action_schema, with_validation=False)

            
            except json.JSONDecodeError as json_error:
                print(f"JSON decoding error: {json_error}")
                for attempt in range(MAX_RETRIES):
                    print(f"Retrying in {RETRY_DELAY} seconds (attempt {attempt + 1}/{MAX_RETRIES})...")
                    time.sleep(RETRY_DELAY)
                    try:
                        while(count<30):
                            print("before monitor (retry)")
                            if count == 0:
                                strategy.monitor(with_validation=False, new_data=True)
                            else:
                                strategy.monitor(with_validation=False)
                            time.sleep(0.5)
                            count= len(strategy.knowledge.monitored_data["tripOverhead"])
                            print("waiting until 30 values have been gathered: ",count)

                        print("before analyse (retry)")
                        if strategy.analyze():
                            print("before plan (retry)")
                            state,action_schema, action,reward,median_plan = strategy.plan(rounds)
                            median_saved.append(median_plan)
                            print("median trip overhead: ", median(median_saved))
    
                            # exploring and updating the q values
                            if(not exploit):
                                print("before execute (retry)")
                                strategy.execute(action_schema, with_validation=False)
                                q_value = strategy.calculate_previous_Q_value(state, action, reward,0.1,0.1)
                                print("our q_value for this action: ", q_value)
                                print("After calculating q values in retry loop")

                            else:
                                print("Exploit")
                                strategy.execute(action_schema, with_validation=False)

                            break  # Break out of the retry loop if successful
                        
                    except json.JSONDecodeError as retry_json_error:
                        print(f"JSON decoding error on retry: {retry_json_error}")
                                
                else:
                    print("Max retries reached. Going back to main try")

        with open(f"./{file_to_save_median_values}", 'w') as file:
            json.dump(median_saved, file)
            print("\n")
        print(median_saved)
            
                    
    except Exception as e:
        print(e)         
        exemplar.stop()
        sys.exit(0)