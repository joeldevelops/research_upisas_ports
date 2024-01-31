
from UPISAS.exemplars.your_exemplar import YourExemplar
from UPISAS.strategy import Strategy
import gym
from gym import spaces
import numpy as np
import pandas as pd

class Adaptive_Planner(gym.Env):
    def __init__(self,exploit,q_table):
        super(Adaptive_Planner, self).__init__()
        # Discretization intervals for action and state spaces
        self.num_actions = 3
        self.binning_action = 5
        self.binning_state = 50
        self.exploit = exploit
        self.q_table_filename = q_table
        
        # Discretization interval for actions maxSpeedAndLengthFactor (1-5), averageEdgeDurationFactor (1-5), freshnessUpdateFactor(10-20)
        self.discretization_intervals_actions = {
            'maxSpeedAndLengthFactor': (1, 5, self.binning_action),
            'averageEdgeDurationFactor': (1, 5, self.binning_action),
            'freshnessUpdateFactor': (10, 20, self.binning_action)
        }

        # Action format
        self.action_format = {
            'maxSpeedAndLengthFactor': 0,
            'averageEdgeDurationFactor': 0,
            'freshnessUpdateFactor': 0
        }

        #50 step binning
        self.discretization_intervals_state = {
            'tripOverhead': (1, 4, self.binning_state),
        }
        
        # Generate action and state spaces
        self.action_space = self.create_multi_discrete_space(self.discretization_intervals_actions)
        self.state_space = self.create_multi_discrete_space(self.discretization_intervals_state)[0]
        # Initialize the Q-table
        self.q_table_shape = tuple([len(self.state_space['tripOverhead']),self.num_actions*self.binning_action])
        # CHANGE TO 0
        # Assuming self.q_table_shape is defined as (50, 15)
        self.q_table = np.random.rand(*self.q_table_shape)
        # Fill the Q-table with zeros
        print("party")
        if(not exploit):
            self.q_table = np.zeros_like(self.q_table)
            df = pd.DataFrame(self.q_table)
            df.to_csv(f'./{self.q_table_filename}', index=False)
            print(self.q_table.shape)
        # Set hyperparameters
        if(exploit):
            self.learning_rate = 0.1
            self.discount_factor = 0.9
            self.exploration_prob = 0
        else:
            self.learning_rate = 0.1
            self.discount_factor = 0.9
            self.exploration_prob = 1

    
    def calculate_median(self, monitored_values, how_much_to_the_past):
        # Extract the last 30 observed values of averageTripOverhead
        last_overheads = monitored_values['tripOverhead'][-how_much_to_the_past:]

        # Replace None value with 0 in the beginning of simulation
        last_overheads = [0 if value is None else value for value in last_overheads]

        # Sort the values in ascending order
        sorted_overheads = sorted(last_overheads)

        # Calculate the median
        n = len(sorted_overheads)
        if n % 2 == 0:
            # If the number of elements is even, average the middle two elements
            median = (sorted_overheads[n // 2 - 1] + sorted_overheads[n // 2]) / 2.0
        else:
            # If the number of elements is odd, take the middle element
            median = sorted_overheads[n // 2]

        return median
        
    
    
    
    def create_multi_discrete_space(self, intervals):
            # Initializing an empty list
            space = []
            # Looping over intervals 
            for key, values in intervals.items():
                lower, upper, interval = values
                # Generate evenly spaced values between the lower and upper bounds
                states = list(np.linspace(lower, upper, interval))
                # Append states to space 
                space.append({key:states})

            space_l = []

            for arr in space:
                space_l.append(len(arr))
            return space

    def discretize_value(self, feature_name, value, discrete_list):
        # Get discretization parameters for the specified feature
        min_value, max_value, step = discrete_list[feature_name]

        # Discretize the value using numpy's arange function
        #discretized_values = np.arange(min_value, max_value + step, step).tolist()
        discretized_values = np.linspace(min_value, max_value, step)
        # Find the closest value in the discretized range
        closest_value = min(discretized_values, key=lambda x: abs(x - value))
        print("old val: ",value," and closest value: ",closest_value)
        # Find the index of the discretized value
        index = list(discretized_values).index(closest_value)
        return closest_value,index

    def step(self, monitored_values,step_number):
        print("Another step")
        self.discretized_states = {}
        self.discretized_actions = {}
        action_format = self.action_format
        # Discretize observed values for both states and actions
        if(not self.exploit):
            self.exploration_prob = 1-(step_number/1000)
        
        # Loop through monitored values
        for feature_name, value in monitored_values.items():
            # Discretization of state space
            if feature_name in self.discretization_intervals_state:
                # Calculate median of the last 30 monitored values
                median = self.calculate_median(monitored_values,30)
                print("median: ", median)
                # Discretize the median value of tripOverhead and get index value
                discretized_state,index = self.discretize_value(feature_name, median, self.discretization_intervals_state)
                self.discretized_states[feature_name] = discretized_state
                self.state_index = index
            if feature_name in self.discretization_intervals_actions:
                # Discretize the value of actions - maxSpeedAndLengthFactor, averageEdgeDurationFactor, freshnessUpdateFactor and get index value
                discretized_action,index = self.discretize_value(feature_name, value[-1], self.discretization_intervals_actions)
                print("action and index:",discretized_action,index)
                self.discretized_actions[feature_name] = discretized_action
                self.action_index = index

        # Choose action using for example epsilon-greedy policy
        actionToTake, action = self.choose_action(self.discretized_actions, self.action_index)

        # Calculate reward
        reward = self.calculate_reward(median)
        return self.state_index,actionToTake,action,reward,median
        
    def _take_action(self, action):
        # Perform the chosen action and get feedback from the system
        # Local import to prevent circular import issue
        from UPISAS.strategies.empty_strategy import EmptyStrategy
        exemplar = YourExemplar(auto_start=True)
        strategy = EmptyStrategy(exemplar,self)
        strategy.execute(action)
        next_state = np.zeros(3)  # Update this based on your environment dynamics
        reward = np.random.randn()  # Placeholder for reward calculation
        done = False  # Placeholder for episode termination logic

        return next_state, reward, done, {}

    def choose_action(self, current__action_format,action_index):
        # Epsilon-greedy action selection
        if np.random.rand() < self.exploration_prob:
            # Explore: choose a random action
            print("Exploring")
            upper_bound = int((self.num_actions * self.binning_action) - 1)
            action = np.random.randint(0, upper_bound)
            # choose one of the three actions from self.action_space (meta action) and a magnitude (out of 5)
            meta_action=action//self.binning_action
            magnitude= action%self.binning_action
            action_space_layered = [list(d.values())[0] for d in self.action_space]
            print("action space: ", action_space_layered)
            key = list(current__action_format.keys())[meta_action]
            print(f"we do action from {current__action_format[key]} which is: {action_space_layered[meta_action][magnitude]}")
            current__action_format[key] = action_space_layered[meta_action][magnitude]
        else:
            # Exploit: choose the action with the highest Q-value
            print("Exploiting")
            path = f'./{self.q_table_filename}'
            q_table_updated = pd.read_csv(path)
            q_values = q_table_updated.iloc[self.state_index]
            print("qvals:",q_values)
            action = np.argmax(q_values)
            meta_action=action//self.binning_action
            magnitude= action%self.binning_action
            action_space_layered = [list(d.values())[0] for d in self.action_space]
            print("action space: ", action_space_layered)
            key = list(current__action_format.keys())[meta_action]
            print(f"we do action from {current__action_format[key]} which is: {action_space_layered[meta_action][magnitude]}")
            current__action_format[key] = action_space_layered[meta_action][magnitude]
        return current__action_format,action
        
    def calculate_reward(self, state):
    
        # Map medianTripOverhead to a reward value between 0 and 1
        # Assuming the worst value is 30 and the best is 1
        min_overhead = 1
        max_overhead = 30

        # Clip the value to make sure it is within the specified range
        clipped_overhead = max(min(state, max_overhead), min_overhead)

        # Map the clipped_overhead to a value between 0 and 1
        # Using linear mapping
        reward = 1.0 - (clipped_overhead - min_overhead) / (max_overhead - min_overhead + 1e-10)

        return reward
