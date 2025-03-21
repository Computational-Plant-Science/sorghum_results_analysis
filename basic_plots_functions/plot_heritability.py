import pandas as pd
import numpy as np
import plotly.express as px

def get_statistics(df, treat_label=None):
    """
     Cleans data, applies scaling, and calculates trait statistics including heritability.
    """
    cols_to_drop = ['file_name', 'Unnamed: 0', 'Replicate', 'Plot_Number', 'Genotype']
    df_numeric = df.drop(columns=cols_to_drop, errors='ignore')

    scaling_factors = {
        'root system diameter max': 15.17745005,
        'root system diameter min': 15.17745005,
        'root system diameter': 15.17745005,
        'root system length': 15.17745005,
        'root system volume': 230.3549901
    }
    for col, factor in scaling_factors.items():
        if col in df_numeric.columns:
            df_numeric[col] *= factor

    stats = {
        'Trait': [],
        'Variance': [],
        'Mean': [],
        'Standard Deviation': [],
        'Ve (Error Variance)': [],
        'Vg (Genetic Variance)': [],
        'Vp (Phenotypic Variance)': [],
        'H2 (Heritability)': [],
        'Treat': []
    }
    n_replicates = 80

    for col in df_numeric.columns:
        if col == "Treat":
            continue
        variance = df_numeric[col].var()
        mean = df_numeric[col].mean()
        std_dev = df_numeric[col].std()

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
        stats['Treat'].append(treat_label)

    return pd.DataFrame(stats)

def plot_stats(stats_df, separate_by_treat=False):
    """
    Plots heritability for each trait using a bar chart.
    """
    filtered_df = stats_df[stats_df['Trait'] != 'root system volume']

    if separate_by_treat:
        fig = px.bar(
            filtered_df,
            x='Trait',
            y='H2 (Heritability)',
            color='Treat',
            barmode='group',
            title='Heritability Comparison (HI vs LI)',
            labels={'H2 (Heritability)': 'Heritability (H²)',},
            error_y='Ve (Error Variance)'
        )
    else:
        fig = px.bar(
            filtered_df,
            x='Trait',
            y='H2 (Heritability)',
            title='Overall Heritability',
            labels={'H2 (Heritability)': 'Heritability (H²)'},
            error_y='Ve (Error Variance)'
        )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def main():
    file_path = "traits_and_sorghums.xlsx"
    df = pd.read_excel(file_path)
    stats_overall = get_statistics(df)
    plot_stats(stats_overall, separate_by_treat=False)

    df_hi = pd.read_excel("./average_trait_values/traits_and_sorghums_HI.xlsx")
    df_li = pd.read_excel("./average_trait_values/traits_and_sorghums_LI.xlsx")

    stats_hi = get_statistics(df_hi, treat_label='HI')
    stats_li = get_statistics(df_li, treat_label='LI')

    df_combined = pd.concat([stats_hi, stats_li], ignore_index=True)

    plot_stats(df_combined, separate_by_treat=True)

if __name__ == '__main__':
    main()
