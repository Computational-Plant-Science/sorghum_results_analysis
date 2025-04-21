import pandas as pd
import plotly.express as px

def load_and_prepare_data(file_path):
    """
    
    """
    df = pd.read_excel(file_path)

    cols_to_drop = ['file_name', 'Unnamed: 0', 'Replicate', 'Plot_Number', 'Genotype', 'plot_number', 'filename','Condition']
    df_numeric = df.drop(columns=cols_to_drop, errors='ignore')

    return df_numeric

def plot_averages(file_path, type='Mean', show_error=True):
    """
    This function reads an Excel file and plots either the mean or median
    of each numeric trait, with optional standard error bars.
    """
    df = load_and_prepare_data(file_path)
    
    if type == 'Mean':
        df_avg = df.mean()
    elif type == 'Median':
        df_avg = df.median()
    else:
        raise ValueError("Type must be 'Mean' or 'Median'.")

    df_avg = df_avg.reset_index()
    df_avg.columns = ['Trait', type]

    if show_error and type == 'Mean':
        standard_error = df.std() / (len(df) ** 0.5)
        standard_error = standard_error.reset_index()
        standard_error.columns = ['Trait', 'SE']
        df_plot = pd.merge(df_avg, standard_error, on='Trait')

        fig = px.bar(
            df_plot,
            x='Trait',
            y=type,
            error_y='SE',
            title=f'{type} of Traits with Standard Error'
        )
    else:
        fig = px.bar(
            df_avg,
            x='Trait',
            y=type,
            title=f'{type} of Traits'
        )

    fig.update_layout(xaxis_tickangle=-45)
    fig.show()


def main():
    file_path = "combined_trait_results_arizona_scaled_cleaned.xlsx"
    plot_averages(file_path, type='Mean', show_error=True)
    # plot_averages(file_path, type='Median', show_error=True)
    # plot_averages(file_path, type='Mean', show_error=False)
    # plot_averages(file_path, type='Median', show_error=False)

if __name__ == '__main__':
    main()