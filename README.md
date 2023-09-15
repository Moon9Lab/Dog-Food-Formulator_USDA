# Dog Food Formulator

## Project Overview

The Food Finder Dashboard is a Streamlit application designed to provide an interactive exploration of nutrient content in various food items. The application allows users to select a nutrient of interest from a dropdown list and displays bar charts that rank the top 10 foods highest in that nutrient for each of four food categories:

- Vegetables and Vegetable Products
- Legumes and Legume Products
- Spices and Herbs
- Cereal Grains and Pasta

## Features

- Dropdown menu to select a nutrient from a list of available nutrients.
- Interactive bar charts to display the top 10 foods rich in the selected nutrient for each specified category.
- Bar charts include the unit of measurement for the nutrient and food descriptions that are easy to interpret.

## Prerequisites

Before running this project, you should have the following installed:

- Python 3.x
- Streamlit
- Pandas
- Matplotlib

You can install the Python packages using pip:

```bash
pip install streamlit pandas matplotlib
```

## Data Sources

The application uses the following CSV files:

- `nutrient.csv`: Contains nutrient names and IDs.
- `food.csv`: Contains food item names and their category IDs.
- `food_nutrient.csv`: Contains the nutrient amount in each food item.
- `food_category.csv`: Contains food category names and IDs.

## How to Run

1. Clone the repository or download the source code.
2. Navigate to the project folder in the terminal.
3. Run the following command:

```bash
streamlit run 01_Finder_streamlit.py
```

This will start the Streamlit app and automatically open it in your default web browser.

## Contributions

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or create a pull request.

## Data Source

The data used in this project originates from the [FoodData Central](https://fdc.nal.usda.gov/download-datasets.html) provided by the U.S. Department of Agriculture. Specifically, the data type used is "SR Legacy," and the file downloaded is from "APRIL 2018 (csv)."

For more information on the dataset and to view the original source, please visit [FoodData Central's Download Datasets page](https://fdc.nal.usda.gov/download-datasets.html).

## License and Citation

This project is released under an open-source license. Users are free to utilize the codebase for research, commercial purposes, or any other lawful activity. While not a strict requirement, we kindly request that you attribute this repository by citing it in any publications or derivative works. 


