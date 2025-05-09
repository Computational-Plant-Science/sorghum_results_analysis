import argparse
import pandas as pd
import numpy as np
import plotly.express as px

def normalize_condition_labels(df):
    mapping = {
        'well_watered': 'HI',
        'well watered': 'HI',
        'ww': 'HI',
        'hi': 'HI',
        'water_limited': 'LI',
        'water limited': 'LI',
        'wl': 'LI',
        'li': 'LI'
    }
    df['Condition'] = (
        df['Condition']
        .astype(str)
        .str.lower()
        .str.strip()
        .replace(mapping)
        .str.upper()
    )
    return df


def get_statistics(df, treat_label=None, n_replicates=80):
    """
    Computes statistical metrics for each numeric trait including estimated heritability (H2).

    Parameters:
    - df (pd.DataFrame): Input data containing numeric traits.
    - treat_label (str): Label to indicate treatment group (e.g., 'HI', 'LI'). Defaults to 'Overall'.
    - n_replicates (int): Number of replicates used to compute error and genetic variance.

    Returns:
    - pd.DataFrame: DataFrame with statistical values per trait including heritability.
    """
    df = df.drop(columns=['Unnamed: 0'], errors='ignore')
    df_numeric = df.select_dtypes(include='number')

    stats = {
        'Trait': [], 'Variance': [], 'Mean': [], 'Standard Deviation': [],
        'Ve (Error Variance)': [], 'Vg (Genetic Variance)': [],
        'Vp (Phenotypic Variance)': [], 'H2 (Heritability)': [],
        'Treat': []
    }

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

def plot_heritability(
    input_file: str,
    out_png: str | None = None,
    separate_by_treat: bool = False,
    show_error: bool = False,
    max_error: float = 5.0
):
    """
    Generates bar plots of heritability (H2) by trait, optionally split by treatment.

    Parameters:
    - input_file (str): Path to Excel file containing cleaned data.
    - out_png (str): Path to save output PNG image (optional).
    - separate_by_treat (bool): Whether to generate separate bars for 'HI' and 'LI'.
    - show_error (bool): Whether to include error bars based on error variance.
    - max_error (float): Maximum error bar value (for clipping).
    """
    df = pd.read_excel(input_file)
    df = normalize_condition_labels(df)

    if separate_by_treat:
        df_hi = df[df['Condition'] == 'HI']
        df_li = df[df['Condition'] == 'LI']

        stats_hi = get_statistics(df_hi, treat_label='HI')
        stats_li = get_statistics(df_li, treat_label='LI')
        stats_df = pd.concat([stats_hi, stats_li], ignore_index=True)
    else:
        stats_df = get_statistics(df)

    stats_df['Ve (Error Variance)'] = stats_df['Ve (Error Variance)'].clip(upper=max_error)
    error_kwargs = {'error_y': 'Ve (Error Variance)'} if show_error else {}

    fig = px.bar(
        stats_df,
        x='Trait',
        y='H2 (Heritability)',
        color='Treat' if separate_by_treat else None,
        barmode='group' if separate_by_treat else 'relative',
        title='Heritability by Trait',
        labels={'H2 (Heritability)': 'Heritability (H²)'},
        **error_kwargs
    )

    fig.update_layout(xaxis_tickangle=-45)

    if out_png:
        fig.write_image(out_png)
        print(f"Saved heritability plot to {out_png}")
    else:
        fig.show()

def main():
    """
    Command-line interface for heritability analysis and visualization.
    """
    parser = argparse.ArgumentParser(description="Generate heritability bar plots.")
    parser.add_argument("--input", required=True, help="Path to cleaned Excel file (e.g. cleaned.xlsx)")
    parser.add_argument("--out", help="Output plot image file (e.g. heritability.png)")
    parser.add_argument("--separate-by-treat", action="store_true", help="Plot HI vs LI side-by-side")
    parser.add_argument("--show-error", action="store_true", help="Show error bars")
    parser.add_argument("--max-error", type=float, default=5.0, help="Clip max error bar to this value")

    args = parser.parse_args()

    plot_heritability(
        input_file=args.input,
        out_png=args.out,
        separate_by_treat=args.separate_by_treat,
        show_error=args.show_error,
        max_error=args.max_error
    )

if __name__ == "__main__":
    main()
