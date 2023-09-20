import streamlit as st
import pandas as pd
import ast

# Load the data
food_nutrient_df = pd.read_csv('Data/food_nutrient.csv')
food_df = pd.read_csv('Data/food.csv')
nutrient_df = pd.read_csv('Data/nutrient.csv')

# Streamlit UI
st.title("Nutrient Analysis Dashboard")

instruction_text = "Enter recipe as dictionaries:"
example_text = '''
    {"Food": "Blueberries", "fdc_id": 173950, "gram": 100},
    {"Food": "Broccoli", "fdc_id": 170379, "gram": 100}
'''

combined_text = f"{instruction_text}\n{example_text}"
food_list_input = st.text_area(combined_text, '')

try:
    # Convert the input to a list of dictionaries
    food_list = ast.literal_eval('[' + food_list_input + ']')
except:
    st.warning("Invalid input. Please enter a valid dictionary.")
    food_list = []

# Function#1.1 data aggregation
def calculate_aggregated_nutrients(food_list):
    nutrient_data_list = []
    for food_item in food_list:
        fdc_id = food_item.get('fdc_id')
        gram = food_item.get('gram')

        # Error handling if fdc_id or gram is None
        if fdc_id is None or gram is None:
            continue

        nutrient_info = food_nutrient_df[food_nutrient_df['fdc_id'] == fdc_id].copy()
        nutrient_info['amount_for_given_gram'] = (nutrient_info['amount'] * gram) / 100
        nutrient_data_list.append(nutrient_info)
    return pd.concat(nutrient_data_list, ignore_index=True)

# Function#1.2 top 10 nutrient
def calculate_significant_nutrient(food_list):
    # Define the list of excluded nutrient IDs
    excluded_nutrient_id = [1008, 1062, 1051]

    # Get aggregated nutrients
    nutrient_data_list = []
    for food_item in food_list:
        fdc_id = food_item.get('fdc_id')
        gram = food_item.get('gram')

        if fdc_id is None or gram is None:
            continue

        nutrient_info = food_nutrient_df[food_nutrient_df['fdc_id'] == fdc_id].copy()
        nutrient_info['amount_for_given_gram'] = (nutrient_info['amount'] * gram) / 100
        nutrient_data_list.append(nutrient_info)

    aggregated_nutrients = pd.concat(nutrient_data_list, ignore_index=True)

    # Filter out excluded nutrient IDs
    aggregated_nutrients = aggregated_nutrients[
    ~aggregated_nutrients['nutrient_id'].isin(excluded_nutrient_id)]

    
    # Get the top nutrients
    top_nutrients = aggregated_nutrients.groupby('nutrient_id')['amount_for_given_gram'] \
                                    .sum() \
                                    .reset_index() \
                                    .nlargest(10, 'amount_for_given_gram')
    top_nutrients = top_nutrients[~top_nutrients['nutrient_id'].isin(excluded_nutrient_id)]

    
    # Initialize results DataFrame
    results = pd.DataFrame(columns=['Nutrient', 'Unit', 'Sum'])

    for food_item in food_list:
        fdc_id = food_item.get('fdc_id')
        gram = food_item.get('gram')

        if fdc_id is None or gram is None:
            continue

        food_description = food_df[food_df['fdc_id'] == fdc_id]['description'].iloc[0]
        brief_food_name = food_description.split(',', 2)[0]

        food_nutrients = food_nutrient_df[food_nutrient_df['fdc_id'] == fdc_id].copy()
        food_nutrients['amount_for_given_gram'] = \
        (food_nutrients['amount'] * gram) / 100

        food_nutrients = food_nutrients[
        food_nutrients['nutrient_id'].isin(top_nutrients['nutrient_id'])]

        food_nutrients = food_nutrients.merge(
        nutrient_df, left_on='nutrient_id', right_on='id', how='left')

        food_nutrients = food_nutrients.groupby(
        ['name', 'unit_name']
        )['amount_for_given_gram'].sum().reset_index()

        food_nutrients.rename(
        columns={'name': 'Nutrient', 'unit_name': 'Unit', 'amount_for_given_gram': brief_food_name},
        inplace=True)

        if results.empty:
            results = food_nutrients
        else:
            results = pd.merge(
            results, food_nutrients, on=['Nutrient', 'Unit'], how='outer')

    # Calculate the sum for each nutrient
    results['Sum'] = results.drop(['Nutrient', 'Unit'], axis=1).sum(axis=1)

    # Round the numbers to the nearest whole number and fill NaNs with 0
    results.iloc[:, 2:] = results.iloc[:, 2:].fillna(0).round(0).astype(int)

    # Reorder the columns
    column_order = ['Nutrient', 'Unit', 'Sum'] + \
               [col for col in results.columns if col not in ['Nutrient', 'Unit', 'Sum']]

    results = results[column_order]
    results = results.sort_values(by='Nutrient')
    
    return results

# Function1.3 Anti-nutrient
Anti_Nutrient = [
  {"Nutrient": "Phytic Acid", "Alt. name": "Inositol hexaphosphate, IP6, phytate", "nutrient_id": 1042},
  {"Nutrient": "Oxalates", "Alt. name": "Ethanedioic acid, oxalic acid", "nutrient_id": 1041},
  {"Nutrient": "Salicylic acid", "Alt. name": "None", "nutrient_id": 1045}
]

def calculate_anti_nutrient(aggregated_nutrients, anti_nutrient_list):
    anti_nutrientdata = {}
    for item in anti_nutrient_list:
        nutrient_id = item['nutrient_id']
        nutrient_info = nutrient_df[nutrient_df['id'] == nutrient_id].iloc[0]
        nutrient_name = nutrient_df[nutrient_df['id'] == nutrient_id]['name'].iloc[0] 
        unit_name = nutrient_info['unit_name'] 
        amount = round(aggregated_nutrients[aggregated_nutrients['nutrient_id'] 
                                            == nutrient_id]['amount_for_given_gram'].sum(), 2)
        anti_nutrientdata[nutrient_name] = [amount] 
        col_name = f"{nutrient_name} ({unit_name})" 
        
    return pd.DataFrame(anti_nutrientdata)

# Function#1.4 Recipe Snapshot
def calculate_summary(food_list, aggregated_nutrients):
    total_weight = round(sum([item['gram'] for item in food_list]), 1)
    
    water_g = round(aggregated_nutrients[
        aggregated_nutrients['nutrient_id'] == 1051
    ]['amount_for_given_gram'].sum(), 1)
    
    energy_Kcal = round(aggregated_nutrients[
        aggregated_nutrients['nutrient_id'] == 1008
    ]['amount_for_given_gram'].sum(), 1)
    
    # Calculate the percentage of water
    if total_weight > 0:
        water_percent = round((water_g / total_weight) * 100, 1)
    else:
        water_percent = 0.0
    
    summary_data = {
        'Total Weight (g)': [total_weight],
        'Water (%)': [water_percent],
        'Energy (Kcal)': [energy_Kcal]
    }

    return pd.DataFrame(summary_data)

# Function#1.5 Macronutrient Outlook
def calculate_macronutrient(aggregated_nutrients):
    protein_g = round(aggregated_nutrients[
        aggregated_nutrients['nutrient_id'] == 1003
    ]['amount_for_given_gram'].sum(), 1)
    
    fat_g = round(aggregated_nutrients[
        aggregated_nutrients['nutrient_id'] == 1004
    ]['amount_for_given_gram'].sum(), 1)
    
    carb_g = round(aggregated_nutrients[
        aggregated_nutrients['nutrient_id'] == 1005
    ]['amount_for_given_gram'].sum(), 1)
    
    macronutrient_data = {
        'Protein (g)': [protein_g],
        'Fat (g)': [fat_g],
        'Carbohydrate (g)': [carb_g]
    }

    return pd.DataFrame(macronutrient_data)

# Confirm input ingredient
food_summary_list = []
for food_item in food_list:
    fdc_id = food_item.get('fdc_id')
    gram = food_item.get('gram')

    if fdc_id is None or gram is None:
        continue

    food_description = food_df[food_df['fdc_id'] == fdc_id]['description'].iloc[0]
    brief_food_name = ', '.join(food_description.split(',', 2)[:2])  
    brief_food_name = brief_food_name.replace(',', '')
    food_summary_list.append({'Food': brief_food_name, 'Grams': gram})

food_summary_df = pd.DataFrame(food_summary_list)
food_summary_df = food_summary_df.sort_values(by='Grams', ascending=False)
food_summary_str_list = food_summary_df.apply(lambda row: f"{row['Food']} ({row['Grams']}g)", axis=1)
food_summary_str = ', '.join(food_summary_str_list)
st.write(f"Recipe Ingredient: {food_summary_str}")


# Display the top 10 nutrients
if food_list:

    aggregated_nutrients = calculate_aggregated_nutrients(food_list)
    summary_df = calculate_summary(food_list, aggregated_nutrients)
    macronutrient_df = calculate_macronutrient(aggregated_nutrients)  # <-- Added this line
    anti_nutrient_df = calculate_anti_nutrient(aggregated_nutrients, Anti_Nutrient)
    
    # Convert all DataFrames to HTML and apply center alignment to headers
    summary_df_html = summary_df.to_html(index=False).replace(
                                '<th>', '<th style="text-align: center;">')
    macronutrient_df_html = macronutrient_df.to_html(index=False).replace(
                                '<th>', '<th style="text-align: center;">')  
    anti_nutrient_df_html = anti_nutrient_df.to_html(index=False).replace(
                                '<th>', '<th style="text-align: center;">')
    
    top_10_nutrients_df = calculate_significant_nutrient(food_list)
    top_10_simplified_df = top_10_nutrients_df[['Nutrient', 'Unit', 'Sum']].copy()
    top_10_simplified_html = top_10_simplified_df.to_html(index=False)
    top_10_simplified_html = top_10_simplified_html.replace('<th>', '<th style="text-align: center;">')

    # Display the tables side-by-side with brief descriptions
    st.write(f"""
    <table style="width:100%; border:0;">
        <tr>
            <td style="vertical-align:top; width:50%; border:0;">
                <h3>Top 10 Nutrients</h3>
                {top_10_simplified_html}
            </td>
            <td style="vertical-align:top; width:50%; border:0;">
                <h3 style="font-size: smaller;">Recipe Snapshot</h3>
                <div style="font-size: smaller;">{summary_df_html}</div>
                <br>
                <h3 style="font-size: smaller;">Macronutrient Outlook</h3>
                <div style="font-size: smaller;">{macronutrient_df_html}</div>
                <br>
                <h3 style="font-size: smaller;">Anti-Nutrient</h3>
                <div style="font-size: smaller;">{anti_nutrient_df_html}</div>
            </td>
        </tr>
    </table>
    """, unsafe_allow_html=True)