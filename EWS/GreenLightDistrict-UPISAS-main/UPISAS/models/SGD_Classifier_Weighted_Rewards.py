import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

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

# Import and prepare the data
data_train = pd.read_csv('../../train_data_with_comp.csv')
data_train.fillna(0, inplace=True)  # Handling missing values

# Feature engineering to create more informative features
data_train['Text_to_Total_Ratio'] = data_train['Text Clients'] / data_train['Total Clients']
data_train['Image_to_Total_Ratio'] = data_train['Image Clients'] / data_train['Total Clients']
data_train['Text_vs_Image'] = data_train['Text Clients'] - data_train['Image Clients']
data_train['Avg_Response_Time'] = data_train['Response Time'] / data_train['Counter']

# Calculate the average response time for each configuration ID beforehand
avg_response_time_per_config_id = data_train.groupby('Config ID')['Avg_Response_Time'].mean()

# Adding the new context features to the feature set
context_features = ['Request', 'Http', 'Compression', 'Cache']
feature_columns = ['Total Clients', 'Text Clients', 'Image Clients', 'Text_to_Total_Ratio', 'Image_to_Total_Ratio', 'Text_vs_Image'] + context_features
features = data_train[feature_columns]
config_ids = data_train['Config ID'].astype('category').cat.codes

# Standardize the features to have a mean of 0 and a standard deviation of 1
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Splitting the data into training (80%) and testing (20%) sets
X_train, X_test, ids_train, ids_test, avg_y_train, avg_y_test = train_test_split(
    features_scaled, config_ids, data_train['Avg_Response_Time'], test_size=0.2, random_state=42
)

# Initialize the SGD Classifier
model = SGDClassifier(max_iter=1000, tol=1e-3)

# Training the model in batches for efficiency
batch_size = 50
for i in range(0, len(X_train), batch_size):
    batch_end = min(i + batch_size, len(X_train))
    model.partial_fit(X_train[i:batch_end], ids_train[i:batch_end], classes=np.unique(config_ids))

# Implementing the epsilon-greedy strategy
epsilon = 0.1
predicted_rewards = []
predicted_config_ids = []

for i in range(len(X_test)):
    if np.random.rand() < epsilon:
        # Exploration: Randomly choose a Config ID
        pred_config_id = np.random.choice(data_train['Config ID'])
    else:
        # Exploitation: Choose the best Config ID based on the model's prediction
        pred_config_id = model.predict([X_test[i]])[0]

    # Retrieve the average response time for the predicted configuration ID
    avg_response_time = avg_response_time_per_config_id.get(pred_config_id, 0)
    
    # Calculate the reward for the chosen configuration using the average response time
    reward = exponential_decay_reward(avg_response_time)

    predicted_rewards.append(reward)
    predicted_config_ids.append(pred_config_id)

# Convert rewards to sample weights for training
reward_weights = np.array(predicted_rewards)
reward_weights = (reward_weights - reward_weights.min()) / (reward_weights.max() - reward_weights.min())
reward_weights += 0.1  # To ensure that no sample has a zero weight

# Update the model with the feedback loop, using rewards as sample weights
model.partial_fit(X_test, ids_test, sample_weight=reward_weights)
