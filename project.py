import streamlit as st
import requests

st.set_page_config(page_title="Personalized Recipe Recommendation", layout="wide", initial_sidebar_state="collapsed")
st.title("Personalized Recipe Recommendation System")
st.write("Get recipe suggestions based on your preferences and allergies!")
st.write("This app helps solve the common dilemma of 'What to cook?' with personalized recipe suggestions that match your preferences, available ingredients, and dietary needs. It also ensures safety by taking allergies into account, making it inclusive for everyone.")

#api request
@st.cache_data
def get_recipes(query, min_calories, max_calories, diet=None, intolerances=None, includeIngredients=None):
    try:
        if intolerances:
            i = ",".join(intolerances)
        else:
            i = None
        if includeIngredients:
            ing = ",".join(includeIngredients) 
        else:
            ing = None
        
        url = "https://api.spoonacular.com/recipes/complexSearch"
        p = { 
            "apiKey": "0ddf61be837c41ba8694600f1ba818e1", 
            "query": query, 
            "minCalories": min_calories,
            "maxCalories": max_calories, 
            "diet": diet, 
            "intolerances": i,
            "includeIngredients": ing, 
            "number": 10, 
            "addRecipeInformation": True, 
            "instructionsRequired": True, 
        }
        response = requests.get(url, params=p)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error("Error fetching recipes from the API. Please try again later.")
        return {"results": []}
    
if "selected_recipe" not in st.session_state:
    st.session_state["selected_recipe"] = None
if "starred_recipes" not in st.session_state:
    st.session_state["starred_recipes"] = []

# Sidebar 
st.sidebar.header("Search Recipes")
query = st.sidebar.text_input("Enter recipe name:")
includeIngredients = st.sidebar.text_input("Enter ingredients to use:")
diet = st.sidebar.selectbox("Choose your dietary preference:", ["None", "Vegetarian", "Vegan", "Keto", "Low-Carb"])
intolerances = st.sidebar.text_area("Enter ingredients you're allergic to (comma-separated):")
calorie_range = st.sidebar.slider("Select calorie range:", min_value=50, max_value=2000, value=(50, 2000))
min_calories, max_calories = calorie_range

#parsing
if intolerances:
    parsed_intolerances = [i.strip().lower() for i in intolerances.split(",")]
else:
    parsed_intolerances = None
if query:
    parsed_query = [item.strip().lower() for item in query.split(",")]
else:
    parsed_query = None
query_string = " ".join(parsed_query) if parsed_query else ""
if includeIngredients:
    parsed_includeIngredients = [ingredient.strip().lower() for ingredient in includeIngredients.split(",")]
else:
    parsed_includeIngredients = None

# Saved recipe button
if st.sidebar.button("Saved Recipes"):
    st.title("Saved Recipes")
    if st.session_state["starred_recipes"]:
        for recipe in st.session_state["starred_recipes"]:
            st.markdown(f"⭐ **{recipe}**")
    else:
        st.write("No saved recipes yet.")
    if st.button("Back to Main"):
        st.experimental_rerun()
    st.stop()

# Get Recipes
recipes_data = get_recipes(
    query=query_string, 
    min_calories=min_calories, 
    max_calories=max_calories, 
    diet=None if diet == "None" else diet, 
    intolerances=parsed_intolerances,
    includeIngredients=parsed_includeIngredients
)

# Handle No Recipes Found
if not recipes_data.get("results"):
    st.warning("No recipes found matching your criteria. Try adjusting the filters.")
else:
    recipes = recipes_data["results"]

# Display Recipes
try:
    if not st.session_state["selected_recipe"]:
        st.markdown("## Recommended Recipes")
        # Display recipes
        for recipe in recipes:
            col1, col2 = st.columns([1, 5])
            with col1:
                st.image(recipe["image"], use_container_width=True)
            with col2:
                recipe_name = recipe["title"]
                calories = recipe.get("nutrition", {}).get("nutrients", [{}])[0].get("amount", "N/A")
                st.write(f"**{recipe_name}** - {calories} kcal")
                if st.button(f"View {recipe_name}", key=f"view_{recipe['id']}"):
                    st.session_state["selected_recipe"] = recipe
                if recipe_name in st.session_state["starred_recipes"]:
                    if st.button("⭐", key=f"unstar_{recipe['id']}"):
                        st.session_state["starred_recipes"].remove(recipe_name)
                else:
                    if st.button("☆", key=f"star_{recipe['id']}"):
                        st.session_state["starred_recipes"].append(recipe_name)
    else:
        # Show Selected Recipe Details
        selected_recipe = st.session_state["selected_recipe"]
        st.header(f"Recipe: {selected_recipe['title']}")
        st.image(selected_recipe["image"], use_container_width=True)
        # Ingredients Display Inline Without Heading
        ingredients = selected_recipe.get("extendedIngredients", [])
        if ingredients:
            st.write("### Ingredients:")
            for ingredient in ingredients:
                st.write(f"- {ingredient['original']}")
        #recipe instruction
        st.write("### Directions to Cook:")
        instructions = selected_recipe.get("analyzedInstructions", [])
        if instructions:
            for instruction_set in instructions:
                for step in instruction_set["steps"]:
                    st.write(f"**{step['number']}. {step['step']}**")
        else:
            st.write("No instructions available.")
        # Back Button
        if st.button("Back to Recipes"):
            st.session_state["selected_recipe"] = None
except Exception as e:
    st.error("An unexpected error occurred. Please try again later.")



    
