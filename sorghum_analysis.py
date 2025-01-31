import pandas as pd
import glob


# df = pd.read_excel("./trait_results/101_1_cleaned_aligned_trait.xlsx")
# print(df.get("root system diameter max"))

def combine_excels():
    l = [pd.read_excel(filename) for filename in glob.glob("./trait_results/*.xlsx")]

    df = pd.concat(l, axis=0)

    file_name = "combined_trait_results.xlsx"
    df.to_excel(file_name)
    print("Traits loaded into {file_name} successfully")


def main():
    combine_excels()

main()