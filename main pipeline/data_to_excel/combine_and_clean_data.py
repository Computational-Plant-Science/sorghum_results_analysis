import pandas as pd
import glob
import numpy as np


def process_metadata(metadata_df):
    # Normalize column names
    metadata_df.columns = [col.strip().lower() for col in metadata_df.columns]
    df = metadata_df.copy()

    # Try to detect Format A (condition columns contain plot numbers)
    condition_columns = [col for col in df.columns if col in ['well-watered', 'water-limited', 'hi', 'li']]

    if condition_columns and 'genotype name' in df.columns:
        melted = df.melt(
            id_vars=['genotype name'],
            value_vars=condition_columns,
            var_name='Condition',
            value_name='plot_number'
        )
        melted = melted.rename(columns={'genotype name': 'Genotype'})

        # Normalize condition labels
        melted['Condition'] = melted['Condition'].str.upper().replace({
            'WELL-WATERED': 'HI',
            'WATER-LIMITED': 'LI'
        })

    # Try to detect Format B (replicate columns with Treat or Condition)
    elif any('rep' in col for col in df.columns):
        rep_columns = [col for col in df.columns if 'rep' in col]
        genotype_col = next((col for col in df.columns if 'genotype' in col), None)
        condition_col = next((col for col in df.columns if col in ['treat', 'treatment', 'condition']), None)

        if genotype_col and condition_col:
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
            melted['Condition'] = melted['Condition'].str.upper()
        else:
            raise ValueError("Missing required columns like 'Genotype' or 'Treat/Condition' in replicate format.")

    else:
        raise ValueError("Metadata format not recognized. Please standardize column names or add support.")

    melted = melted.dropna(subset=['plot_number'])  # Drop missing values
    melted['plot_number'] = melted['plot_number'].astype(str).str.strip()

    return melted[['plot_number', 'Genotype', 'Condition']]


def combine_excels(file_path, metadata_path):
    """
    Combines trait Excel files, averages by plot number, and merges with metadata.
    """
    file_list = glob.glob(file_path)
    data_frames = []

    for filename in file_list:
        df_temp = pd.read_excel(filename)
        base_filename = filename.split("/")[-1]
        name_without_extension = base_filename.rsplit('.', 1)[0]
        if name_without_extension.startswith("T_"):
            name_without_extension = name_without_extension[2:]
        df_temp['filename'] = name_without_extension
        data_frames.append(df_temp)

    if not data_frames:
        raise ValueError("No files found matching the pattern: " + file_path)

    combined_df = pd.concat(data_frames, axis=0, ignore_index=True)

    combined_df = combined_df.drop(columns=['Unnamed: 0'], errors='ignore')

    combined_df['plot_number'] = combined_df['filename'].astype(str).apply(lambda x: x.split('_')[0])
    numeric_cols = combined_df.select_dtypes(include='number').columns.tolist()

    averaged_df = combined_df.groupby('plot_number')[numeric_cols].mean().reset_index()

    metadata_df = pd.read_excel(metadata_path)
    metadata_long = process_metadata(metadata_df)
    metadata_long['Genotype'] = metadata_long['Genotype'].str.replace('.', '', regex=False)

    merged_df = pd.merge(averaged_df, metadata_long, on='plot_number', how='left')

    group_cols = ['Genotype'] + (['Condition'] if 'Condition' in merged_df.columns else [])
    final_df = merged_df.groupby(group_cols, as_index=False)[numeric_cols].mean()

    return final_df

def scale_factor(df):
    """
    Applies scaling factors to specific trait columns and saves the scaled dataframe.
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
            mask = (df_out[col] < lower) | (df_out[col] > upper)
            df_out.loc[mask, col] = np.nan

    return df_out


def main():
    file_path = "./trait_excels/arizona_excels/*.xlsx"
    metadata_path = "trait_excels/genotype_plot_number/sorghum2024_sample_info_wide.xlsx"
    output_name = "combined_trait_results_arizona_scaled_cleaned.xlsx"

    # file_path = "./trait_excels/texas_excels/*.xlsx"
    # metadata_path = "texas/Root sampling at TTU_2024.xlsx"
    # output_name = "combined_trait_results_texas_scaled_cleaned.xlsx"
    
    df = combine_excels(file_path, metadata_path)
    df_scaled = scale_factor(df)
    df_cleaned = replace_outliers_iqr(df_scaled, k=1.5, winsorise=True)

    df_cleaned.to_excel(output_name, index=False)

if __name__ == '__main__':
    main()