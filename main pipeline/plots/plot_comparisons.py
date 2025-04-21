import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math

def plot_traits_grid(df, traits=None, cols=2):
    """
    Plots each trait as a grouped bar chart in a grid layout.
    """
    df = df.copy()
    df = df.drop(columns=['Unnamed: 0'], errors='ignore')

    # Get traits to plot
    if traits is None:
        ignore_cols = {'Genotype', 'Condition'}
        traits = [col for col in df.columns if col not in ignore_cols and pd.api.types.is_numeric_dtype(df[col])]

    rows = math.ceil(len(traits) / cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[t.title() for t in traits])

    # Set consistent colors
    color_map = {'HI': '#636EFA', 'LI': '#EF553B'}  # Blue and red

    for idx, trait in enumerate(traits):
        row = idx // cols + 1
        col = idx % cols + 1
        df_avg = df.groupby(['Genotype', 'Condition'])[trait].mean().reset_index()

        for cond in ['HI', 'LI']:  # Maintain order and color
            cond_df = df_avg[df_avg['Condition'] == cond]
            fig.add_trace(
                go.Bar(
                    x=cond_df['Genotype'],
                    y=cond_df[trait],
                    name=cond,
                    marker_color=color_map[cond],
                    showlegend=(idx == 0)  # Show legend only once
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
    fig.show()


def main():
    file_path = "combined_trait_results_texas_scaled_cleaned.xlsx"
    df = pd.read_excel(file_path)

    plot_traits_grid(df, traits=None, cols=2)

if __name__ == '__main__':
    main()
