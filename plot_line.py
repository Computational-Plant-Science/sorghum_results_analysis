import argparse
import pandas as pd
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

def prepare_fully_scaled_data(df, scale='zscore'):
    """
    Prepares and reshapes the data for plotting by scaling numeric traits
    using either z-score or min-max normalization.

    Parameters:
    - df (pd.DataFrame): Input DataFrame with raw trait values.
    - scale (str): 'zscore' or 'minmax' scaling method.

    Returns:
    - pd.DataFrame: Long-form DataFrame with scaled trait values.
    """
    df = df.drop(columns=['Unnamed: 0', 'plot_number'], errors='ignore')

    trait_cols = df.select_dtypes(include='number').columns.tolist()

    if scale == 'zscore':
        df[trait_cols] = df[trait_cols].apply(lambda x: (x - x.mean()) / x.std())
    elif scale == 'minmax':
        df[trait_cols] = df[trait_cols].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    else:
        raise ValueError("scale must be 'zscore' or 'minmax'")

    df_long = df.melt(
        id_vars=['Genotype', 'Condition'],
        var_name='Trait',
        value_name='Scaled_Value'
    )
    return df_long

def plot_plain(df_long, condition, title_prefix="", out_png=None):
    """
    Plots scaled trait values across genotypes for a specific condition.

    Parameters:
    - df_long (pd.DataFrame): Long-form DataFrame with scaled values.
    - condition (str): Condition to filter for (e.g., 'HI' or 'LI').
    - title_prefix (str): Region or context to prepend to the plot title.
    - out_png (str): Optional output file path for saving the plot.
    """
    df = df_long[df_long['Condition'] == condition]
    fig = px.line(
        df, x='Trait', y='Scaled_Value',
        color='Genotype', line_group='Genotype',
        markers=True,
        title=f'{title_prefix} — {condition}',
        labels={'Scaled_Value': 'Scaled Trait Value'}
    )
    fig.update_layout(xaxis_tickangle=-45, template='plotly_white')
    if out_png:
        fig.write_image(out_png.replace(".png", f"_{condition}.png"))
        print(f"Saved plot for {condition} to {out_png.replace('.png', f'_{condition}.png')}")
    else:
        fig.show()

def plot_highlight_genotypes(df_long, condition, top_n, title_prefix="", out_png=None):
    """
    Plots scaled trait values across genotypes, highlighting the top N most variable genotypes.

    Parameters:
    - df_long (pd.DataFrame): Long-form DataFrame with scaled values.
    - condition (str): Condition to filter for (e.g., 'HI' or 'LI').
    - top_n (int): Number of most variable genotypes to highlight.
    - title_prefix (str): Region or context to prepend to the plot title.
    - out_png (str): Optional output file path for saving the plot.
    """
    df = df_long[df_long['Condition'] == condition]

    geno_var = df.groupby('Genotype')['Scaled_Value'].std().sort_values(ascending=False)
    top_genos = geno_var.head(top_n).index.tolist()

    df_bg = df[~df['Genotype'].isin(top_genos)]
    df_fg = df[df['Genotype'].isin(top_genos)]

    fig = px.line(df_bg, x='Trait', y='Scaled_Value',
                  color='Genotype', line_group='Genotype', markers=False)
    fig.for_each_trace(lambda t: t.update(line_color='lightgray',
                                          marker_color='lightgray',
                                          showlegend=False))

    fig2 = px.line(df_fg, x='Trait', y='Scaled_Value',
                   color='Genotype', line_group='Genotype', markers=True)
    for trace in fig2.data:
        fig.add_trace(trace)

    fig.update_layout(
        title=f'{title_prefix} — {condition} (Top {top_n} Genotypes Highlighted)',
        xaxis_tickangle=-45,
        yaxis_title='Scaled Trait Value',
        template='plotly_white'
    )
    if out_png:
        fig.write_image(out_png.replace(".png", f"_{condition}.png"))
        print(f"Saved highlighted plot for {condition} to {out_png.replace('.png', f'_{condition}.png')}")
    else:
        fig.show()

def main():
    """
    CLI for generating line plots of scaled trait values across genotypes,
    with optional highlighting of the most variable ones.
    """
    p = argparse.ArgumentParser(description="Line plot of scaled trait values across genotypes.")
    p.add_argument('--input', required=True, help='Cleaned Excel input file')
    p.add_argument('--out', help='Path to save plot image (adds _HI/_LI suffixes)')
    p.add_argument('--top', type=int, help='Highlight top N most variable genotypes')
    p.add_argument('--scale', choices=['zscore', 'minmax'], default='zscore', help='Scaling method for traits')
    p.add_argument('--region', help='Region label in plot title')

    args = p.parse_args()

    df = pd.read_excel(args.input)
    df = normalize_condition_labels(df)
    df_long = prepare_fully_scaled_data(df, scale=args.scale)

    for cond in ['HI', 'LI']:
        if args.top:
            plot_highlight_genotypes(df_long, cond, args.top, title_prefix=args.region, out_png=args.out)
        else:
            plot_plain(df_long, cond, title_prefix=args.region, out_png=args.out)

if __name__ == '__main__':
    main()
