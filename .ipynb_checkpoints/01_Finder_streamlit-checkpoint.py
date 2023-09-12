# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
nutrient_df = pd.read_csv('Data/nutrient.csv')
food_df = pd.read_csv('Data/food.csv')
food_nutrient_df = pd.read_csv('Data/food_nutrient.csv')
food_category_df = pd.read_csv('Data/food_category.csv')

# Streamlit app
st.title("Food Finder Dashboard")

# Dropdown for nutrient selection
selected_nutrient = st.selectbox('Select a Nutrient:', nutrient_df['name'].unique())

# Show selected nutrient
st.write(f"Selected Nutrient: {selected_nutrient}")

# Find nutrient_id and unit for selected nutrient
nutrient_info = nutrient_df[nutrient_df['name'] == selected_nutrient].iloc[0]
nutrient_id = nutrient_info['id']
nutrient_unit = nutrient_info['unit_name']

# Debug Line 2: Show nutrient ID
st.write(f"Nutrient ID: {nutrient_id}")

# Filter food_nutrient dataframe
filtered_food_nutrient_df = food_nutrient_df[food_nutrient_df['nutrient_id'] == nutrient_id]

# Debug Line 3: Show number of rows in filtered DataFrame
st.write(f"Number of Rows in Filtered DataFrame: {len(filtered_food_nutrient_df)}")

# Merge with food_df
result_df = pd.merge(filtered_food_nutrient_df, food_df, on='fdc_id')

# Filter food_category DataFrame
specified_categories = [
    "Vegetables and Vegetable Products",
    "Legumes and Legume Products",
    "Spices and Herbs",
    "Cereal Grains and Pasta",
    "Fats and Oils"
]
filtered_food_category_df = food_category_df[food_category_df['description'].isin(specified_categories)]

# Loop through each specified category and plot
for category in specified_categories:
    st.subheader(f'Top 10 Foods in {category}')
    
    # Filter result_df by food_category_id
    category_id = filtered_food_category_df[filtered_food_category_df['description'] == category]['id'].values[0]
    category_df = result_df[result_df['food_category_id'] == category_id]
    
    # Sort and take top 10
    top_foods = category_df.sort_values('amount', ascending=False).head(10)
    
    # Modify food description
    def get_first_two_words_before_second_comma(description):
        parts = description.split(',')
        if len(parts) >= 2:
            first_two_words = ' '.join(parts[0].split()[:2]) + ', ' + ' '.join(parts[1].split()[:2])
            return first_two_words
        else:
            return description
    
    top_foods['short_description'] = top_foods['description'].apply(get_first_two_words_before_second_comma)
    top_foods['display_name'] = top_foods['short_description'] + " (" + top_foods['fdc_id'].astype(str) + ")"
    
    # Plot
    fig, ax = plt.subplots()
    ax.barh(top_foods['display_name'], top_foods['amount'])
    ax.set_xlabel(f'Amount ({nutrient_unit})')  # Display unit
    ax.set_ylabel('Food Description')
    ax.set_title(f'Top 10 Foods based on {selected_nutrient} in {category}')
    st.pyplot(fig)
