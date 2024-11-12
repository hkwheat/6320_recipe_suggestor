import pandas as pd
import spacy
import random
from collections import defaultdict
from typing import List, Dict
import os
# load spaCy model globally
nlp = spacy.load("en_core_web_sm")
#---
#class RecieSuggester

class RecipeSuggester:
    #def __init__


    #def load_recipes


    #def analyze_user_input


    #def get_recipe_suggestions



def main():
    suggester = RecipeSuggester('dataset/min', debug=True)
    print("\nWelcome to the Recipe Suggestion System ")
    print("Type 'quit' or 'exit' to leave the system.\n")
    
    while True:
        # get user input with a randomized prompt
        command = input(f"{random.choice(suggester.prompts)} ").strip().lower()
        
        # exit condition
        if command in ['quit', 'exit']:
            print("Thank you for using the Recipe Suggestion System!")
            break
        
        # determine meal type from user input
        meal_type = suggester.analyze_user_input(command)
        
        # get suggestions based on meal type
        suggestions = suggester.get_recipe_suggestions(meal_type)
        
        # display suggestions from dataset rating reviews etc
        print("\nSuggested Recipes:")
        for i, recipe in enumerate(suggestions, 1):
            print(f"\n{i}. {recipe['Name']}")
            print(f"   Preparation Time: {recipe.get('PrepTime', 'Unknown')}")
            if pd.notna(recipe.get('AggregatedRating')):
                print(f"   Rating: {recipe['AggregatedRating']:.1f}/5.0")
            if pd.notna(recipe.get('ReviewCount')):
                print(f"   Number of Reviews: {recipe['ReviewCount']}")

        
        print("\nEnter another preference or type 'quit' to exit.")

if __name__ == "__main__":
    main()
