import os
import json
from datetime import datetime, timedelta
from main import RecipeSuggester, UserManager, UserProfile, MAX_WEIGHT #from filename 

# Paths to data and user directories
data_dir = 'dataset/min'
users_dir = 'users'

# Initialize user manager and recipe suggester
user_manager = UserManager(users_dir)
suggester = RecipeSuggester(data_dir, debug=True)

# Test username
username = "tony"

# Load or create the user profile
profile = user_manager.load_user_profile(username)


def print_separator():
    print("\n" + "-" * 50 + "\n")


def test_like_dislike_recipes():
    """Test liking and disliking recipes, checking preferences updates and weight adjustments."""
    print("\n--- Test: Liking and Disliking Recipes ---")

    # Sample recipes to like and dislike
    like_recipes = [
        {"recipe_id": "3858", "recipe_name": "Chicken Pot Pie Lasagna"},
        {"recipe_id": "1119", "recipe_name": "Spaghetti Pie"},
    ]
    dislike_recipe = {"recipe_id": "67", "recipe_name": "Creamed Spinach"}

    # Like recipes and check preferences update
    for recipe in like_recipes:
        suggester.update_user_preference(profile, recipe["recipe_id"], recipe["recipe_name"], liked=True)
        reloaded_profile = user_manager.load_user_profile(profile.user_id)
        liked_ids = [r["recipe_id"] for r in reloaded_profile.preferences["liked_recipes"]]
        assert recipe["recipe_id"] in liked_ids, f"Recipe {recipe['recipe_name']} was not added to liked recipes."

    # Dislike a recipe and check it is added to disliked_recipes
    suggester.update_user_preference(profile, dislike_recipe["recipe_id"], dislike_recipe["recipe_name"], liked=False)
    reloaded_profile = user_manager.load_user_profile(profile.user_id)
    disliked_ids = [r["recipe_id"] for r in reloaded_profile.preferences["disliked_recipes"]]
    assert dislike_recipe["recipe_id"] in disliked_ids, f"Recipe {dislike_recipe['recipe_name']} was not added to disliked recipes."

    print("Liking and disliking recipes test passed.")
    print_separator()


def test_weight_cap_and_decay():
    """Test weight capping and decay mechanism."""
    print("\n--- Test: Weight Cap and Decay ---")

    # Simulate liking the same type to reach max weight
    for _ in range(10):  # Repeat to attempt to exceed MAX_WEIGHT
        profile.update_weight("dinner")
    user_manager.save_user_profile(profile)

    # Reload and verify weight cap
    reloaded_profile = user_manager.load_user_profile(profile.user_id)
    assert reloaded_profile.preferences["meal_type_preferences"]["dinner"] <= MAX_WEIGHT, "Weight cap not enforced correctly."

    # Force a decay and check if weights are reduced correctly
    reloaded_profile.last_decay_date = (datetime.now() - timedelta(days=31)).isoformat()
    reloaded_profile.apply_decay()
    user_manager.save_user_profile(reloaded_profile)

    decayed_profile = user_manager.load_user_profile(profile.user_id)
    assert decayed_profile.preferences["meal_type_preferences"]["dinner"] < MAX_WEIGHT, "Weight decay did not apply correctly."

    print("Weight capping and decay test passed.")
    print_separator()


def test_get_recipe_suggestions():
    """Test recipe suggestions, excluding disliked recipes and selectively including liked recipes."""
    print("\n--- Test: Recipe Suggestions ---")

    # Define test input
    input_text = "I'm looking for a light dessert."

    # Get suggestions and verify
    suggestions = suggester.get_recipe_suggestions(profile, input_text, num_suggestions=3, include_liked_probability=0.3)
    suggestion_ids = [s["RecipeId"] for s in suggestions]

    # Ensure disliked recipes are excluded
    disliked_ids = [r["recipe_id"] for r in profile.preferences["disliked_recipes"]]
    assert all(sid not in disliked_ids for sid in suggestion_ids), "Disliked recipes should be excluded from suggestions."

    # Check if liked recipes appear occasionally based on probability
    liked_ids = [r["recipe_id"] for r in profile.preferences["liked_recipes"]]
    liked_appeared = any(sid in liked_ids for sid in suggestion_ids)
    if liked_appeared:
        print("Liked recipes appeared as expected based on the probability setting.")

    print("Recipe suggestions test passed.")
    print_separator()


def test_nlp_analysis():
    """Test NLP-based meal type analysis with varied user inputs."""
    print("\n--- Test: NLP Analysis ---")

    # Test different input phrases for meal type recognition
    test_inputs = [
        "Something sweet",
        "Quick morning meal",
        "Dinner options",
        "Healthy lunch",
    ]

    for input_text in test_inputs:
        meal_type = suggester.analyze_user_input(input_text)
        assert meal_type in suggester.meal_keywords, f"Input '{input_text}' was not recognized as a valid meal type."

    print("NLP analysis test passed.")
    print_separator()


def test_statistics_tracking():
    print("\n--- Test: Statistics Tracking ---")
    
    # Load profile and record initial values
    profile = user_manager.load_user_profile(username)
    initial_suggestions = profile.total_suggestions_received
    initial_interactions = profile.total_interactions

    # Perform a suggestion operation
    suggestions = suggester.get_recipe_suggestions(profile, "any dessert", num_suggestions=3)
    user_manager.save_user_profile(profile)  # Ensure the updates persist
    
    # Reload profile and validate statistics
    updated_profile = user_manager.load_user_profile(username)
    print(f"Updated suggestions received: {updated_profile.total_suggestions_received}")
    print(f"Updated interactions count: {updated_profile.total_interactions}")

    # Check that suggestions and interactions have been incremented correctly
    assert updated_profile.total_suggestions_received == initial_suggestions + 3, "Total suggestions received did not update correctly."
    assert updated_profile.total_interactions == initial_interactions + 1, "Total interactions did not update correctly."

    print("Statistics tracking test passed.")
    print("\n--------------------------------------------------\n")



def run_all_tests():
    """Run all test functions for comprehensive testing."""
    test_like_dislike_recipes()
    test_weight_cap_and_decay()
    test_get_recipe_suggestions()
    test_nlp_analysis()
    test_statistics_tracking()


# Run all tests
run_all_tests()

# Optional cleanup: Reset test user profile by deleting the JSON file
# os.remove(os.path.join(users_dir, f"{username}.json"))
