from UPISAS.strategy import Strategy
import pandas as pd, numpy as np
from sklearn.linear_model import LogisticRegression
from contextualbandits.online import AdaptiveGreedy, EpsilonGreedy, LinUCB
from sklearn.linear_model import SGDClassifier
from contextualbandits.linreg import LinearRegression
from copy import deepcopy

class ContextualBanditStrategy(Strategy):

    def exponential_decay_reward(self, avg_response_time):
        scale_factor = 0.0001
        if isinstance(avg_response_time, np.ndarray):
            return np.where(avg_response_time > 0, np.exp(-avg_response_time * scale_factor), 0)
        else:
            return np.exp(-avg_response_time * scale_factor) if avg_response_time > 0 else 0


    def simulate_epsilon_greedy_rounds(self, model, rewards, actions_hist, features, labels, batch_size):

        # importing data file
        data = pd.read_csv('./data/train_data_with_comp.csv')

        # Batch training
        for i in range(0, len(features), batch_size):
            batch_end = min(i + batch_size, len(features))
            batch_X = features[i:batch_end]
            batch_y = labels[i:batch_end]
            rewards_batch = np.array([])
            rewards_batch = rewards_batch.reshape(-1,1)

            # Predicting the actions for the batch using the model
            actions_this_batch = model.predict(batch_X).astype('uint8')

            # Calculate rewards obtained in the current batch based on the chosen actions
            # Access the data file to get the corresonpding rewards for predicted actions
            for j in range(len(batch_X)):
                # Finding the reward for each predicted action using features from the dataset
                action_idx = actions_this_batch[j]
                feature_subset = data[
                    (data['Total Clients'] == batch_X[j][0]) &
                    (data['Text Clients'] == batch_X[j][1]) &
                    (data['Image Clients'] == batch_X[j][2]) &
                    (data['Config ID'] == action_idx)
                ]

                if not feature_subset.empty:
                    avg_response_time = feature_subset['Response Time'].values[0] / feature_subset['Counter'].values[0]
                    reward = self.exponential_decay_reward(avg_response_time)
                    rewards_batch = np.append(rewards_batch, reward)

            # Append rewards obtained in the current batch to the 'rewards' list
            rewards = np.append(rewards, rewards_batch)

            # Update actions_hist with the predicted actions for this batch
            actions_hist = np.append(actions_hist, actions_this_batch)

            # Update the model using the current batch's features, predicted actions, and rewards
            model.partial_fit(features[:batch_end], actions_hist, rewards)

        return actions_hist


    def train_model(self):

        # importing data file
        data = pd.read_csv('./data/train_data_with_comp.csv')

        # Feature engineering
        data['Text_to_Total_Ratio'] = data['Text Clients'] / data['Total Clients']
        data['Image_to_Total_Ratio'] = data['Image Clients'] / data['Total Clients']
        data['Text_vs_Image'] = data['Text Clients'] - data['Image Clients']
        data['Avg_Response_Time'] = data['Response Time'] / data['Counter']

        # Adding context features - main components in config composition
        context_features = ['Request', 'Http', 'Compression', 'Cache']
        feature_columns = ['Total Clients', 'Text Clients', 'Image Clients', 'Text_to_Total_Ratio', 'Image_to_Total_Ratio', 'Text_vs_Image'] + context_features
        features = data[feature_columns]
        features = features.to_numpy()

        # Rewards array
        labels = data['Avg_Response_Time'].to_numpy()
        labels = labels.reshape(-1, 1)

        # Actions array
        nchoices = data['Config ID'].to_numpy()
        choices_array = np.unique(nchoices)

        rewards_epsilon_greedy = np.array([])
        actions_hist_epsilon_greedy = np.array([], dtype=np.uint8)
        base_ols = LinearRegression(lambda_=10., fit_intercept=True, method="sm")

        # Using Contextual Bandit Alogorithms
        self.model = AdaptiveGreedy(deepcopy(base_ols), nchoices = choices_array,
                                            smoothing = (1,2), beta_prior = None,
                                            decay_type = 'percentile', decay = 0.9997, batch_train = True,
                                            random_state = 4444)

        # Switch to LinUCB or Epsilon Greedy by assigning it to self.model
         
        # linucb = LinUCB(nchoices = nchoices, beta_prior = None, alpha = 0.1,
        #         ucb_from_empty = False, random_state = 1111)

        # epsilon_greedy_nodecay = EpsilonGreedy(deepcopy(base_ols), nchoices = choices_array,
        #                                     smoothing = (1,2), beta_prior = None,
        #                                     decay = None, batch_train = True,
        #                                     deep_copy_buffer = False, random_state = 6666)

        batch_size = 50

        # Set initial random seed
        np.random.seed(1)

        # Generate random indices for the first batch
        random_indices = np.random.choice(len(data), batch_size, replace=False)

        # Select the first batch based on the randomly generated indices
        first_batch_x = features[random_indices]
        first_batch_y = np.array([self.exponential_decay_reward(x) for x in labels[random_indices]])
        first_batch_actions = nchoices[random_indices]

        # Fitting the Epsilon Greedy model with the training data for first batch
        self.model.fit(X=first_batch_x, a=first_batch_actions, r=first_batch_y)

        # Start batch training by calling the method
        actions_hist_epsilon_greedy = self.simulate_epsilon_greedy_rounds(
            self.model, rewards_epsilon_greedy, actions_hist_epsilon_greedy, features, labels, batch_size
        )

        self.current_config = 0


    def analyze(self):
        print("----------------- ANALYZE -----------------")
        data = self.knowledge.monitored_data
        data = pd.DataFrame([self.knowledge.monitored_data])
        counter = int(data.at[0, "Counter"])
        avg_response_time = data.at[0, "Response Time"] / data.at[0, "Counter"]

        print(f"[Analysis]\tAverage Response Time: {avg_response_time}\tCounter: {counter}")

        # Check against the thresholds to decide if the system needs adaptation
        # The counter threshold is set to 1000 because monitor data is collected over a 10 second interval.
        # Essentially the threshold is 100 per second.
        if (avg_response_time > 5 or counter > 1000):
            self.knowledge.analysis_data["avg_response_time"] = avg_response_time
            self.knowledge.analysis_data["counter"] = counter
            return True
        return False

    def plan(self):
        data = pd.DataFrame([self.knowledge.monitored_data])

        # Feature engineering to create more informative features
        data['Text_to_Total_Ratio'] = data['Text Clients'] / data['Total Clients']
        data['Image_to_Total_Ratio'] = data['Image Clients'] / data['Total Clients']
        data['Text_vs_Image'] = data['Text Clients'] - data['Image Clients']
        data['Avg_Response_Time'] = data['Response Time'] / data['Counter']

        #read compositions file for config id and context features
        configs = pd.read_csv('./data/compositions.csv')

        # Preparing the X_test data to predict actions using the trained model
        column_names = ['Total Clients', 'Text Clients', 'Image Clients', 'Text_to_Total_Ratio', 'Image_to_Total_Ratio', 'Text_vs_Image', 'Request', 'Http', 'Compression', 'Cache']
        X_test = pd.DataFrame(np.zeros((1, len(column_names))), columns=column_names)

        # Accessing the monitored data to populate X_test
        X_test.at[0,'Total Clients'] = data.at[0,'Total Clients']
        X_test.at[0,'Text Clients'] = data.at[0,'Text Clients']
        X_test.at[0,'Image Clients'] = data.at[0,'Image Clients']
        X_test.at[0,'Text_to_Total_Ratio'] = data.at[0,'Text_to_Total_Ratio']
        X_test.at[0,'Image_to_Total_Ratio'] = data.at[0,'Image_to_Total_Ratio']
        X_test.at[0,'Text_vs_Image'] = data.at[0,'Text_vs_Image']
        X_test.at[0,'Request'] = configs.loc[self.current_config, 'Request']
        X_test.at[0,'Http'] = configs.loc[self.current_config, 'Http']
        X_test.at[0,'Compression'] = configs.loc[self.current_config, 'Compression']
        X_test.at[0,'Cache'] = configs.loc[self.current_config, 'Cache']

        self.model.partial_fit(X_test, np.array([self.current_config]), np.array([self.exponential_decay_reward(data.at[0,'Avg_Response_Time'])]))

        config_id = int((self.model.predict(X_test))[0])

        print(f"Selected Config: {config_id}")

        config_composition_row = configs[configs['ID'] == config_id]
        config_composition =  config_composition_row['Composition'].values[0]

        # Setting the configuration to plan_data for execute method
        self.knowledge.plan_data = { "id" : config_id,
                    "config": config_composition }

        self.current_config = config_id

        return True
