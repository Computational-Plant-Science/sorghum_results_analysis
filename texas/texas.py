import pandas as pd
import glob
import numpy as np
import plotly.express as px

def combine_excels():
    """
    Grabs all files in ./trait_results and combines them into one excel sheet.
    """
    l = [pd.read_excel(filename) for filename in glob.glob("./texas/texas_excels/*.xlsx")]

    df = pd.concat(l, axis=0)
    print(df.columns)

    file_name = "combined_trait_results_texas.xlsx"
    df.to_excel(file_name)
    
    print(f"Traits loaded into {file_name} successfully")
    return df

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

    file_name = "combined_trait_results_texas_scaled.xlsx"
    df.to_excel(file_name)

    return df


def get_statistics(df, treat_label=None):
    """
    Calculates trait-level statistics and heritability.
    """
    stats = {
        'Trait': [],
        'Variance': [],
        'Mean': [],
        'Standard Deviation': [],
        'Ve (Error Variance)': [],
        'Vg (Genetic Variance)': [],
        'Vp (Phenotypic Variance)': [],
        'H2 (Heritability)': [],
    }
    n_replicates = 80

    for col in df.columns:
        variance = df[col].var()
        mean = df[col].mean()
        std_dev = df[col].std()

        ve = std_dev / np.sqrt(n_replicates)
        vg = np.abs(np.sqrt(mean) - ve) / n_replicates
        vp = ve / n_replicates + vg
        h2 = vg / vp if vp != 0 else np.nan

        stats['Trait'].append(col)
        stats['Variance'].append(variance)
        stats['Mean'].append(mean)
        stats['Standard Deviation'].append(std_dev)
        stats['Ve (Error Variance)'].append(ve)
        stats['Vg (Genetic Variance)'].append(vg)
        stats['Vp (Phenotypic Variance)'].append(vp)
        stats['H2 (Heritability)'].append(h2)

    return pd.DataFrame(stats)

def plot_stats(stats_df):
    """
    Plots heritability (H²) for each trait in a bar chart.
    """
    # filtered_df = stats_df[stats_df['Trait'] != 'root system volume']

    fig = px.bar(
        stats_df,
        x='Trait',
        y='H2 (Heritability)',
        title='Overall Heritability',
        labels={'H2 (Heritability)': 'Heritability (H²)'},
        # error_y='Ve (Error Variance)'
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def main():
    df = combine_excels()
    df = scale_factor(df)
    df_stats = get_statistics(df)
    plot_stats(df_stats)

if __name__ == '__main__':
    main()