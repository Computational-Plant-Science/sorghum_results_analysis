import pandas as pd
import plotly.express as px

def load_and_prepare_data(file_path):
    """
    
    """
    df = pd.read_excel(file_path)

    cols_to_drop = ['file_name', 'Unnamed: 0', 'Replicate', 'Plot_Number', 'Genotype', "Treat"]
    df_numeric = df.drop(columns=cols_to_drop, errors='ignore')

    return df_numeric

def plot_averages(file_path, type='Mean'):
    """
    This function reads an excel file and plots the averages of the remaining columns.
    """
    df = load_and_prepare_data(file_path)
    if type == 'Mean':
        df_avg = df.mean()
    elif type == 'Median':
        df_avg = df.median()
    df_avg = df_avg.reset_index()
    df_avg.columns = ['Trait', type]
    fig = px.bar(
        df_avg,
        x='Trait',
        y=type,
        title=f'{type} of Traits'
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def main():
    # file_path = 'trait_excels/traits_and_sorghums.xlsx'
    file_path = 'texas/combined_trait_results_texas_scaled_cleaned.xlsx'
    plot_averages(file_path, type='Mean')
    plot_averages(file_path, type='Median')

if __name__ == '__main__':
    main()