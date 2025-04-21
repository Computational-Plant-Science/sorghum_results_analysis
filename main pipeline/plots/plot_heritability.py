import pandas as pd
import numpy as np
import plotly.express as px

def get_statistics(df, treat_label=None):
    """
    Cleans data, applies scaling, and calculates trait statistics including heritability.
    """
    
    df = df.drop(columns=['Unnamed: 0'], errors='ignore')
    df_numeric = df.select_dtypes(include='number')

    stats = {
        'Trait': [], 'Variance': [], 'Mean': [], 'Standard Deviation': [],
        'Ve (Error Variance)': [], 'Vg (Genetic Variance)': [],
        'Vp (Phenotypic Variance)': [], 'H2 (Heritability)': [],
        'Treat': []
    }
    n_replicates = 80

    for col in df_numeric.columns:
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
        stats['Treat'].append(treat_label if treat_label is not None else 'Overall')

    return pd.DataFrame(stats)

def plot_stats(stats_df, separate_by_treat=False, max_error=5, show_error=True):
    df = stats_df.copy()
    df['Ve (Error Variance)'] = df['Ve (Error Variance)'].clip(upper=max_error)

    error_kwargs = {'error_y': 'Ve (Error Variance)'} if show_error else {}

    if separate_by_treat:
        fig = px.bar(
            df,
            x='Trait',
            y='H2 (Heritability)',
            color='Treat',
            barmode='group',
            title='Heritability Comparison (HI vs LI)',
            labels={'H2 (Heritability)': 'Heritability (H²)'},
            **error_kwargs
        )
    else:
        fig = px.bar(
            df,
            x='Trait',
            y='H2 (Heritability)',
            title='Overall Heritability',
            labels={'H2 (Heritability)': 'Heritability (H²)'},
            **error_kwargs
        )

    fig.update_layout(xaxis_tickangle=-45)
    fig.show()


def main(separate_by_treat=False, show_error=False):
    file_path = "combined_trait_results_arizona_scaled_cleaned.xlsx"
    df = pd.read_excel(file_path)

    if separate_by_treat:
        df_hi = df[df['Condition'] == 'HI']
        df_li = df[df['Condition'] == 'LI']

        stats_hi = get_statistics(df_hi, treat_label='HI')
        stats_li = get_statistics(df_li, treat_label='LI')

        stats_all = pd.concat([stats_hi, stats_li], ignore_index=True)
        plot_stats(stats_all, separate_by_treat=True, show_error=show_error)

    else:
        stats_overall = get_statistics(df, treat_label=None)
        plot_stats(stats_overall, separate_by_treat=False, show_error=show_error)


if __name__ == '__main__':
    # main(separate_by_treat=False, show_error=True)
    # main(separate_by_treat=False, show_error=False)
    # main(separate_by_treat=True,show_error=True)
    main(separate_by_treat=True, show_error=False)
    
