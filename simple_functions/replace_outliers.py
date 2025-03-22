import pandas as pd

def load_df(file_name):
    """
    Loads a dataframe from a file name
    """
    df = pd.read_excel(file_name)
    df = df.drop('Unnamed: 0', axis=1)
    return df

def replace_outliers(df, threshold=1.5):
    df_cleaned = df.copy()
    numeric_cols = df.select_dtypes(include='number').columns

    for col in numeric_cols:
        col_mean = df_cleaned[col].mean()

        col_std = df_cleaned[col].std()
        lower_bound = col_mean - threshold * col_std
        upper_bound = col_mean + threshold * col_std

        df_cleaned[col] = df_cleaned[col].apply(lambda x: col_mean if x < lower_bound or x > upper_bound else x)

    return df_cleaned

def main():
    file_name = "./texas/combined_trait_results_texas_scaled.xlsx"
    df = load_df(file_name)
    df_replaced = replace_outliers(df)
    df_replaced.to_excel("./combined_trait_results_texas_scaled_cleaned.xlsx")

if __name__ == '__main__':
    main()