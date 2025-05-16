import argparse
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math

def plot_traits_grid(df, traits=None, cols=2, out_html=None):
    """
    Generates a grid of grouped bar charts comparing specified traits
    across genotypes and conditions (e.g., HI vs LI).

    Parameters:
    - df (pd.DataFrame): DataFrame containing trait data with 'Genotype' and 'Condition'.
    - traits (list): List of trait names to include. If None, all numeric traits are used.
    - cols (int): Number of columns in the grid layout.
    - out_html (str): Path to save the output image (HTML).
    """
    df = df.copy()
    df = df.drop(columns=['Unnamed: 0'], errors='ignore')

    if traits is None:
        ignore_cols = {'Genotype', 'Condition'}
        traits = [col for col in df.columns if col not in ignore_cols and pd.api.types.is_numeric_dtype(df[col])]
    else:
        traits = [t for t in traits if t in df.columns]

    rows = math.ceil(len(traits) / cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[t.title() for t in traits])

    color_map = {'HI': '#636EFA', 'LI': '#EF553B'}

    for idx, trait in enumerate(traits):
        row = idx // cols + 1
        col = idx % cols + 1
        df_avg = df.groupby(['Genotype', 'Condition'])[trait].mean().reset_index()

        for cond in ['HI', 'LI']:
            cond_df = df_avg[df_avg['Condition'] == cond]
            fig.add_trace(
                go.Bar(
                    x=cond_df['Genotype'],
                    y=cond_df[trait],
                    name=cond,
                    marker_color=color_map[cond],
                    showlegend=(idx == 0)
                ),
                row=row, col=col
            )

    fig.update_layout(
        height=300 * rows,
        title_text="Trait Comparison by Genotype and Treatment",
        barmode='group',
        template='plotly_white'
    )
    fig.update_xaxes(tickangle=-45)

    if out_html:
        fig.write_html(out_html)
        print(f"Saved grid plot to {out_html}")
    else:
        fig.show()


def compare_two_locations(df1, df2, traits=None, cols=2, out_html=None):
    """
    Places two trait‐grid plots side by side for location1 vs location2.
    """
    if traits is None:
        traits = [
            c for c in df1.select_dtypes(include='number').columns
            if c not in ('Genotype','Condition')
        ]

    n_traits = len(traits)
    rows = n_traits
    cols = 2

    titles = []
    for t in traits:
        titles += [f"Loc1: {t}", f"Loc2: {t}"]

    color_map = {'HI': 'red', 'LI': 'blue'}

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=titles,
        vertical_spacing=0.05,
        horizontal_spacing=0.1
    )

    for i, trait in enumerate(traits, start=1):
        d1 = df1.groupby(['Genotype','Condition'])[trait].mean().reset_index()
        for cond in sorted(d1['Condition'].unique()):
            sub = d1[d1['Condition']==cond]
            fig.add_trace(
                go.Bar(
                    x=sub['Genotype'],
                    y=sub[trait],
                    name=cond,
                    legendgroup=cond,
                    marker_color=color_map.get(cond, 'gray'),
                ),
                row=i, col=1
            )

        d2 = df2.groupby(['Genotype','Condition'])[trait].mean().reset_index()
        for cond in sorted(d2['Condition'].unique()):
            sub = d2[d2['Condition']==cond]
            fig.add_trace(
                go.Bar(
                    x=sub['Genotype'],
                    y=sub[trait],
                    name=cond,
                    legendgroup=cond,
                    showlegend=False,
                    marker_color=color_map.get(cond, 'gray'),
                ),
                row=i, col=2
            )

    fig.update_layout(
        height=300 * rows,
        width=800,
        barmode='group',
        title_text="Trait Comparison: Location 1 (left) vs Location 2 (right)",
        margin=dict(t=100),
    )

    fig.update_xaxes(tickangle=45, tickfont=dict(size=9))
    
    if out_html:
        fig.write_html(out_html)
    fig.show()


def main():
    p = argparse.ArgumentParser(description="Grid plot of traits by genotype and condition (1 or 2 locations)")
    p.add_argument('--inputs',nargs='+',required=True, help='One or two cleaned Excel input files')
    p.add_argument('--output', required=True, help='Path to save output image (HTML)')
    p.add_argument('--traits',nargs='+',help='List of traits to include (default: all numeric traits)')
    p.add_argument('--cols',type=int,default=2,help='Number of columns in the grid layout (per location)')
    args = p.parse_args()

    if len(args.inputs) == 1:
        df = pd.read_excel(args.inputs[0])
        plot_traits_grid(
            df,
            traits=args.traits,
            cols=args.cols,
            out_html=args.out
        )

    elif len(args.inputs) == 2:
        df1 = pd.read_excel(args.inputs[0])
        df2 = pd.read_excel(args.inputs[1])
        compare_two_locations(
            df1,
            df2,
            traits=args.traits,
            out_html=args.output
        )

    else:
        raise ValueError("You must supply one or two --inputs files only")

if __name__ == '__main__':
    main()
