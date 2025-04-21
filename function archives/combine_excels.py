import pandas as pd
import glob


def combine_excels():
    """
    Grabs all files in ./trait_results and combines them into one excel sheet.
    """
    l = [pd.read_excel(filename) for filename in glob.glob("./trait_excels/trait_results/*.xlsx")]
    print(l)

    df = pd.concat(l, axis=0)
    df = df.drop('Unnamed: 0', axis=1)

    file_name = "combined_trait_results.xlsx"
    df.to_excel(file_name)
    
    print(f"Traits loaded into {file_name} successfully")
    return df

def parse_genotype_and_treatments(df):
    """
    Extracts plot number from file names, and maps them with the sorghum treatments.
    """
    df['Plot_Number'] = df['file_name'].str.extract(r"(\d+)_").astype(int)

    sorghum_treatments = pd.read_excel('./genotype_plot_number/sorghum2024_sample_info_wide.xlsx')    
    sorghum_treatments = pd.melt(frame=sorghum_treatments, id_vars=['Treat', 'Genotype'], value_vars=['Rep1', 'Rep2', 'Rep3'], var_name='Replicate', value_name='Plot_Number')

    df = df.merge(sorghum_treatments, on="Plot_Number", how="left")
    file_name = "traits_and_sorghums.xlsx"
    df.to_excel(file_name)


def main():
    df = combine_excels()
    parse_genotype_and_treatments(df)

main()