import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler

def load_and_prepare_data(file_path):
    """
    Loads an Excel file, identifies the genotype column, and separates numeric and non-numeric columns.
    """
    df = pd.read_excel(file_path)

    non_numeric_columns = df.select_dtypes(include=['object']).columns
    genotype_column = 'Genotype' if 'Genotype' in non_numeric_columns else non_numeric_columns[0]
    genotype_values = df[genotype_column]

    df = df.drop(columns=['Plot_Number', 'Unnamed: 0'], errors='ignore')
    df_numeric = df.drop(columns=non_numeric_columns, errors='ignore')

    scaler = StandardScaler()
    df_normalized = pd.DataFrame(scaler.fit_transform(df_numeric), columns=df_numeric.columns)

    df_normalized['Genotype'] = genotype_values

    return df_normalized

def plot_normalized_traits(df_normalized, treat_label):
    """
    Plots normalized trait values per genotype using line plots.
    """
    df_melted = df_normalized.melt(id_vars='Genotype', var_name='Trait', value_name='Normalized Value')

    fig = px.line(
        df_melted,
        x='Trait',
        y='Normalized Value',
        color='Genotype',
        title=f'Normalized Traits for {treat_label}',
        markers=True
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def main():
    file_path_hi = "trait_excels/average_trait_values/traits_and_sorghums_HI_avg.xlsx"
    file_path_li = "trait_excels/average_trait_values/traits_and_sorghums_LI_avg.xlsx"

    df_hi_normalized = load_and_prepare_data(file_path_hi)
    df_li_normalized = load_and_prepare_data(file_path_li)

    plot_normalized_traits(df_hi_normalized, treat_label='HI')
    plot_normalized_traits(df_li_normalized, treat_label='LI')

if __name__ == '__main__':
    main()
