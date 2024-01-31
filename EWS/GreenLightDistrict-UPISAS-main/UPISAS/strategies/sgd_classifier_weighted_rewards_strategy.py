import pandas as pd
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class SGDClassifierWeightedRewardsStrategy:
    def __init__(self, random_state=42, epsilon=0.1, batch_size=50):
        self.model = SGDClassifier(max_iter=1000, tol=1e-3, random_state=random_state)
        self.scaler = StandardScaler()
        self.epsilon = epsilon
        self.batch_size = batch_size
        np.random.seed(random_state)

    def exponential_decay_reward(self, avg_response_time):
        scale_factor = 0.0001
        return np.exp(-avg_response_time * scale_factor) if avg_response_time > 0 else 0

    def rewards_to_weights(self, rewards):
        rewards = np.array(rewards)
        rewards = (rewards - rewards.min()) / (rewards.max() - rewards.min())
        rewards += 0.1  # Avoid zero weights
        return rewards

    def train_model(self, data_train):
        data_train.fillna(0, inplace=True)

        # Feature engineering
        data_train['Text_to_Total_Ratio'] = data_train['Text Clients'] / data_train['Total Clients']
        data_train['Image_to_Total_Ratio'] = data_train['Image Clients'] / data_train['Total Clients']
        data_train['Text_vs_Image'] = data_train['Text Clients'] - data_train['Image Clients']
        data_train['Avg_Response_Time'] = data_train['Response Time'] / data_train['Counter']

        context_features = ['Request', 'Http', 'Compression', 'Cache']
        feature_columns = ['Total Clients', 'Text Clients', 'Image Clients',
                           'Text_to_Total_Ratio', 'Image_to_Total_Ratio',
                           'Text_vs_Image'] + context_features
        features = data_train[feature_columns]
        avg_response_time_per_config_id = data_train.groupby('Config ID')['Avg_Response_Time'].mean().to_dict()

        features_scaled = self.scaler.fit_transform(features)
        config_ids = data_train['Config ID'].astype('category').cat.codes

        # Split data
        X_train, self.X_test, self.ids_train, self.ids_test, _, _ = train_test_split(
            features_scaled, config_ids, data_train['Avg_Response_Time'],
            test_size=0.2, random_state=42)

        # Training the model
        for i in range(0, len(X_train), self.batch_size):
            batch_end = min(i + self.batch_size, len(X_train))
            self.model.partial_fit(X_train[i:batch_end], self.ids_train[i:batch_end],
                                   classes=np.unique(config_ids))
        return avg_response_time_per_config_id

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

    def predict_and_update(self):
        predicted_rewards = []
        predicted_config_ids = []

        for i in range(len(self.X_test)):
            if np.random.rand() < self.epsilon:
                # Exploration
                pred_config_id = np.random.choice(self.ids_train.unique())
            else:
                # Exploitation
                pred_config_id = self.model.predict([self.X_test[i]])[0]

            reward = self.exponential_decay_reward(self.avg_response_time_per_config_id[pred_config_id])
            predicted_rewards.append(reward)
            predicted_config_ids.append(pred_config_id)

        # Convert rewards to sample weights for training
        reward_weights = self.rewards_to_weights(predicted_rewards)

        # Update the model
        self.model.partial_fit(self.X_test, self.ids_test, sample_weight=reward_weights)

        return predicted_config_ids

    def plan(self):

        data = pd.DataFrame([self.knowledge.monitored_data])

        # Feature engineering to create more informative features
        data['Text_to_Total_Ratio'] = data['Text Clients'] / data['Total Clients']
        data['Image_to_Total_Ratio'] = data['Image Clients'] / data['Total Clients']
        data['Text_vs_Image'] = data['Text Clients'] - data['Image Clients']
        data['Avg_Response_Time'] = data['Response Time'] / data['Counter']

        configs = pd.read_csv('../../compositions.csv')
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

        predicted_config_id = int(self.model.predict(X_test)[0])
        self.model.partial_fit(X_test, [predicted_config_id], sample_weight=[self.exponential_decay_reward(data.at[0, 'Avg_Response_Time'])])

        config_composition_row = configs[configs['ID'] == predicted_config_id]
        config_composition =  config_composition_row['Composition'].values[0]

        # Setting the configuration to plan_data for execute method
        self.knowledge.plan_data = {"id": predicted_config_id, "config": config_composition}
        self.current_config = predicted_config_id

        return True
