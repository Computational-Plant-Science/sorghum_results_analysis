import pandas as pd

def load_df(file_name):
    """
    Loads a dataframe from a file name
    """
    df = pd.read_excel(file_name)
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)
    if 'Plot_Number' in df.columns:
        df = df.drop('Plot_Number', axis=1)
    return df

def calculate_averages(df):
    """
    Gets averages of dataframe by genotype
    """
    df_averages = df.groupby('Genotype', as_index=False).mean(numeric_only=True)
    return df_averages

def split_df(df):
    """
    Splits the dataframe by inputs into two separate dataframes.
    """
    df_hi = df[df["Treat"] == 'HI']
    df_li = df[df["Treat"] == 'LI']
    return df_hi, df_li

def main():
    df = load_df("trait_excels/traits_and_sorghums.xlsx")
    df_hi, df_li = split_df(df)

    df_hi.to_excel("traits_and_sorghums_HI.xlsx")
    df_li.to_excel("traits_and_sorghums_LI.xlsx")

    df_hi = calculate_averages(df_hi)
    df_li = calculate_averages(df_li)
    # df_averages = calculate_averages(df)

    df_hi.to_excel("traits_and_sorghums_HI_avg.xlsx")
    df_li.to_excel("traits_and_sorghums_LI_avg.xlsx")
    # df_averages.to_excel("traits_and_sorghums_avg.xlsx")

main()