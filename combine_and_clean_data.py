import argparse
import pandas as pd
import glob
import numpy as np
import os
import re

def process_metadata(metadata_df):
    """
    Converts metadata from wide to long format and standardizes columns.
    - If there are NO 'rep' or explicit 'condition' columns, assumes every
      other column is a treatment/condition (e.g. 'ww', 'hi', 'low', etc.).
    - Else, treats columns containing 'rep' as replicates and melts them
      using the first found 'condition' column.

    Returns a DataFrame with ['plot_number', 'Genotype', 'Condition'].
    """
    metadata_df.columns = metadata_df.columns.str.strip().str.lower()
    df = metadata_df.copy()

    genotype_col   = next((c for c in df.columns if 'genotype' in c), None)
    rep_columns    = [c for c in df.columns if 'rep' in c]
    treat_columns  = [c for c in df.columns 
                      if any(k in c for k in ('treat', 'treatment', 'condition'))]

    if genotype_col is None:
        raise ValueError("Could not find a 'genotype' column in metadata.")

    if not rep_columns and not treat_columns:
        condition_columns = [c for c in df.columns if c != genotype_col]
        melted = df.melt(
            id_vars=[genotype_col],
            value_vars=condition_columns,
            var_name='Condition',
            value_name='plot_number'
        )
        melted = melted.rename(columns={genotype_col: 'Genotype'})

        melted['Condition'] = (
            melted['Condition']
              .str.replace(r'[\.\-]', '_', regex=True)
              .str.strip().str.upper()
        )

    elif rep_columns and treat_columns:
        condition_col = treat_columns[0]
        melted = df.melt(
            id_vars=[condition_col, genotype_col],
            value_vars=rep_columns,
            var_name='Rep',
            value_name='plot_number'
        )
        melted = melted.rename(columns={
            genotype_col: 'Genotype',
            condition_col: 'Condition'
        })
        melted['Condition'] = melted['Condition'].astype(str).str.upper()

    else:
        raise ValueError(
            "Metadata format not recognized: mixed presence of 'rep' and "
            "no explicit treatment columns."
        )

    melted = melted.dropna(subset=['plot_number'])
    melted['plot_number'] = melted['plot_number'].astype(str).str.strip()

    return melted[['plot_number', 'Genotype', 'Condition']]

def combine_excels(file_pattern, metadata_path):
    """
    Combines multiple Excel files into a single cleaned DataFrame.
    Averages numeric trait columns by plot, merges with metadata,
    and computes average trait values grouped by Genotype and Condition.

    Parameters:
    - file_pattern (str): Glob pattern to find all relevant Excel files.
    - metadata_path (str): Path to the Excel metadata file.

    Returns:
    - pd.DataFrame: Merged and averaged DataFrame ready for scaling/cleaning.
    """
    file_list = glob.glob(file_pattern)
    data_frames = []

    for filename in file_list:
        df_temp = pd.read_excel(filename)
        base = os.path.basename(filename).rsplit('.', 1)[0]

        # find all digit-runs, pick the longest (e.g. "1104" over "1")
        nums = re.findall(r'\d+', base)
        if not nums:
            raise ValueError(f"Could not extract any digits from filename: {base}")
        plot_number = max(nums, key=len)

        df_temp['plot_number'] = plot_number
        data_frames.append(df_temp)

    if not data_frames:
        raise ValueError("No files found matching the pattern: " + file_pattern)

    combined_df = pd.concat(data_frames, ignore_index=True)
    combined_df = combined_df.drop(columns=['Unnamed: 0'], errors='ignore')

    # average numeric columns per plot
    numeric_cols = combined_df.select_dtypes(include='number').columns.tolist()
    averaged_df = combined_df.groupby('plot_number', as_index=False)[numeric_cols].mean()

    # merge with metadata
    metadata_df  = pd.read_excel(metadata_path)
    metadata_long = process_metadata(metadata_df)
    metadata_long['Genotype'] = metadata_long['Genotype'].str.replace('.', '', regex=False)

    merged_df = pd.merge(averaged_df,
                         metadata_long,
                         on='plot_number',
                         how='left')

    group_cols = ['Genotype'] + (['Condition'] if 'Condition' in merged_df.columns else [])
    final_df = merged_df.groupby(group_cols, as_index=False)[numeric_cols].mean()
    return final_df

def scale_factor(df):
    """
    Applies domain-specific scaling to select trait columns using known constants.
    
    Parameters:
    - df (pd.DataFrame): DataFrame with numeric trait data.

    Returns:
    - pd.DataFrame: Scaled DataFrame.
    """
    scaling_factors = {
        'root system diameter max': 15.1774500525728,
        'root system diameter min': 15.1774500525728,
        'root system diameter': 15.1774500525728,
        'root system length': 15.1774500525728,
        'root system volume': 230.354990098342
    }
    for col, factor in scaling_factors.items():
        if col in df.columns:
            df[col] *= factor
    return df

def replace_outliers_iqr(df, k=1.5, winsorise=True):
    """
    Removes or clips outliers in numeric columns using the IQR method.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - k (float): Multiplier for IQR to define outlier bounds.
    - winsorise (bool): If True, clips values instead of removing them.

    Returns:
    - pd.DataFrame: DataFrame with outliers handled.
    """
    df_out = df.copy()
    numeric_cols = df_out.select_dtypes(include='number').columns
    for col in numeric_cols:
        q1 = df_out[col].quantile(0.25)
        q3 = df_out[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - k * iqr
        upper = q3 + k * iqr
        if winsorise:
            df_out[col] = df_out[col].clip(lower, upper)
        else:
            df_out.loc[(df_out[col] < lower) | (df_out[col] > upper), col] = np.nan
    return df_out

def run_pipeline(input_dir, metadata_path, output_name):
    """
    Runs the full data preparation pipeline:
    - Combines raw Excel files
    - Scales specific traits
    - Handles outliers
    - Saves cleaned output

    Parameters:
    - input_dir (str): Directory containing input Excel files.
    - metadata_path (str): Path to metadata Excel file.
    - output_name (str): Path to save cleaned output Excel file.
    """
    file_pattern = os.path.join(input_dir, '*.xlsx')
    df = combine_excels(file_pattern, metadata_path)
    df_scaled = scale_factor(df)
    df_cleaned = replace_outliers_iqr(df_scaled, k=1.5, winsorise=True)
    df_cleaned.to_excel(output_name, index=False)
    print(f"Saved cleaned dataset to: {output_name}")

def parse_args():
    """
    Parses command-line arguments for the data processing pipeline.
    """
    p = argparse.ArgumentParser(description="Combine, scale, and clean trait Excel files using metadata.")
    p.add_argument('--input-dir', default='data/raw', help="Folder containing raw Excel trait files")
    p.add_argument('--metadata',  default='data/meta.xlsx', help="Metadata file (Excel)")
    p.add_argument('--output',    default="/srv/data/cleaned.xlsx", help="Path to save the final cleaned file")
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    run_pipeline(args.input_dir, args.metadata, args.output)
