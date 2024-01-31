from gym import spaces
from UPISAS.adaptation.DQN import DQN
from UPISAS.strategy import Strategy
from pprint import pprint
import numpy as np
import time

class DingnetDQNStrategy(Strategy):
    """
    A class which implements an adaption strategy for the DingNet exemplar based on a Deep Q-Learning.

    The strategy follows the MAPE-K reference model.

    Attributes
    ----------
    dqn : DQN
        The model for Deep Q-Learning.
    prev_state : (bool, np.array)
        A tuple indicating if a previous state exists and the previous state if applicable.
    prediction : int
        The spreading factor to be applied.
    action : int
        The action predicted by the model.

    Methods
    -------
    get_latest_monitor_data(mote_index=0)
        Returns the last monitored data of a given mote.
    get_adaptation_range(adaptation_name)
        Returns the range of possible adaptation values for a given adaptation.
    get_state()
        Returns the last monitored state consisting of the packet loss.
    calculate_reward(prev_state, curr_state)
        Calculates the reward for the Q learning based on the previous and the current state.
    analyze()
        Returns True if an adaptation is necessary because the predicted spreading factor differs from the currently
        set spreading factor, otherwise returns False.
    plan()
        Plans the adaption, applies the predicted action and trains the DQN model with the newly monitored state.
    step(spreading_factor)
        Executes one step of the Q learning by applying the given adaptation, waiting for one second and monitoring the
        new mote state.
    """
    def __init__(self, exemplar):
        """
        Creates a new instance of a DingnetDQNStrategy for a given DingNet exemplar.

        Parameters
        ----------
        exemplar : DingNet
            The DingNet exemplar to adapt.
        """
        super().__init__(exemplar)

        # Populate schemas for validation
        self.get_adaptation_options_schema()
        self.get_execute_schema()
        self.get_monitor_schema()

        # Populate data for environment initialization
        self.monitor()
        self.get_adaptation_options()

        _min, _max = map(int, self.get_adaptation_range('spreading_factor'))
        self.dqn = DQN(action_space=spaces.Discrete(_max - _min + 1))
        self.prev_state = (False, None)
        self.prediction = None
        self.action = None

    def get_latest_monitor_data(self, mote_index = 0):
        """
        Returns the last monitored data of a given mote.

        Parameters
        ----------
        mote_index : int, optional
            The index of the monitored mote. It defaults to 0.

        Returns
        -------
        np.array
            The state of the given mote that was most recently monitored.

        Raises
        ------
        RuntimeError
            If the data does not contain mote states, there is no history of mote states,
            the mote index is out of range or there is no data for the given mote.
        """
        monitored_data = self.knowledge.monitored_data
        
        if 'moteStates' not in monitored_data:
            raise RuntimeError("moteState not in monitored data")
        
        if not monitored_data['moteStates']:
            raise RuntimeError("no moteState monitor history")

        if len(monitored_data['moteStates'][-1]) < mote_index + 1:
            raise RuntimeError(f"no moteState for mote {mote_index}")
            
        if not monitored_data['moteStates'][-1][mote_index]:
            raise RuntimeError(f"no mote data for mote {mote_index} in moteStates in monitored data")

        return monitored_data['moteStates'][-1][mote_index]

    def get_adaptation_range(self, adaptation_name):
        """
        Returns the range of possible adaptation values for a given adaptation.

        Parameters
        ----------
        adaptation_name : string
            The name of the adaptation.

        Returns
        -------
        (int, int)
            The minimum and maximum value of adaptation values.

        Raises
        ------
        ValueError
            If the given adaptation name does not correspond to a known adaptation.
        """
        adaptation_data = self.knowledge.adaptation_options['items']

        for item in adaptation_data:
            if item['name'] == adaptation_name:
                return item['minValue'], item['maxValue']

        raise ValueError(f"Adaptation {adaptation_name} not found")

    def get_state(self):
        """
        Returns the last monitored state consisting of the packet loss.

        Returns
        -------
        np.array
            The last monitored state, which contains the packet loss or 0 if no packet loss has been monitored.
        """
        data = self.get_latest_monitor_data()

        return np.array([
            data['packetsLost'] if 'packetsLost' in data else 0,
        ]
    )

    def calculate_reward(self, prev_state, curr_state):
        """
        Calculates the reward for the Q learning based on the previous and the current state.

        Parameters
        ----------
        prev_state : np.array
            The previous state of the mote before the adaptation.
        curr_state : np.array
            The current state of the mote after applying the adaptation.

        Returns
        -------
        int
            The calculated reward for the Q learning.
        """
        if not prev_state[0]:
            return -curr_state[0]

        prev_packets_lost = prev_state[1][0]
        new_packets_lost = curr_state[0]

        # Reward based on new amount of packets lost. Less is better.
        return -(new_packets_lost - prev_packets_lost)

    def analyze(self):
        """
        Returns True if an adaptation is necessary because the predicted spreading factor differs from the currently
        set spreading factor, otherwise returns False.

        This function implements the Analyze step of the MAPE-K reference model.

        Returns
        -------
        bool
            True if adaptation is necessary because the predicted spreading factor differs from the currently
            set spreading factor, otherwise False.
        """
        min_spreading_factor, _ = self.get_adaptation_range('spreading_factor')
        curr_state = self.get_state().reshape((1,1))
        action = self.dqn.act(curr_state)
        spreading_factor = min_spreading_factor + action

        self.prediction = spreading_factor
        self.action = action

        # No need to adapt if it is the same as the current SF
        if self.get_latest_monitor_data()['sf'] == spreading_factor:
            # Do a blank monitor just so we have the same amount of monitor calls whether
            # we call step() (in plan()) or not
            self.monitor(with_validation=False)
            return False
        else:
            return True

    def plan(self):
        """
        Plans the adaption, applies the predicted action and trains the DQN model with the newly monitored state.

        This function implements the Plan step of the MAPE-K reference model.

        Returns
        -------
        bool
            True
        """
        curr_state = self.get_state().reshape((1,1))
        new_state, reward = self.step(self.prediction)
        target = self.dqn.target_model.predict(curr_state, verbose=False)
        Q_future = max(self.dqn.target_model.predict(new_state, verbose=False)[0])
        target[0][self.action] = reward + Q_future * self.dqn.gamma
        self.dqn.model.fit(curr_state, target, epochs=1, verbose=False)
        self.dqn.target_train()

        return True

    def step(self, spreading_factor):
        """
        Executes one step of the Q learning by applying the given adaptation, waiting for one second and monitoring the
        new mote state.

        Parameters
        -----------
        spreading_factor : int
            The spreading factor to be applied.

        Returns
        -------
        (np.array, int)
            A tuple containing the new state of the mote and the calulated reward.
        """
        self.knowledge.plan_data = {
            'items': [
                {
                    'id': 0,
                    'adaptations': [
                        {
                            'name': 'spreading_factor',
                            'value': spreading_factor
                        }
                    ]
                }
            ]
        }

        prev_state = (True, self.get_state().reshape((1,1)))
        print(f"Changing spreading factor: {self.prediction}")
        self.execute(self.knowledge.plan_data, with_validation=False)
        time.sleep(1)
        self.monitor(with_validation=False)

        return self.get_state().reshape((1,1)), self.calculate_reward(prev_state, self.get_state())
    

