import argparse
import pandas as pd
import plotly.express as px

def load_and_prepare_data(file_path):
    """
    Loads an Excel file and filters out non-trait columns to retain only numeric trait data.

    Parameters:
    - file_path (str): Path to the Excel file.

    Returns:
    - pd.DataFrame: DataFrame containing only numeric trait columns.
    """
    df = pd.read_excel(file_path)
    cols_to_drop = ['file_name', 'Unnamed: 0', 'Replicate', 'Plot_Number', 'Genotype', 'plot_number', 'filename', 'Condition']
    df_numeric = df.drop(columns=cols_to_drop, errors='ignore')
    return df_numeric

def plot_averages(df, stat_type='Mean', show_error=True, out_html=None):
    """
    Generates a bar plot showing either the mean or median of traits.
    Optionally includes standard error bars if plotting the mean.

    Parameters:
    - df (pd.DataFrame): DataFrame containing numeric trait data.
    - stat_type (str): 'Mean' or 'Median' to indicate which statistic to plot.
    - show_error (bool): Whether to include standard error bars (valid only for Mean).
    - out_html (str): Saves the plot to a HTML file.
    """
    if stat_type == 'Mean':
        df_avg = df.mean()
    elif stat_type == 'Median':
        df_avg = df.median()
    else:
        raise ValueError("Type must be 'Mean' or 'Median'.")

    df_avg = df_avg.reset_index()
    df_avg.columns = ['Trait', stat_type]

    if show_error and stat_type == 'Mean':
        se = df.std() / (len(df) ** 0.5)
        df_se = se.reset_index()
        df_se.columns = ['Trait', 'SE']
        df_plot = pd.merge(df_avg, df_se, on='Trait')

        fig = px.bar(
            df_plot,
            x='Trait',
            y=stat_type,
            error_y='SE',
            title=f'{stat_type} of Traits with Standard Error'
        )
    else:
        fig = px.bar(
            df_avg,
            x='Trait',
            y=stat_type,
            title=f'{stat_type} of Traits'
        )

    fig.update_layout(xaxis_tickangle=-45)

    if out_html:
        fig.write_html(out_html)
        print(f"Saved plot to {out_html}")
    else:
        fig.show()

def main():
    """
    Command-line interface for plotting the mean or median of traits from an Excel file.
    """
    parser = argparse.ArgumentParser(description="Plot mean or median of numeric traits.")
    parser.add_argument('--input', default="/srv/data/cleaned.xlsx", help='Cleaned Excel file')
    parser.add_argument('--output', default="/srv/data/mean_median.html", help='Output HTML file')
    parser.add_argument('--type', choices=['Mean', 'Median'], default='Mean', help="Statistic to plot")
    parser.add_argument('--hide-error', action='store_true', help="Hide standard error bars (only affects Mean)")

    args = parser.parse_args()
    df = load_and_prepare_data(args.input)

    plot_averages(
        df,
        stat_type=args.type,
        show_error=not args.hide_error,
        out_html=args.output
    )

if __name__ == '__main__':
    main()
