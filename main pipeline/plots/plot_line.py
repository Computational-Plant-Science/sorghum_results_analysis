import pandas as pd
import plotly.express as px

def prepare_fully_scaled_data(file_path, scale='zscore'):
    df = pd.read_excel(file_path)
    df = df.drop(columns=['Unnamed: 0', 'plot_number'], errors='ignore')

    # trait columns (already 1 row per Genotype+Condition)
    trait_cols = df.select_dtypes(include='number').columns.tolist()

    # scale each trait
    if scale == 'zscore':
        df[trait_cols] = df[trait_cols].apply(lambda x: (x - x.mean()) / x.std())
    elif scale == 'minmax':
        df[trait_cols] = df[trait_cols].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    else:
        raise ValueError("scale must be 'zscore' or 'minmax'")

    # melt to long
    df_long = df.melt(
        id_vars=['Genotype', 'Condition'],
        var_name='Trait',
        value_name='Scaled_Value'
    )
    return df_long



def plot_plain(df_long, condition, title_prefix=""):
    df = df_long[df_long['Condition']==condition]
    fig = px.line(
        df, x='Trait', y='Scaled_Value',
        color='Genotype', line_group='Genotype',
        markers=True,
        title=f'{title_prefix} — {condition}',
        labels={'Scaled_Value':'Scaled Trait Value'}
    )
    fig.update_layout(xaxis_tickangle=-45, template='plotly_white')
    fig.show()

def plot_highlight_genotypes(df_long, condition, top_n, title_prefix=""):
    df = df_long[df_long['Condition']==condition]

    # 1) compute each genotype's overall variability
    geno_var = df.groupby('Genotype')['Scaled_Value']\
                 .std()\
                 .sort_values(ascending=False)
    top_genos = geno_var.head(top_n).index.tolist()

    # 2) split into background vs highlight
    df_bg = df[~df['Genotype'].isin(top_genos)]
    df_fg = df[df['Genotype'].isin(top_genos)]

    # 3a) plot the background in gray
    fig = px.line(
        df_bg, x='Trait', y='Scaled_Value',
        color='Genotype', line_group='Genotype',
        markers=False
    )
    fig.for_each_trace(lambda t: t.update(line_color='lightgray',
                                          marker_color='lightgray',
                                          showlegend=False))

    # 3b) overlay the highlighted genotypes in color + markers
    fig2 = px.line(
        df_fg, x='Trait', y='Scaled_Value',
        color='Genotype', line_group='Genotype',
        markers=True
    )
    for trace in fig2.data:
        fig.add_trace(trace)

    # 4) finalize
    fig.update_layout(
        title=f'{title_prefix} — {condition} (Top {top_n} Genotypes Highlighted)',
        xaxis_tickangle=-45,
        yaxis_title='Scaled Trait Value',
        template='plotly_white'
    )
    fig.show()

def main(top_n=None):
    fp = "combined_trait_results_texas_scaled_cleaned.xlsx"
    df_long = prepare_fully_scaled_data(fp, scale='zscore')

    for cond in ['HI','LI']:
        if top_n is None:
            plot_plain(df_long, cond, title_prefix='Texas')
        else:
            plot_highlight_genotypes(df_long, cond, top_n, title_prefix='Texas')

if __name__=='__main__':
    # main()
    main(top_n=5)
