import csv
import matplotlib.pyplot as plt
from collections import defaultdict
import os

# Path to the CSV results files
file_paths = [
    '../results/results_epsilon_greedy.csv',
    '../results/results_adaptive_greedy.csv',
    '../results/results_linUCB.csv'
]

# Define the categories for each graph
categories = {
    "Only Text Clients": [],
    "Only Image Clients": [],
    "Equal Number of Text and Image Clients": [],
    "Text Clients More Than Image Clients": [],
    "Image Clients More Than Text Clients": []
}

# Create a defaultdict to store data for each file within each category
file_categories = defaultdict(lambda: defaultdict(list))

# Function to categorize the data
def categorize_data(row, file_path):
    text_clients = int(row['Text_Clients'])
    image_clients = int(row['Image_Clients'])

    if text_clients == 0 and image_clients != 0:
        categories["Only Image Clients"].append(row)
        file_categories[file_path]["Only Image Clients"].append(float(row['Avg_Response_Time']))
    elif image_clients == 0 and text_clients != 0:
        categories["Only Text Clients"].append(row)
        file_categories[file_path]["Only Text Clients"].append(float(row['Avg_Response_Time']))
    elif text_clients == image_clients:
        categories["Equal Number of Text and Image Clients"].append(row)
        file_categories[file_path]["Equal Number of Text and Image Clients"].append(float(row['Avg_Response_Time']))
    elif text_clients > image_clients:
        categories["Text Clients More Than Image Clients"].append(row)
        file_categories[file_path]["Text Clients More Than Image Clients"].append(float(row['Avg_Response_Time']))
    elif image_clients > text_clients:
        categories["Image Clients More Than Text Clients"].append(row)
        file_categories[file_path]["Image Clients More Than Text Clients"].append(float(row['Avg_Response_Time']))


# Read and categorize data from each file
for file_path in file_paths:
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            categorize_data(row, file_path)


# Plot line and bar charts for each category
for category, _ in categories.items():
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Line chart
    for idx, file_path in enumerate(file_paths):
        file_name = file_path.split('/')[-1].split('.')[0]  # Extract the file name without extension
        response_times = file_categories[file_path][category]
        ax1.plot(response_times, label=file_name)

    ax1.set_xlabel('Data Points')
    ax1.set_ylabel('Avg Response Time')
    ax1.set_title(f"{category} - Line Chart")
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)

    # Save the line chart in the 'graphs' folder with the category name
    output_line_chart = os.path.join('../graphs/', f"{category.replace(' ', '_')}_line_chart.png")
    plt.tight_layout()
    plt.savefig(output_line_chart)
    plt.close(fig)


    fig, ax2 = plt.subplots(figsize=(8, 5))

    # Bar chart
    x_values = range(len(file_paths))  # X-values for the bars (representing files)
    for idx, file_path in enumerate(file_paths):
        file_name = file_path.split('/')[-1].split('.')[0]  # Extract the file name without extension
        response_data = file_categories[file_path][category]
        ax2.bar([x_values[idx]], [sum(response_data) / len(response_data)], width=0.25, label=file_name)

    ax2.set_xlabel('Files')
    ax2.set_ylabel('Avg Response Time')
    ax2.set_title(f"{category} - Bar Chart")
    ax2.legend()

    # Save the bar chart in the 'graphs' folder with the category name
    output_bar_chart = os.path.join('../graphs/', f"{category.replace(' ', '_')}_bar_chart.png")
    plt.tight_layout()
    plt.savefig(output_bar_chart)
    plt.close(fig)