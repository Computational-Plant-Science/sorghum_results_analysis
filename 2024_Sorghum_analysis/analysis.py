import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler


def load_data(file_path):
    directory = "./2024_Sorghum_analysis/"
    df = pd.read_excel(directory + file_path)
    return df

def split_df(df):
    first_half = df.iloc[:,:11]
    second_half = df.iloc[:,12:].dropna()
    return first_half, second_half

def plot_normalized_traits(df, treat):
    title=f"Normalized Traits for {treat} (Top 10 Most Variable)"
    df_hi = df[df["Treat"] == treat]

    trait_columns = [col for col in df.columns if col not in ["file_name", "Treat", "Genotype", "Replicate"]]
    trait_columns = trait_columns[1:11]
    
    scaler = StandardScaler()
    df_hi_normalized = df_hi.copy()
    df_hi_normalized[trait_columns] = scaler.fit_transform(df_hi[trait_columns])

    top_variance_genotypes = df_hi_normalized.groupby("Genotype")[trait_columns].std().mean(axis=1).nlargest(10).index
    df_hi_filtered = df_hi_normalized[df_hi_normalized["Genotype"].isin(top_variance_genotypes)]

    df_melted = df_hi_filtered.melt(id_vars=["Genotype"], value_vars=trait_columns, var_name="Trait", value_name="Normalized Value")

    palette = sns.color_palette("tab20", n_colors=len(df_melted["Genotype"].unique()))

    plt.figure(figsize=(14, 8))
    sns.lineplot(
        data=df_melted, x="Trait", y="Normalized Value", hue="Genotype",
        marker="o", alpha=0.4, linewidth=1.5, palette=palette, ci=None
    )

    # Improve readability
    plt.title(title, fontsize=16, fontweight="bold")
    plt.xticks(rotation=60, ha="right", fontsize=12)
    plt.xlabel("Trait", fontsize=14)
    plt.ylabel("Normalized Value", fontsize=14)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Genotype", fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()

def main():
    all_samples = load_data("traits_all_samples.xlsx")
    traits_and_sorghums = load_data("traits_and_sorghums.xlsx")
    traits_by_genotype_and_averages = load_data("traits_by_genotype.xlsx")

    traits_by_genotype, traits_by_genotype_averages = split_df(traits_by_genotype_and_averages)

    plot_normalized_traits(traits_and_sorghums, "HI")
    plot_normalized_traits(traits_and_sorghums, "LI")
    
main()