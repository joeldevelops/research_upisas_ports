from UPISAS.strategy import Strategy
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class RandomForestStrategy(Strategy):

     np.random.seed(42)
     def calculate_reward(self, avg_response_time):
      # Define a scale factor for the reward calculation
      scale_factor = 0.0001
      # Calculate the reward based on average response time
      reward = np.exp(-avg_response_time * scale_factor)
      return reward


     def train_model(self):
          data = pd.read_csv('./data/train_data_with_comp.csv')
          data.fillna(0, inplace=True)

          data['Text_to_Total_Ratio'] = data['Text Clients'] / data['Total Clients']
          data['Image_to_Total_Ratio'] = data['Image Clients'] / data['Total Clients']
          data['Text_vs_Image'] = data['Text Clients'] - data['Image Clients']
          data['Avg_Response_Time'] = data['Response Time'] / data['Counter']

          context_features = ['Request', 'Http', 'Compression', 'Cache']
          feature_columns = ['Total Clients', 'Text Clients', 'Image Clients',
                              'Text_to_Total_Ratio', 'Image_to_Total_Ratio',
                              'Text_vs_Image', 'Config ID',] + context_features
          features = data[feature_columns]
          avg_y = data['Avg_Response_Time']

          self.scaler = StandardScaler()
          features_scaled = self.scaler.fit_transform(features)

          self.model = RandomForestRegressor(n_estimators=100, random_state=42)
          self.model.fit(features_scaled, avg_y)

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
          configs = pd.read_csv('./data/compositions.csv')
          data = pd.DataFrame([self.knowledge.monitored_data])

          data['Text_to_Total_Ratio'] = data['Text Clients'] / data['Total Clients']
          data['Image_to_Total_Ratio'] = data['Image Clients'] / data['Total Clients']
          data['Text_vs_Image'] = data['Text Clients'] - data['Image Clients']

          column_names = ['Total Clients', 'Text Clients', 'Image Clients',
                         'Text_to_Total_Ratio', 'Image_to_Total_Ratio',
                         'Text_vs_Image', 'Config ID', 'Request', 'Http',
                         'Compression', 'Cache']
          X_test = pd.DataFrame(np.zeros((len(configs), len(column_names))), columns=column_names)

          for i in range(len(configs)):
               X_test.at[i,'Total Clients'] = data.at[0,'Total Clients']
               X_test.at[i,'Text Clients'] = data.at[0,'Text Clients']
               X_test.at[i,'Image Clients'] = data.at[0,'Image Clients']
               X_test.at[i,'Text_to_Total_Ratio'] = data.at[0,'Text_to_Total_Ratio']
               X_test.at[i,'Image_to_Total_Ratio'] = data.at[0,'Image_to_Total_Ratio']
               X_test.at[i,'Text_vs_Image'] = data.at[0,'Text_vs_Image']
               X_test.at[i,'Config ID'] = configs.loc[i, 'ID']
               X_test.at[i,'Request'] = configs.loc[i, 'Request']
               X_test.at[i,'Http'] = configs.loc[i, 'Http']
               X_test.at[i,'Compression'] = configs.loc[i, 'Compression']
               X_test.at[i,'Cache'] = configs.loc[i, 'Cache']

          X_test_scaled = self.scaler.transform(X_test)
          avg_response_time = self.model.predict(X_test_scaled)

          # Calculate rewards for each configuration
          rewards = np.array([self.calculate_reward(time) for time in avg_response_time])

          # Find the index of the configuration with the highest reward
          max_reward_index = np.argmax(rewards)
          max_reward_value = rewards[max_reward_index]

          print(f"Max reward value: {max_reward_value}")
          print(f"Selected config index: {max_reward_index}")

          # Select the configuration with the highest reward
          selected_config_id = configs.loc[max_reward_index, 'ID']
          config_composition = configs.loc[configs['ID'] == selected_config_id, 'Composition'].values[0]

          # Store the selected configuration in the knowledge base
          self.knowledge.plan_data = {"id": selected_config_id, "config": config_composition}
          self.current_config = selected_config_id

          return True
