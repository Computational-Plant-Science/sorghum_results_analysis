import pandas as pd
import plotly.express as px

def compute_trait_by_region(file_path, trait, genotype, region_label="Region", sheet_name="Sheet1"):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df[df['Genotype'] == genotype]
    df = df[['Condition', trait]].copy()
    df[trait] = pd.to_numeric(df[trait], errors='coerce')
    df = df.dropna(subset=[trait])
    grouped = df.groupby('Condition', as_index=False).mean()
    grouped['Region'] = region_label
    grouped['Genotype'] = genotype
    return grouped

def compute_all_traits_by_region(file_path, genotype, region_label="Region", sheet_name="Sheet1"):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df[df['Genotype'] == genotype]
    
    # Keep only numeric columns and required metadata
    non_traits = ['Condition', 'Genotype', 'Region', 'plot_number', 'Unnamed: 0']
    trait_cols = df.select_dtypes(include='number').columns.difference(non_traits)

    df[trait_cols] = df[trait_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=trait_cols, how='all')

    grouped = df.groupby('Condition', as_index=False)[trait_cols].mean()
    grouped['Region'] = region_label
    grouped['Genotype'] = genotype
    return grouped

def plot_raw_trait(df, trait, genotype):
    fig = px.line(
        df,
        x='Condition',
        y=trait,
        color='Region',
        markers=True,
        title=f'{trait.title()} by Region for Genotype {genotype}',
        labels={'Condition': 'Condition', trait: trait.title()}
    )
    fig.update_layout(template='plotly_white')
    fig.show()

def plot_all_traits(df, genotype):
    # Convert to long format
    val_cols = df.select_dtypes(include='number').columns.difference(['Region'])
    long_df = df.melt(
        id_vars=['Condition', 'Region', 'Genotype'],
        value_vars=val_cols,
        var_name='Trait',
        value_name='Value'
    )

    fig = px.line(
        long_df,
        x='Condition',
        y='Value',
        color='Region',
        facet_col='Trait',
        facet_col_wrap=3,
        markers=True,
        title=f'All Traits by Region for Genotype {genotype}',
        labels={'Condition': 'Condition', 'Value': 'Value'}
    )
    fig.for_each_yaxis(lambda y: y.update(matches=None))
    fig.update_layout(template='plotly_white')
    fig.show()

def main():
    trait = ""
    genotype = "SC56" 

    file_az = "combined_trait_results_arizona_scaled_cleaned.xlsx"
    file_tx = "combined_trait_results_texas_scaled_cleaned.xlsx"

    if not genotype:
        raise ValueError("Please specify a genotype.")

    if trait:
        df_az = compute_trait_by_region(file_az, trait, genotype, region_label="Arizona")
        df_tx = compute_trait_by_region(file_tx, trait, genotype, region_label="Texas")
        df_combined = pd.concat([df_az, df_tx], ignore_index=True)
        plot_raw_trait(df_combined, trait, genotype)
    else:
        df_az_all = compute_all_traits_by_region(file_az, genotype, region_label="Arizona")
        df_tx_all = compute_all_traits_by_region(file_tx, genotype, region_label="Texas")
        df_combined = pd.concat([df_az_all, df_tx_all], ignore_index=True)
        plot_all_traits(df_combined, genotype)

if __name__ == '__main__':
    main()
