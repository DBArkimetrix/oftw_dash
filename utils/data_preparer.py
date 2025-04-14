import polars as pl

import openai
import os
from pathlib import Path

import json
import cairosvg  # You'll need to install this: pip install cairosvg
import base64
import re
from PIL import Image
from io import BytesIO

from utils.data_loader import data_loader

# Set up OpenAI API (ensure this is your valid API key)
openai.api_key = os.getenv("OPENAI_API_KEY")

LOGO_DIR = (Path(__file__)/'..'/'..'/'data/downloaded_logos/').resolve()

class DataPreparer:
    def __init__(self):
        pass

    def get_col_unique_values(self, dataset_name, col_name, sort_desc = False):
        """
        Retrieves the unique list of column from the dataset.
        """
        lf = data_loader.get_data(dataset_name)
        return lf.filter(pl.col(col_name).is_not_null()).select(col_name).unique().sort(by = col_name, descending = sort_desc).collect().to_series().to_list()
    
    def get_unique_col_count(self, dataset_name, col_name):
        """
        Retrieves the count of unique values in the column.
        """
        lf = data_loader.get_data(dataset_name)
        return lf.filter(pl.col(col_name).is_not_null()).select(pl.col(col_name).n_unique()).collect().item()
    
    def get_col_unique_values_lf(self, lf, column_name):
        """
        Returns the unique values of a given column in a DataFrame.

        Parameters:
        lf (DataFrame): The DataFrame containing the column.
        column_name (str): The name of the column to get unique values from.

        Returns:
        list: A list of unique values in the specified column.
        """
        return lf.filter(pl.col(column_name).is_not_null()).select(column_name).unique().sort(by = column_name).collect().to_series().to_list()
    
    def get_unique_col_count_lf(self, lf, column_name):
        """
        Returns the count of unique values of a given column in a DataFrame.

        Parameters:
        lf (DataFrame): The DataFrame containing the column.
        column_name (str): The name of the column to get unique values count from.

        Returns:
        list: A total count of unique values in the specified column.
        """
        return lf.filter(pl.col(column_name).is_not_null()).select(pl.col(column_name).n_unique()).collect().item()
    
    def get_column_max_value(self, dataset_name, column_name):
        """
        Returns the maximum value of a given column in a DataFrame.

        Parameters:
        lf (DataFrame): The DataFrame containing the column.
        column_name (str): The name of the column to get the maximum value from.

        Returns:
        list: A list of unique values in the specified column.
        """
        return data_loader.get_data(dataset_name).filter(pl.col(column_name).is_not_null()).select(pl.col(column_name).max()).collect().item()

    def filter_data(self, dataset_name, filters = None, columns = None, logic = "AND"):
        """
        Generic method to filter and select columns from a dataset.

        Parameters:
        - dataset_name (str): Dataset to query.
        - filters (list of tuples): [(canonical_name, operator, value)], e.g., [("center_id", "==", 123)].
        - columns (list of str): Canonical column names to return.
        - logic (str): "AND" (default) or "OR" for combining filters.

        Returns:
        - LazyFrame: Filtered and projected dataset.
        """
        lf = data_loader.get_data(dataset_name)

        # Apply filters if provided
        if filters:
            expressions = [self._build_filter_expr(dataset_name, f) for f in filters]
            # print(expressions)
            # combined_filter = pl.all(expressions) if logic == "AND" else pl.any(expressions)
            # print(combined_filter)
            lf = lf.filter(expressions)

        # Select required columns
        if columns:
            lf = lf.select(columns)

        return lf

    def _build_filter_expr(self, dataset_name, filter_tuple):
        """
        Helper to convert (canonical_name, operator, value) to a Polars expression.
        """
        col_name, operator, value = filter_tuple

        # Handle None values
        if operator in ["not_null", "null"]:
            if operator == "not_null":
                return pl.col(col_name).is_not_null()
            elif operator == "null":
                return pl.col(col_name).is_null()
        
        ops = {
            "==": pl.col(col_name) == value,
            "!=": pl.col(col_name) != value,
            ">": pl.col(col_name) > value,
            ">=": pl.col(col_name) >= value,
            "<": pl.col(col_name) < value,
            "<=": pl.col(col_name) <= value,
            "in": pl.col(col_name).is_in(value) if isinstance(value, list) else pl.col(col_name) == value,
            "not_in": ~pl.col(col_name).is_in(value) if isinstance(value, list) else pl.col(col_name) != value,
        }

        if operator not in ops:
            raise ValueError(f"Unsupported operator: {operator}")

        return ops[operator]
    
    def get_llm_insight(self, plotly_fig_data):
        """
        Placeholder for LLM insight retrieval.
        """

        prompt = """
            You are an AI assistant for the OFTW (One for the World is a movement aimed at revolutionizing charitable giving to 
            eradicate extreme poverty by educating and motivating people to donate effectively.) dashboard.
            Based on the plotly figure data below, provide:  
            1. A short (1 line) summary of what the graph shows. 
            2. 2 key insights from the data. 
            3. 2 actionable suggestions for organization.  
            Plotly Figure Data: {}
            Please provide the insights in a markdown format, such as:
            1. Summary: [Your summary here]
            2. Key Insights: [Your insights here]
            3. Action Suggestions: [Your suggestions here]
            Use plain language and keep it concise. 
        """.format(plotly_fig_data)

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                n=1,
                stop=None,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in LLM insight retrieval: {e}")
            # Handle error (e.g., log it, raise it, etc.)
            # For now, return a placeholder
            return "LLM could not generate insight."
        
    # Load logo mappings
    def load_logo_mappings(self):
        """Load the mapping between donor_chapter names and logo filenames"""
        mapping_file = LOGO_DIR / "logo_mapping.json"
        
        if mapping_file.exists():
            with open(mapping_file, "r") as f:
                return json.load(f)
        else:
            # Create a simple mapping from files that exist
            mapping = {}
            logo_files = list(LOGO_DIR.glob("*.svg")) + list(LOGO_DIR.glob("*.png")) + list(LOGO_DIR.glob("*.ico"))
            
            # Try to match logo filenames to organization names
            for logo_file in logo_files:
                # Extract organization name from filename (without extension)
                slug = logo_file.stem
                # Convert slug back to a name (very basic)
                org_name = slug.replace('-', ' ').title()
                mapping[org_name] = logo_file.name
            
            return mapping

    def get_logo_as_base64(self, logo_filename, height=30):
        """Get the logo as a base64 encoded string, resized to specified height"""
        
        file_path = LOGO_DIR / logo_filename
        if not file_path.exists():
            return None
        
        try:
            # Handle different file formats
            if file_path.suffix.lower() == '.svg':
                # Convert SVG to PNG using cairosvg
                png_data = cairosvg.svg2png(
                    url=str(file_path),
                    output_width=None,  
                    output_height=height
                )
                encoded = base64.b64encode(png_data).decode('ascii')
                b64_image = f"data:image/png;base64,{encoded}"
            else:
                # For PNG, JPG, ICO, etc.
                with Image.open(file_path) as img:
                    # Calculate new width to maintain aspect ratio
                    width = int(img.width * (height / img.height))
                    # Resize the image
                    img = img.resize((width, height), Image.LANCZOS)
                    
                    # Save to BytesIO in PNG format
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    
                    encoded = base64.b64encode(buffer.read()).decode('ascii')
                    b64_image = f"data:image/png;base64,{encoded}"
            
            return b64_image
        
        except Exception as e:
            print(f"Error processing logo {logo_filename}: {e}")
            return None
        
    # Function to find the best matching logo for a donor chapter
    def find_best_logo_match(self, donor_chapter, logo_mapping):
        """Find the best matching logo for a donor chapter name"""
        if donor_chapter in logo_mapping:
            return logo_mapping[donor_chapter]
        
        # Try to find a partial match
        donor_lower = donor_chapter.lower()
        for org_name, logo_file in logo_mapping.items():
            if org_name.lower() in donor_lower or donor_lower in org_name.lower():
                return logo_file
        
        # Try matching with standardized names
        donor_slug = re.sub(r'[^a-z0-9\s]', '', donor_lower).replace(' ', '-')
        for logo_file in os.listdir(LOGO_DIR):
            file_stem = Path(logo_file).stem
            if donor_slug in file_stem or file_stem in donor_slug:
                return logo_file
        
        return None