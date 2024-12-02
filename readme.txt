README - Recipe Recommendation System

Project Overview:
-----------------
This project is a personalized recipe recommendation system designed to suggest recipes based on user preferences, meal type requests, and past interactions.
The system employs NLP to interpret user input and select appropriate meal types (e.g., appetizer, breakfast, lunch, dinner, dessert). 
Over time, the system learns user preferences, adjusting meal type weights based on user feedback, applying weight decay for less-used meal types, and 
occasionally reintroducing liked recipes for a balanced experience.

Key Features:
-------------
1. **NLP-Based Meal Type Detection**: Uses spaCy to interpret user input and determine the meal type based on keywords (e.g., “dessert,” “lunch”).
2. **User-Driven Personalization**: Suggests recipes based on meal types that the user has shown interest in, with weights that dynamically update according to interactions.
3. **Weight Decay Mechanism**: Reduces meal type weights over time, ensuring preferences are balanced and remain relevant.
4. **Probability-Based Reintroduction of Liked Recipes**: Occasionally includes previously liked recipes for variety while still introducing new suggestions.

Setup Instructions:
-------------------
1. **Python Version**: Ensure you are using Python 3.7 or later.
2. **Install Dependencies**:
   - Required packages can be installed via pip:
     ```
     pip install pandas spacy
     ```
   - Download the spaCy English model:
     ```
     python -m spacy download en_core_web_sm
     ```
3. **Data Preparation**:
   - Place your recipe data files in a `dataset/min` directory. Each meal type should have its own CSV file (e.g., appetizer.csv, breakfast.csv).
   - The `users` directory will store user profiles as JSON files, allowing for profile-specific preference tracking and personalization.

Usage Instructions:
-------------------
1. **Run the Program**:
   - Start the application from the command line:
     ```
     python main.py
     ```
     run in debug mode:
     python main.py --debug 

   - You will be prompted to enter a username. If the user profile does not exist, 
      a new profile will be created.

2. **Commands**:
   - **Type 'stats'**: View profile statistics, including liked recipes, meal type preferences, and interaction metrics.
   - **Type 'quit'**: Exit the application and save your profile.

3. **Interacting with Recipe Suggestions**:
   - The system will prompt you with a message like "What kind of recipe are you in the mood for?" or similar. Enter your preferences in plain text (e.g., “something sweet,” “quick lunch”).
   - **Feedback Options**:
     - After viewing suggestions, indicate if you like any recipes by entering the recipe number, typing 'n' for none, or 'more' for additional options.
     - When you select a recipe, you will be asked if you liked or disliked it. This feedback helps the system adjust your profile.

Project Structure:
------------------
- **main.py**: Entry point of the program, handling user input, suggestions, and feedback.
- **UserProfile class**: Manages user preferences, meal type weights, weight decay, and profile persistence.
- **RecipeSuggester class**: Generates recipe suggestions based on user input, profile data, and NLP meal type analysis.
- **UserManager class**: Handles loading and saving user profiles to JSON files.
- **Data Files**: folder should be (dataset/min/csv files here)
  - **Recipe Data**: CSV files categorized by meal type (e.g., appetizer.csv).
  - **User Data**: JSON files stored in the `users` directory to maintain profile-specific preferences.

Explanation of Key Functions:
-----------------------------
1. **analyze_user_input**:
   - Parses user input with spaCy NLP to identify the most relevant meal type based on keywords.
   - This function prioritizes specific requests (e.g., “dessert”) over generalized preferences, ensuring user intent is respected.

2. **get_recipe_suggestions**:
   - Uses user preferences and feedback history to suggest recipes, scoring them based on meal type weights and ratings.
   - Occasionally reintroduces liked recipes based on a set probability (`include_liked_probability`) to balance new and familiar recommendations.

3. **apply_decay**:
   - Reduces weights for meal types that haven’t been selected in a while, keeping preferences current and dynamic.
   - This function is triggered periodically, ensuring the profile reflects recent interactions.

4. **update_user_preference**:
   - Updates the user profile when a recipe is liked or disliked, affecting meal type weights and stored ratings.

---------------
Usage:

System-Specific Adjustments:

include_liked_probability can be adjusted to control how often liked recipes reappear in suggestions.
MAX_WEIGHT and DECAY_FACTOR are configurable constants that govern priority caps and decay rates for meal-type weights, allowing for a customizable user experience.

Additional Notes:
-----------------
- **Weight Decay Mechanism**: 
   - Meal type preferences gradually decay over time if they’re not used, ensuring that long-unused preferences don’t over-influence suggestions.
   - For example, if a user hasn’t interacted with a certain meal type(dinner for example) in a while, the weight of that type will gradually decrease, promoting other types the user might engage with more frequently.
   - This keeps the recommendation system dynamic and responsive to the user’s evolving tastes.

- **Liked Recipe Reintroduction**:
   - The system keeps track of recipes that the user has explicitly liked by storing these recipes in the user profile.
   - **Selective Reintroduction**: By default, liked recipes are excluded from suggestions to provide fresh recommendations. However, the system periodically reintroduces liked recipes based on a set probability (`include_liked_probability`).
   - **How It Works**:
     - When generating recipe suggestions, the system randomly determines whether to include each liked recipe based on the probability. For example, with a probability set at 20%, there’s a one-in-five chance for a previously liked recipe to appear in a suggestion set.
     - This feature allows users to occasionally see their favorites, offering a mix of familiar and new recommendations.
     - Liked recipes are still ranked according to their scores (based on factors such as ratings and meal type weights), ensuring they are suggested at appropriate times and don’t overshadow fresh options.
   - **Customizability**: The probability of liked recipe reintroduction can be adjusted by changing the `include_liked_probability` parameter in the `get_recipe_suggestions` function. A higher probability will reintroduce favorites more often, while a lower probability will prioritize fresh suggestions.

Overall, the **Liked Recipe Reintroduction** feature aims to balance novelty and familiarity, 
offering a varied user experience that includes both favorite and new recipes over time.

-------------------

