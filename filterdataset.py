import os
import pandas as pd
#download original dataset from link and put in same dir as script
#original dataset- https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews

def filter_and_save_data(df, keywords_list, meal_type, output_dir, limit=None):
    # create regex pattern from keywords list
    meal_type_keywords = '|'.join(keywords_list)
    
     # filter recipes based on keywords in RecipeCategory and Keywords columns from dataset
    filtered_df = df[
        df['RecipeCategory'].str.contains(meal_type_keywords, case=False, na=False) | 
        df['Keywords'].str.contains(meal_type_keywords, case=False, na=False)
    ]
    
    print(f"Filtered {meal_type.capitalize()}: {filtered_df.shape[0]} records found.")  # Debugging line
    
     # If filtered_df not empty then save it
    if not filtered_df.empty:
        if limit:
            filtered_df = filtered_df.head(limit)
        file_path = os.path.join(output_dir, f"{meal_type.lower()}.csv")
        filtered_df.to_csv(file_path, index=False)
        print(f"{meal_type.capitalize()} dataset saved to {file_path}")
    else:
        print(f"No records found for {meal_type.capitalize()}. Skipping.")


def combine_min_files(min_dir, output_file):
    # get all csvs
    csv_files = [os.path.join(min_dir, f) for f in os.listdir(min_dir) if f.endswith('.csv')]
    # combine into dataframe
    combined_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    combine_dir = os.path.join(min_dir, 'combine') #create dir if not exist
    os.makedirs(combine_dir, exist_ok=True)
    #save combine version
    combined_file_path = os.path.join(combine_dir, 'combined_recipes.csv')
    combined_df.to_csv(combined_file_path, index=False)
    print(f"Combined CSV saved to {combined_file_path}")


def main():
    file_path = 'recipes.csv'  
    df = pd.read_csv(file_path)
    
    # user choice for dataset generation
    print("Choose dataset generation option:")
    print("1. Minimal version (user-defined record limit per meal type)")
    print("2. Full version (all records per meal type)")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        output_dir = 'dataset/min'
        limit = int(input("Enter the number of records to include for each meal type: "))
    elif choice == '2':
        output_dir = 'dataset/full'
        limit = None
    else:
        print("Invalid choice. Exiting.")
        return
    # create output directory 
    os.makedirs(output_dir, exist_ok=True)
    # define categories and associated keywords can add more??
    categories = {
        'breakfast': ['breakfast', 'brunch', 'morning'],
        'lunch': ['lunch', 'sandwich', 'salad', 'soup'],
        'dinner': ['dinner', 'supper', 'main course', 'entree', 'meal', 'dish'],
        'appetizer': ['appetizer', 'starter', 'hors d\'oeuvre', 'snack'],
        'dessert': ['dessert', 'sweet', 'cake', 'pie', 'cookie', 'pastry']
    }

    # filter data for each meal type and save
    for meal_type, keywords in categories.items():
        filter_and_save_data(df, keywords, meal_type, output_dir, limit)

    # ask user if wants to combine all min/ csv files into one medium dataset.
    if choice == '1':
        combine_choice = input("Do you want to combine all CSV files in 'min/' into one? (yes or no): ").lower()
        if combine_choice == 'yes':
            combine_min_files(output_dir, 'combined_recipes.csv')

if __name__ == "__main__":
    main()
