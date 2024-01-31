import pandas as pd
from UPISAS.strategy import Strategy
import gym
from gym import spaces
import numpy as np
import requests
from UPISAS.strategies.RL_crowd_nav import Adaptive_Planner

class EmptyStrategy(Strategy):
    
    # Initializing the strategy
    def __init__(self, exemplar, Planner:Adaptive_Planner):
        super().__init__(exemplar)
        self.Planner = Planner
        self.data = self.knowledge.monitored_data
       
        
    # analyze method
    def analyze(self):
        number_of_cars = self.data['numberOfCars'][-1]
        # Checking traffic level based on the number of cars
        if(number_of_cars>=101 and number_of_cars<=500):
            print('low traffic')
            return "q_table_500_final.csv"
        if(number_of_cars>=501 and number_of_cars<=700):
            print('medium traffic')
            return "q_table_700_final.csv"
        if(number_of_cars>=701 and number_of_cars<=800):
            print('high traffic')
            return "q_table_800_final.csv"
        return True
    # Planner method 
    def plan(self,step_number,q_table_name):
        state, action_schema, action,reward,median = self.Planner.step(self.knowledge.monitored_data,step_number, q_table_name)
        print("action: ",action)
        print("reward: ",reward)
        print("state: ",state)
        return state,action_schema, action,reward,median
    
    # calculating q value for the latest action taken
    def calculate_previous_Q_value(self, new_state, last_state, last_action, new_reward,learning_rate,discount_factor,path_name):
        path = f'./{path_name}'
        q_table = pd.read_csv(path)
        last_q_value = q_table.iloc[last_state,last_action]
        next_max_q_value= max(q_table.iloc[new_state])
        q_value_for_last_state = (1 - learning_rate) * last_q_value + \
         learning_rate * (new_reward + discount_factor * next_max_q_value)
        q_table.iloc[last_state,last_action] = q_value_for_last_state
        q_table.to_csv(path, index=False)
        return q_value_for_last_state
        

