import os
import pandas as pd

csv_files = {
    'Breakfast': 'breakfast.csv',
    'Lunch': 'lunch.csv',
    'Dinner': 'dinner.csv',
    'Appetizer': 'appetizer.csv',
    'Dessert': 'dessert.csv'
}

# dataset/min directory
min_dir = 'dataset/min'

# load each file and print a success message
for category, filename in csv_files.items():
    file_path = os.path.join(min_dir, filename)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        print(f"{category} file '{filename}' loaded successfully.")
    else:
        print(f"{category} file '{filename}' not found.")
