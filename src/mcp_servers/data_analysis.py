from fastmcp import FastMCP
from groq import Groq

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import logging
import base64
import json
import os
from typing import List, Optional, Dict, Any, Union

logging.basicConfig(
    filename='logs/data_analysis.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataAnalysisMCPServer")

mcp = FastMCP(
    "data_analysis",
    description="Data Analysis and Visualization Server"
)

groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key)
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

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


@mcp.tool
def get_raw_data(dataset: pd.DataFrame, filters: Optional[Dict[str, Union[str, int]]] = None) -> Union[pd.DataFrame|str]:
    """
    Returns the raw dataset or a filtered subset for analysis.

    Args:
        filters (dict, optional): Filtering conditions. Example: {"country": "Philippines", "year": 2024}
    
    Returns:
        DataFrame: The raw or filtered dataset.
    """
    try:
        data = dataset.copy()

        if filters:
            for col, value in filters.items():
                data = data[data[col] == value]

        return data

    except Exception as e:
        logger.error(f"Error in get_raw_data: {str(e)}")
        return f"Error processing data: {str(e)}"


@mcp.tool
def clean_data(dataset: pd.DataFrame, method: str = "fillna") -> Union[pd.DataFrame|str]:
    """
    Cleans the dataset by handling missing values and duplicates.

    Args:
        dataset (DataFrame): The dataset to clean.
        method (str): The cleaning or preprocessing method to apply.
                    Supported methods: 'fillna', 'normalize'

    Returns:
        DataFrame: The cleaned dataset.
    """
    cleaned = dataset.copy()

    if method == "fillna":
        cleaned = cleaned.ffill()
    elif method == "normalize":
        numeric_cols = cleaned.select_dtypes(include=[np.number]).columns
        cleaned[numeric_cols] = cleaned[numeric_cols].apply(min_max_normalize)
    else:
        logger.error(f"Unknown cleaning method: {method}")
        return f"Unknown cleaning method: {method}"

    return cleaned


@mcp.tool
async def extract_chart_data(img_url: str = None, chart_type: str = "", columns: List[str] = []) -> dict:
    """
    Extracts chart data from a given image URL.

    Args:
        img_url (str): URL of the chart image.
        chart_type (str): Type of the chart (e.g., "bar", "line").
        columns (List[str]): List of columns to extract data from.

    Returns:
        dict: Extracted chart data in JSON format.
    """
    try:
        prompt = (
                f"You are an expert data analyst specialized in interpreting chart images. "
                f"Carefully examine the provided {chart_type} chart image and extract all available numeric data. "
                f"Focus on the following columns or labels: {', '.join(columns)}. Ignore other columns or labels. "
                f"For each label, identify the corresponding numeric value as accurately as possible. "
                f"Return your answer strictly as a JSON object using this format:\n\n"
                f"{{\n"
                f"  {{'label': <column_name>, 'value': <numeric_value>}}, ...\n"
                f"}}\n\n"
                f"Do not include explanations or extra text outside the JSON."
            )

        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": img_url}}  # make sure the url is publicly accessible
                    ]
                }
            ],
            temperature=0.7,
            max_completion_tokens=512,
            top_p=1,
            response_format={"type": "json_object"},
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Error in extract_chart_data: {str(e)}")
        return {"error": "Groq API call failed", "details": str(e)}


@mcp.tool
def compute_statistics(dataset: pd.DataFrame, columns: List[str], metrics: List[str]) -> dict:
    """
    Computes the mean, median, and std of specified columns.

    Args:
        dataset (DataFrame): The dataset to analyze.
        columns (List[str]): List of columns to compute statistics for.
        metrics (List[str]): List of metrics to compute. Possible values are ["mean", "median", "std"].

    Returns:
        dict: A dictionary containing the computed statistics.
    """
    stats = {}
    try:
        for col in columns:
            stats[col] = {}
            if "mean" in metrics:
                stats[col]["mean"] = dataset[col].mean()
            if "median" in metrics:
                stats[col]["median"] = dataset[col].median()
            if "std" in metrics:
                stats[col]["std"] = dataset[col].std()

            unknown_metrics = [m for m in metrics if m not in ["mean", "median", "std"]]
            if unknown_metrics:
                logger.error(f"Unknown metric(s): {unknown_metrics}")
                return {"error": f"Unknown metric(s): {unknown_metrics}"}

    except Exception as e:
        logger.error(f"Error computing statistics: {str(e)}")
        return {"error": "Statistics computation failed", "details": {str(e)}}

    return stats


@mcp.tool
def visualize_data(dataset: pd.DataFrame, x_axis: str, y_axis: List[str], plot_type: str) -> str:
    """
    Generates a chart visualization (bar, line, scatter) from the dataset.
    If plot type is "scatter", the y_axis should be a single column.

    Args:
        dataset (DataFrame): The dataset to visualize.
        x_axis (str): The column to use for the x-axis.
        y_axis (List[str]): List of columns to use for the y-axis.
        plot_type (str): Type of plot to create. Possible values are ["bar", "line", "scatter"].

    Returns:
        str: The path to the generated image.
    """
    if plot_type not in ["bar", "line", "scatter"]:
        logger.error(f"Unknown plot type: {plot_type}")
        return f"Unknown plot type: {plot_type}"
    
    try:
        # Ensure the 'plots' directory exists
        os.makedirs("plots", exist_ok=True)
        dataset.plot(kind=plot_type, x=x_axis, y=y_axis, title=f"{plot_type.capitalize()} Plot")
        plt.savefig(f"plots/{plot_type}_plot.png", bbox_inches='tight')
        plt.close()
        return f"plots/{plot_type}_plot.png"

    except Exception as e:
        logger.error(f"Error in visualize_data: {str(e)}")
        return f"Error generating {plot_type} plot: {str(e)}"


@mcp.tool
async def generate_report(dataset: pd.DataFrame, stats: dict, plots: List[str]) -> str:
    """
    Generates a summary report based on the dataset and analysis results.

    Args:
        dataset (DataFrame): The dataset to analyze.
        stats (dict): Computed statistics from the dataset.
        plots (List[str]): List of plot image paths to include in the report.

    Returns:
        str: A textual summary report.
    """
    try:
        prompt = (
            "You are a data analyst. Write a clear, insightful summary based on the dataset, statistics, and plots below.\n\n"
            "### Dataset Preview\n"
            f"{dataset.head(10).to_string(index=False)}\n\n"
            "### Statistics\n"
            f"{json.dumps(stats, indent=2)}\n\n"
            "### Notes\n"
            "- Mention key patterns, trends, and anomalies.\n"
            "- Refer to the provided plots when relevant.\n"
            "- Keep it concise, professional, and easy to read.\n\n"
        )

        base64_images = [encode_image(plot) for plot in plots]

        content = [{"type": "text", "text": prompt}]
        for b64_img in base64_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64_img}"
                }
            })

        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=0.7,
            max_completion_tokens=512,
            top_p=1,
            stream=False,
            stop=None,
        )
         
        return completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Error in generate_report: {str(e)}")
        return f"Error generating report: {str(e)}"
    

@mcp.tool
def detect_outliers(dataset: pd.DataFrame, columns: List[str], method: str = "z_score") -> dict:
    """
    Identifies outliers in a dataset.

    Args:
        dataset (DataFrame): The dataset to analyze.
        columns (List[str]): List of columns to check for outliers.
        method (str): Method to use for outlier detection. Possible values are ["z_score", "iqr"].

    Returns:
        dict: A dictionary with column names as keys and lists of outlier values.
    """
    outliers = {}
    try:
        for col in columns:
            if method == "z_score":
                threshold = 2.0
                mean = dataset[col].mean()
                std = dataset[col].std()
                outliers[col] = dataset[(np.abs((dataset[col] - mean) / std) > threshold)][col].tolist()
            elif method == "iqr":
                Q1 = dataset[col].quantile(0.25)
                Q3 = dataset[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers[col] = dataset[(dataset[col] < lower_bound) | (dataset[col] > upper_bound)][col].tolist()
            else:
                logger.error(f"Unknown outlier detection method: {method}")
                return {"error": f"Unknown outlier detection method: {method}"}

    except Exception as e:
        logger.error(f"Error detecting outliers: {str(e)}")
        return {"error": "Outlier detection failed", "details": {str(e)}}

    return outliers


@mcp.tool
def compare_datasets(dataset1: pd.DataFrame, dataset2: pd.DataFrame, columns: List[str]) -> dict:
    """
    Compares two datasets and highlights differences in specified columns.

    Args:
        dataset1 (DataFrame): The first dataset.
        dataset2 (DataFrame): The second dataset.
        columns (List[str]): List of columns to compare.

    Returns:
        dict: A dictionary highlighting differences for each specified column.
    """
    differences = {}
    try:
        for col in columns:
            diffs = dataset1[col].compare(dataset2[col])
            differences[col] = diffs.to_dict()

    except Exception as e:
        logger.error(f"Error comparing datasets: {str(e)}")
        return {"error": "Dataset comparison failed", "details": {str(e)}}

    return differences