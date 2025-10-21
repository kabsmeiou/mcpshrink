import pandas as pd
import base64

# Helper function for clean_data tool
def min_max_normalize(series: pd.Series) -> pd.Series:
        """
        Applies Min-Max Normalization to a Pandas Series, scaling values to [0, 1].
        """
        min_val = series.min()
        max_val = series.max()
        
        # Handle the case where max_val == min_val to avoid division by zero
        if max_val == min_val:
            return pd.Series(0.0, index=series.index)
            
        return (series - min_val) / (max_val - min_val)

# Helper function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')