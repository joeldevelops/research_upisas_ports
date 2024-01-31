from UPISAS.strategy import Strategy

import pandas as pd
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler


class SGDStrategy(Strategy):

    # Set a random seed for reproducibility of results
    np.random.seed(42)

    # Define a function to calculate rewards based on average response time
    def exponential_decay_reward(avg_response_time):
        scale_factor = 0.0001
        if avg_response_time > 0:
            reward = np.exp(-avg_response_time * scale_factor)
            return reward
        else:
            return 0

    def train_model(self):
        self.current_config = 0

        # Import and prepare the data
        data = pd.read_csv('./data/train_data_with_comp.csv')
        data.fillna(0, inplace=True)  # Handling missing values

        # Feature engineering to create more informative features
        data['Text_to_Total_Ratio'] = data['Text Clients'] / data['Total Clients']
        data['Image_to_Total_Ratio'] = data['Image Clients'] / data['Total Clients']
        data['Text_vs_Image'] = data['Text Clients'] - data['Image Clients']
        data['Avg_Response_Time'] = np.log(data['Response Time'] / data['Counter'])

        # Adding the new context features to the feature set
        context_features = ['Request', 'Http', 'Compression', 'Cache']
        feature_columns = ['Total Clients', 'Text Clients', 'Image Clients', 'Text_to_Total_Ratio', 'Image_to_Total_Ratio', 'Text_vs_Image', 'Config ID',] + context_features
        features = data[feature_columns]
        avg_y= data['Avg_Response_Time']


        # Initialize the SGDRegressor model
        self.model = SGDRegressor(max_iter=10000)

        # Standardize the features to have a mean of 0 and a standard deviation of 1
        self.scaler = StandardScaler()
        features = self.scaler.fit_transform(features, avg_y)

        # Training the model in batches for efficiency
        batch_size = 50
        for i in range(0, len(features), batch_size):
            batch_end = min(i + batch_size, len(features))
            self.model.partial_fit(features[i:batch_end], avg_y[i:batch_end])

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
        data['Avg_Response_Time'] = np.log(data['Response Time'] / data['Counter'])

        #read compositions file for config id and context features
        configs = pd.read_csv('./data/compositions.csv')

        # Preparing the X_test data to predict actions using the trained model
        column_names = ['Total Clients', 'Text Clients', 'Image Clients', 'Text_to_Total_Ratio', 'Image_to_Total_Ratio', 'Text_vs_Image', 'Config ID', 'Request', 'Http', 'Compression', 'Cache']
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

        X_test = self.scaler.transform(X_test)

        avg_response_time = np.array(0)
        avg_response_time = np.exp(self.model.predict(X_test))

        print(avg_response_time)

        min_index = int(np.argmin(avg_response_time))
        min_value = avg_response_time[min_index]

        print(f"Min value: {min_value}")
        print(f"Min index: {min_index}")

        self.model.partial_fit(X_test[[self.current_config]], [data.at[0,'Avg_Response_Time']])

        config_composition_row = configs[configs['ID'] == min_index]
        config_composition =  config_composition_row['Composition'].values[0]

        # Setting the configuration to plan_data for execute method
        self.knowledge.plan_data = { "id" : min_index,
                    "config": config_composition }

        self.current_config = min_index

        return True
