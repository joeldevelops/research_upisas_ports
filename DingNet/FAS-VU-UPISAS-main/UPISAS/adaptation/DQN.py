import gym
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense, Input
from keras.optimizers import Adam

from collections import deque

class DQN:
    """
    A class representing Deep Q-Learning. This class was adopted from
    https://towardsdatascience.com/reinforcement-learning-w-keras-openai-dqns-1eed3a5338c

    Attributes
    ----------
    action_space : gym.spaces.Discrete
        A discrete space of actions that can be taken from every state.
    memory : collections.deque
        A double-ended queue to save a sequence of the recent states, actions, and rewards.
    gamma : double
        The future rewards depreciation factor.
    epsilon: double
        The fraction of time corresponding to exploration.
    epsilon_min : double
        The minimal fraction of time corresponding to exploration.
    epsilon_decay : double
        The factor the probability of exploration decreases by in every iteration.
    learning_rate : double
        The standard learning rate parameter for stochastic gradient descent.
    tau : double
        The weight of the interpolation between the weights of the model and the target model when training the target
        model. The higher this value, the stronger the impact of the model weights during the update.
    model: keras.Sequential
        The model to predict what actions to take.
    target_model: keras.Sequential
        The model to predict the target actions of the other model.

    Methods
    -------
    create_model()
        Create a feedforward neural network model for mapping the state to the next action
    act(state)
        Determines the action to take based on the current state.
    target_train()
        Trains the target model to reorient the goals.
    """
    def __init__(self, action_space):
        """
        Creates a new DQN object with a given space of actions for the reinforcement learning.

        Parameters
        ----------
        action_space : gym.spaces.Discrete
            A discrete space of possible actions for the reinforcement learning.
        """
        self.action_space = action_space
        self.memory  = deque(maxlen=2000)
        
        self.gamma = 0.85
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.005
        self.tau = .125
        self.model        = self.create_model()
        # According to DeepMind, a separate target model improves convergence during training.
        self.target_model = self.create_model()

    def create_model(self):
        """
        Create a feedforward neural network model for mapping the state to the next action to take.

        Returns
        -------
        keras.Sequential
            A feedforward multi-layer neural network model for mapping the state to the next action to take.
        """
        model = Sequential()
    
        model.add(Dense(24, input_dim=1, activation="relu"))
        model.add(Dense(48, activation="relu"))
        model.add(Dense(24, activation="relu"))
        model.add(Dense(self.action_space.n))
        model.compile(loss="mean_squared_error", optimizer=Adam(lr=self.learning_rate))
    
        return model

    def act(self, state):
        """
        Determines the action to take based on the current state.

        Parameters
        ----------
        state : np.array
            The current state of the mote being adapted

        Returns
        -------
        int
            The index of the action to take within the action space.
        """
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        # Exploration
        if np.random.random() < self.epsilon:
            return self.action_space.sample()
        return np.argmax(self.model.predict(state, verbose=False)[0])

    def target_train(self):
        """
        Trains the target model to reorient the goals. The weights of the target model are interpolated between
        the weights of the model and the current weights of the target model based on the weight tau.
        """
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)