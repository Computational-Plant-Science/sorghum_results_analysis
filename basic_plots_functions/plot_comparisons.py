import pandas as pd
import numpy as np
import plotly.express as px

def plot(df, trait):
    cols_to_drop = ['file_name', 'Unnamed: 0', 'Replicate', 'Plot_Number']
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
    
    df = df_numeric[['Genotype', trait, 'Treat']]
    return df

def plot_stats(stats_df,trait):
    fig = px.bar(
            stats_df,
            x='Genotype',
            y=trait,
            color='Treat',
            barmode='group',
            title=f'Comparison between {trait}'
        )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def main():

    df_hi = pd.read_excel("./average_trait_values/traits_and_sorghums_HI_avg.xlsx")
    df_li = pd.read_excel("./average_trait_values/traits_and_sorghums_LI_avg.xlsx")
    df_hi["Treat"] = 'HI'
    df_li["Treat"] = 'LI'

    trait = 'root system bushiness'
    stats_hi = plot(df_hi, trait)
    stats_li = plot(df_li, trait)

    df_combined = pd.concat([stats_hi, stats_li], ignore_index=True)

    plot_stats(df_combined,trait)

if __name__ == '__main__':
    main()