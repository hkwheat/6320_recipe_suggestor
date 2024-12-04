import pandas as pd  
import spacy  
import json  
from collections import defaultdict 
from typing import Dict, List  # for type hinting
from datetime import datetime, timedelta  # for datetime operations
import os  
import argparse  # arg parsing
import random  

# load spaCy model globally to avoid repeated loading
nlp = spacy.load("en_core_web_sm")

# constants
MAX_WEIGHT = 5.0  # maximum cap for any meal type weight
DECAY_FACTOR = 0.9  # decay factor to reduce weight by 10%
DECAY_INTERVAL_DAYS = 30  # apply decay every 30 days

class UserProfile:
    def __init__(self, user_id: str):
        self.user_id = user_id  # store the user's id
        self.preferences = {
            'liked_recipes': [],  # list of dictionaries with recipe_id and recipe_name
            'disliked_recipes': [],  # list to hold dictionaries of disliked recipe_id and recipe_name
            'dietary_restrictions': set(),  # set of dietary restrictions
            'favorite_cuisines': set(),  # set of favorite cuisines
            'meal_type_preferences': defaultdict(float)  # default dictionary for meal type preferences
        }
        self.recipe_ratings = defaultdict(float)  # store recipe ratings
        self.last_login = datetime.now().isoformat()  # store last login date
        self.total_suggestions_received = 0  # track total suggestions received
        self.total_interactions = 0  # track total user interactions
        self.last_decay_date = datetime.now().isoformat()  # track when decay was last applied

    def to_dict(self) -> Dict:
        #convert profile to dictionary for storage
        return {
            'user_id': self.user_id,  # user id
            'preferences': {
                'liked_recipes': self.preferences['liked_recipes'],  # list of liked recipes
                'disliked_recipes': self.preferences['disliked_recipes'],  # list of disliked recipes
                'dietary_restrictions': list(self.preferences['dietary_restrictions']),  # dietary restrictions
                'favorite_cuisines': list(self.preferences['favorite_cuisines']),  # favorite cuisines
                'meal_type_preferences': dict(self.preferences['meal_type_preferences'])  # meal type preferences
            },
            'recipe_ratings': dict(self.recipe_ratings),  # recipe ratings
            'last_login': self.last_login,  # last login timestamp
            'total_suggestions_received': self.total_suggestions_received,  # total suggestions
            'total_interactions': self.total_interactions,  # total interactions
            'last_decay_date': self.last_decay_date  # last decay date
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        #create user profile instance from dictionary
        profile = cls(data['user_id'])  # initialize user profile with user_id
        profile.preferences['liked_recipes'] = data['preferences']['liked_recipes']  # load liked recipes
        profile.preferences['disliked_recipes'] = data['preferences']['disliked_recipes']  # load disliked recipes
        profile.preferences['dietary_restrictions'] = set(data['preferences']['dietary_restrictions'])  # load restrictions
        profile.preferences['favorite_cuisines'] = set(data['preferences']['favorite_cuisines'])  # load cuisines
        profile.preferences['meal_type_preferences'] = defaultdict(float, data['preferences']['meal_type_preferences'])  # meal types
        profile.recipe_ratings = defaultdict(float, data['recipe_ratings'])  # recipe ratings
        profile.last_login = data.get('last_login', datetime.now().isoformat())  # load last login
        profile.total_suggestions_received = data.get('total_suggestions_received', 0)  # load suggestions count
        profile.total_interactions = data.get('total_interactions', 0)  # load interactions count
        profile.last_decay_date = data.get('last_decay_date', datetime.now().isoformat())  # load last decay date
        return profile  # return the profile object

    def apply_decay(self):
        #apply decay to weights if enough time has passed
        last_decay_date = datetime.fromisoformat(self.last_decay_date)  # parse last decay date
        current_date = datetime.now()  # get current date
        days_since_decay = (current_date - last_decay_date).days  # calculate days since last decay

        if days_since_decay >= DECAY_INTERVAL_DAYS:  # check if decay interval is met
            for meal_type in self.preferences['meal_type_preferences']:  # iterate through meal types
                self.preferences['meal_type_preferences'][meal_type] *= DECAY_FACTOR  # apply decay factor
            self.last_decay_date = current_date.isoformat()  # update last decay date

    def update_weight(self, meal_type: str):
        #update the weight for a meal type, applying cap and decay
        self.apply_decay()  # apply decay before updating
        new_weight = self.preferences['meal_type_preferences'].get(meal_type, 0) + 1.0  # increase weight
        self.preferences['meal_type_preferences'][meal_type] = min(new_weight, MAX_WEIGHT)  # apply cap

class UserManager:
    def __init__(self, users_dir: str = "users"):
        self.users_dir = users_dir  # set the directory for user profiles
        os.makedirs(users_dir, exist_ok=True)  # create directory if it doesn't exist

    def get_user_profile_path(self, username: str) -> str:
        return os.path.join(self.users_dir, f"{username.lower()}.json")  # return path to user profile file

    def load_user_profile(self, username: str) -> UserProfile:
        profile_path = self.get_user_profile_path(username)  # get profile path
        if os.path.exists(profile_path):  # check if profile exists
            with open(profile_path, 'r') as f:  # open profile file
                data = json.load(f)  # load data from json
            profile = UserProfile.from_dict(data)  # create profile from data
            profile.last_login = datetime.now().isoformat()  # update last login
            self.save_user_profile(profile)  # save updated profile
            print(f"Welcome back, {username}! Last login: {data['last_login']}")  # print welcome message
        else:
            profile = UserProfile(username)  # create new profile
            print(f"Welcome, {username}! Created new profile.")  # print creation message
            self.save_user_profile(profile)  # save new profile immediately
        return profile  # return user profile

    def save_user_profile(self, profile: UserProfile):
        profile_path = self.get_user_profile_path(profile.user_id)  # get profile path
        try:
            with open(profile_path, 'w') as f:  # open file for writing
                json.dump(profile.to_dict(), f, indent=2)  # save profile as json
            print(f"Profile saved successfully for user {profile.user_id}")  # print success message
        except Exception as e:
            print(f"Error saving profile for user {profile.user_id}: {e}")  # print error message

class RecipeSuggester:
    def __init__(self, data_dir: str, debug: bool = False):
        self.debug = debug  # enable or disable debug mode
        self.data_dir = data_dir  # set the directory for recipe data
        self.recipes_df = self.load_recipes()  # load all recipes from the specified directory
        self.user_manager = UserManager()  # initialize the user manager to handle user profiles
        self.meal_keywords = {  # define keywords for identifying meal types from user input
            'appetizer': ['appetizer', 'starter', 'snack'],
            'breakfast': ['breakfast', 'brunch', 'morning'],
            'lunch': ['lunch', 'sandwich', 'salad'],
            'dinner': ['dinner', 'supper', 'main course'],
            'dessert': ['dessert', 'sweet', 'cake', 'cookie']
        }
        self.prompts = [  # define random prompts to interact with the user
            "What kind of recipe would you like today?",
            "What are you in the mood for?",
            "Looking for something specific?",
            "What would you like to have today?"
        ]

    def load_recipes(self) -> pd.DataFrame:
        dfs = []  # list to store dataframes of recipes
        for category_file in ['appetizer.csv', 'breakfast.csv', 'dessert.csv', 'dinner.csv', 'lunch.csv']:  # iterate over all recipe categories
            file_path = os.path.join(self.data_dir, category_file)  # construct the file path for the category
            if os.path.exists(file_path):  # check if the file exists
                df = pd.read_csv(file_path)  # read the CSV file into a dataframe
                df['meal_type'] = category_file.split('.')[0]  # add a column specifying the meal type
                dfs.append(df)  # add the dataframe to the list
                if self.debug:  # if debug mode is enabled
                    print(f"Loaded recipes from: {file_path}")  # print the file path of the loaded file
        return pd.concat(dfs, ignore_index=True)  # combine all dataframes into one and return it

   
    def analyze_user_input(self, text: str) -> str:
        # determine the meal type based on user input
        doc = nlp(text.lower())  # process the input text using spaCy for NLP
        meal_scores = defaultdict(float)  # initialize a default dictionary to store scores for meal types
        for token in doc:  # iterate through each token in the processed text
            for meal_type, keywords in self.meal_keywords.items():  # check each meal type and its associated keywords
                if token.text in keywords:  # if the token matches a keyword
                    meal_scores[meal_type] += 1  # increment the score for that meal type
        if self.debug:  # if debug mode is enabled
            print(f"Meal type scores from user input '{text}':", meal_scores)  # print the scores for each meal type
        if any(meal_scores.values()):  # check if there are any non-zero scores
            return max(meal_scores.items(), key=lambda x: x[1])[0]  # return the meal type with the highest score
        return "dinner"  # default to 'dinner' if no keywords match

    def get_recipe_suggestions(self, profile: UserProfile, text: str, num_suggestions: int = 3, include_liked_probability: float = 0.2) -> List[Dict]:
        # generate recipe suggestions based on user input and profile preferences
        meal_type = self.analyze_user_input(text)  # determine the meal type from user input
        meal_recipes = self.recipes_df[self.recipes_df['meal_type'] == meal_type].copy()  # filter recipes by meal type

        # exclude disliked recipes
        disliked_recipe_ids = {r['recipe_id'] for r in profile.preferences['disliked_recipes']}  # get ids of disliked recipes
        meal_recipes = meal_recipes[~meal_recipes['RecipeId'].astype(str).isin(disliked_recipe_ids)]  # filter out disliked recipes

        # exclude liked recipes, but allow some to reappear based on the probability
        liked_recipe_ids = {r['recipe_id'] for r in profile.preferences['liked_recipes']}  # get ids of liked recipes
        meal_recipes['include_liked'] = meal_recipes['RecipeId'].astype(str).apply(  # decide whether to include liked recipes
            lambda x: (x not in liked_recipe_ids) or (random.random() < include_liked_probability)  # include liked recipes probabilistically
        )
        meal_recipes = meal_recipes[meal_recipes['include_liked']]  # filter recipes to include liked recipes based on the probability

        # scoring based on meal type preferences and ratings
        meal_recipes['score'] = meal_recipes.apply(  # calculate the score for each recipe
            lambda x: (
                profile.recipe_ratings.get(str(x['RecipeId']), 0.5) *  # base score from recipe rating
                (1 + profile.preferences['meal_type_preferences'].get(meal_type, 0))  # add weight based on meal type preferences
            ),
            axis=1
        )
        
        # multiply by the recipe's aggregate rating if available
        meal_recipes['score'] *= meal_recipes['AggregatedRating'].fillna(1)  # factor in aggregated rating

        # update interaction metrics
        profile.total_suggestions_received += num_suggestions  # increment the total suggestions received
        profile.total_interactions += 1  # increment the total interactions

        # sort and select top recipes based on score
        suggestions = meal_recipes.nlargest(num_suggestions, 'score')  # get the top 'num_suggestions' recipes

        if self.debug:  # if debug mode is enabled
            print(f"Meal type for suggestion: {meal_type}")  # print the determined meal type
            print("Top scored recipes with optional liked reintroduction:")  # print debug message
            print(meal_recipes[['Name', 'score']].head(num_suggestions))  # print the top scored recipes

        return suggestions.to_dict('records')  # return the top recipes as a list of dictionaries

    def update_user_preference(self, profile: UserProfile, recipe_id: str, recipe_name: str, liked: bool):
        # update user preferences for a recipe, including meal type preference
        if liked:
            if not any(r['recipe_id'] == recipe_id for r in profile.preferences['liked_recipes']):
                profile.preferences['liked_recipes'].append({"recipe_id": recipe_id, "recipe_name": recipe_name})

            # Retrieve recipe details using RecipeId
            recipe = self.recipes_df[self.recipes_df['RecipeId'].astype(str) == str(recipe_id)]
            if not recipe.empty:
                meal_type = recipe['meal_type'].iloc[0]  # Ensure meal_type exists

                # Update meal type preference
                profile.update_weight(meal_type)
                print(f"Updated meal type preference for '{meal_type}' to {profile.preferences['meal_type_preferences'][meal_type]}")
            else:
                print(f"Error: Recipe with ID '{recipe_id}' not found.")
        else:
            if not any(r['recipe_id'] == recipe_id for r in profile.preferences['disliked_recipes']):
                profile.preferences['disliked_recipes'].append({"recipe_id": recipe_id, "recipe_name": recipe_name})

        profile.recipe_ratings[recipe_id] += 1 if liked else 0
        self.user_manager.save_user_profile(profile)

        if self.debug:
            print(f"Updated preferences for user '{profile.user_id}': {'Liked' if liked else 'Disliked'} recipe '{recipe_id}' - {recipe_name}")
            print(f"Updated meal_type_preferences: {profile.preferences['meal_type_preferences']}")


def main():
            parser = argparse.ArgumentParser(description="Recipe Suggestion System")  # create an argument parser for the script
            parser.add_argument('--debug', action='store_true', help="Enable debug mode")  # add an optional debug mode argument
            args = parser.parse_args()  # parse the command-line arguments

            suggester = RecipeSuggester('dataset/min', debug=args.debug)  # initialize the RecipeSuggester with the dataset directory and debug mode
            username = input("Please enter your username: ").strip()  # prompt the user to enter their username
            profile = suggester.user_manager.load_user_profile(username)  # load the user's profile based on their username

            print("\nRecipe Suggestion System")  # print the system's header
            print("Type 'quit' to exit, 'stats' to see your profile stats")  # provide usage instructions to the user

            while True:  # enter an infinite loop to keep interacting with the user
                # randomly display one of the predefined prompts to the user
                command = input(f"\n{random.choice(suggester.prompts)} ").strip().lower()  # get user input and normalize to lowercase

                if command == 'quit':  # if the user types 'quit', exit the loop
                    break
                elif command == 'stats':  # if the user types 'stats', display their profile statistics
                    print(f"\nProfile Statistics for {username}:")  # display the username
                    print(f"Total suggestions received: {profile.total_suggestions_received}")  # display total suggestions received
                    print(f"Total interactions: {profile.total_interactions}")  # display total interactions
                    print(f"Liked recipes: {len(profile.preferences['liked_recipes'])}")  # display count of liked recipes
                    print(f"Meal type preferences: {dict(profile.preferences['meal_type_preferences'])}")  # display meal type preferences
                    continue  # skip to the next iteration of the loop

                # get recipe suggestions based on the user input
                suggestions = suggester.get_recipe_suggestions(profile, command)  # fetch suggestions based on the command

                if not suggestions:  # if no suggestions are found
                    print("No matching recipes found.")  # inform the user
                    continue  # skip to the next iteration of the loop

                for i, recipe in enumerate(suggestions, 1):  # iterate over the suggested recipes
                    print(f"\n{i}. {recipe['Name']}")  # display the recipe name with its index
                    print(f"   Preparation Time: {recipe.get('PrepTime', 'N/A')}")  # display the preparation time or 'N/A' if not available
                    if pd.notna(recipe.get('AggregatedRating')):  # if the aggregated rating exists
                        print(f"   Rating: {recipe['AggregatedRating']:.1f}/5.0")  # display the rating
                    if pd.notna(recipe.get('ReviewCount')):  # if the review count exists
                        print(f"   Number of Reviews: {recipe['ReviewCount']}")  # display the number of reviews

                while True:  # enter a loop to handle user feedback
                    feedback = input("\nDid you like any of these recipes? (Enter recipe number, 'n' for none, or 'more' for more options): ").strip().lower()  # prompt for feedback
                    if feedback.isdigit() and 1 <= int(feedback) <= len(suggestions):  # if feedback is a valid recipe number
                        recipe = suggestions[int(feedback) - 1]  # get the selected recipe

                        # Display recipe instructions immediately after selection
                        recipe_id = recipe['RecipeId']
                        recipe_name = recipe['Name']
                        instructions = suggester.recipes_df[suggester.recipes_df['RecipeId'].astype(str) == str(recipe_id)]['RecipeInstructions'].iloc[0]

                        print(f"\nRecipe Instructions for '{recipe_name}':")
                        print(instructions if instructions else "No instructions available.")  # Print the instructions or fallback message

                        # ask if the user liked or disliked the selected recipe
                        like_dislike = input(f"\nDid you like {recipe_name}? (yes or no): ").strip().lower()  # ask for a like/dislike response
                        liked = like_dislike == 'yes'  # determine if the response is 'yes'

                        # update the user's preference based on their feedback
                        suggester.update_user_preference(profile, recipe_id, recipe_name, liked=liked)  # update preferences

                        # thank the user for their feedback
                        if liked:  # if the user liked the recipe
                            print(f"Great! {recipe_name} has been added to your liked recipes.")  # confirm addition to liked recipes
                        else:  # if the user disliked the recipe
                            print(f"{recipe_name} has been marked as disliked.")  # confirm marking as disliked
                        break  # exit the feedback loop

                    elif feedback == 'n':  # if the user indicates they liked none of the recipes
                        print("Got it. Let's find more options for you.")  # acknowledge and move on
                        break  # exit the feedback loop
                    elif feedback == 'more':  # if the user requests more suggestions
                        print("Fetching more options...")  # indicate that more suggestions are being fetched
                        break  # exit the feedback loop
                    else:  # if the input is invalid
                        print("Please enter a valid option.")  # prompt the user to try again


                # if user requests more, continue with new suggestions in the next loop iteration
                if feedback == 'more':  # if the user asked for more options
                    continue  # skip to the next iteration
                elif feedback == 'n':  # if the user liked none of the suggestions
                    print("No more suggestions available at this time.")  # inform the user
                    break  # exit the loop

            # save the user's profile before exiting the program
            suggester.user_manager.save_user_profile(profile)  # persist the updated profile
            print(f"\nGoodbye {username}! Your profile has been saved.")  # print a farewell message

if __name__ == "__main__":
    main()  # execute the main function
