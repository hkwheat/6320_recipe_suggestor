import os
#download original dataset from link and put in same dir as script
import pandas as pd
#original dataset- https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews
def filter_and_save_data(df, keywords_list, meal_type, output_dir, limit=None):
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


def main():
    file_path = 'recipes.csv'  # load original large csv 500 mb
    df = pd.read_csv(file_path)
    
    # no 1 for min version with custom number of recipe each csv ,no 2 for full
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
    #create dataset/min or /full we be using min mostly
    os.makedirs(output_dir, exist_ok=True)

    # categories and associated keywords
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

if __name__ == "__main__":
    main()
