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


def compute_trait_by_region(file_path, trait, genotype, region_label="Region", sheet_name="Sheet1"):
    """
    Extracts and averages a single trait by condition for a specific genotype and region from an Excel file.

    Parameters:
    - file_path (str): Path to the Excel file.
    - trait (str): Name of the trait to extract.
    - genotype (str): Genotype to filter for.
    - region_label (str): Label identifying the region (e.g., 'Arizona', 'Texas').
    - sheet_name (str): Sheet name in the Excel file.

    Returns:
    - pd.DataFrame: DataFrame with average trait values per condition, with region and genotype included.
    """
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
    """
    Extracts and averages all numeric traits by condition for a specific genotype and region.

    Parameters:
    - file_path (str): Path to the Excel file.
    - genotype (str): Genotype to filter for.
    - region_label (str): Label identifying the region.
    - sheet_name (str): Sheet name in the Excel file.

    Returns:
    - pd.DataFrame: DataFrame with average values of all traits per condition.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df[df['Genotype'] == genotype]

    non_traits = ['Condition', 'Genotype', 'Region', 'plot_number', 'Unnamed: 0']
    trait_cols = df.select_dtypes(include='number').columns.difference(non_traits)

    df[trait_cols] = df[trait_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=trait_cols, how='all')

    grouped = df.groupby('Condition', as_index=False)[trait_cols].mean()
    grouped['Region'] = region_label
    grouped['Genotype'] = genotype
    return grouped

def plot_raw_trait(df, trait, genotype):
    """
    Plots a line chart of a single trait across conditions, colored by region.

    Parameters:
    - df (pd.DataFrame): Combined DataFrame containing trait values.
    - trait (str): Trait to plot.
    - genotype (str): Genotype label to display in the title.
    """
    fig = px.line(
        df,
        x='Condition',
        y=trait,
        color='Region',
        markers=True,
        title=f'{trait.title()} by Region for Genotype {genotype}',
        labels={'Condition': 'Condition', trait: trait.title()}
    )
    fig.update_xaxes(showticklabels=True, tickangle=45)
    fig.update_layout(template='plotly_white')
    fig.show()

def plot_all_traits(df, genotype):
    """
    Plots all traits in a faceted line chart, one subplot per trait.

    Parameters:
    - df (pd.DataFrame): Combined DataFrame of all traits.
    - genotype (str): Genotype label to display in the title.
    """
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
    fig.update_xaxes(showticklabels=True, tickangle=45)
    fig.for_each_yaxis(lambda y: y.update(matches=None))
    fig.update_layout(template='plotly_white')
    fig.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--genotype", required=True, help="Genotype name")
    parser.add_argument("--trait", help="Single trait to plot")
    parser.add_argument("--file1", required=True, help="Excel file for region 1")
    parser.add_argument("--file2", required=True, help="Excel file for region 2")
    parser.add_argument("--region1", required=True, help="Label for region 1")
    parser.add_argument("--region2", required=True, help="Label for region 2")
    args = parser.parse_args()
    if args.trait:
        df1 = normalize_condition_labels(
            compute_trait_by_region(args.file1, args.trait, args.genotype, region_label=args.region1)
        )
        df2 = normalize_condition_labels(
            compute_trait_by_region(args.file2, args.trait, args.genotype, region_label=args.region2)
        )
        df_combined = pd.concat([df1, df2], ignore_index=True)
        plot_raw_trait(df_combined, args.trait, args.genotype)
    else:
        df1_all = normalize_condition_labels(
            compute_all_traits_by_region(args.file1, args.genotype, region_label=args.region1)
        )
        df2_all = normalize_condition_labels(
            compute_all_traits_by_region(args.file2, args.genotype, region_label=args.region2)
        )
        df_combined = pd.concat([df1_all, df2_all], ignore_index=True)
        plot_all_traits(df_combined, args.genotype)

if __name__ == '__main__':
    main()