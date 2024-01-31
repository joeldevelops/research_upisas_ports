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
        if(number_of_cars>=501 and number_of_cars<=700):
            print('medium traffic')
        if(number_of_cars>=701 and number_of_cars<=800):
            print('high traffic')
        return True
    # Planner method 
    def plan(self,step_number):
        state, action_schema, action,reward,median = self.Planner.step(self.knowledge.monitored_data,step_number)
        print("action: ",action)
        print("reward: ",reward)
        print("state: ",state)
        return state,action_schema, action,reward,median
    
    # calculating q value for the latest action taken
    def calculate_previous_Q_value(self, state, action,reward,learning_rate,discount_factor,filename):
        path = './{filename}'
        q_table = pd.read_csv(path)
        current_q_value = q_table.iloc[state,action]
        next_max_q_value= max(q_table.iloc[state])
        new_q_value = (1 - learning_rate) * current_q_value + \
         learning_rate * (reward + discount_factor * next_max_q_value)
        q_table.iloc[state,action] = new_q_value
        q_table.to_csv(path, index=False)
        return new_q_value
        

