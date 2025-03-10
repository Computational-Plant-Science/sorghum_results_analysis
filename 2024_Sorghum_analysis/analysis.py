import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def load_data(file_path):
    directory = "./2024_Sorghum_analysis/"
    df = pd.read_excel(directory + file_path)
    return df

def split_df(df):
    first_half = df.iloc[:,:11]
    second_half = df.iloc[:,12:].dropna()
    return first_half, second_half

def plot_normalized_traits_top_ten(df, treat):
    title=f"Normalized Traits for {treat} (Top 10 Most Variable)"
    df_hi = df[df["Treat"] == treat]

    trait_columns, df_hi_normalized = normalize_data(df_hi)

    top_variance_genotypes = df_hi_normalized.groupby("Genotype")[trait_columns].std().mean(axis=1).nlargest(10).index
    df_hi_filtered = df_hi_normalized[df_hi_normalized["Genotype"].isin(top_variance_genotypes)]

    df_melted = df_hi_filtered.melt(id_vars=["Genotype"], value_vars=trait_columns, var_name="Trait", value_name="Normalized Value")

    palette = sns.color_palette("tab20", n_colors=len(df_melted["Genotype"].unique()))

    plt.figure(figsize=(14, 8))
    sns.lineplot(
        data=df_melted, x="Trait", y="Normalized Value", hue="Genotype",
        marker="o", alpha=0.4, linewidth=1.5, palette=palette, ci=None
    )

    plt.title(title, fontsize=16, fontweight="bold")
    plt.xticks(rotation=60, ha="right", fontsize=12)
    plt.xlabel("Trait", fontsize=14)
    plt.ylabel("Normalized Value", fontsize=14)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Genotype", fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()

def normalize_data(df):
    trait_columns = [col for col in df.columns if col not in ["file_name", "Treat", "Genotype", "Replicate"]]
    trait_columns = trait_columns[1:11]
    
    scaler = StandardScaler()
    df_hi_normalized = df.copy()
    df_hi_normalized[trait_columns] = scaler.fit_transform(df[trait_columns])
    return trait_columns,df_hi_normalized

def plot_all_traits_with_error(df, mean_or_median):
    plt.figure(figsize=(20, 8))

    trait_columns = [col for col in df.columns if col not in ["file_name", "Treat", "Genotype", "Replicate"]]
    trait_columns = trait_columns[1:11]
    
    summary = df.groupby("Treat")[trait_columns].agg([mean_or_median, "sem"]).stack(level=0).reset_index()
    summary.columns = ["Treatment", "Trait", mean_or_median, "SE"]

    ax = sns.barplot(
        data=summary, 
        x="Trait", 
        y="{mean_or_median}", 
        hue="Treatment", 
        palette="coolwarm", 
        capsize=0.2
    )

    for p in ax.patches:
        x = p.get_x() + p.get_width() / 2
        y = p.get_height()
        
        if y > 0.1:
            ax.annotate(
                f"{y:.2f}", 
                (x, y), 
                ha="center", 
                fontsize=10, 
                xytext=(0, 5), 
                textcoords="offset points"
            )

    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Trait", fontsize=12)
    plt.ylabel("{mean_or_median} Value", fontsize=12)
    plt.title("Comparison of All Traits by Treatment (HI vs. LI)", fontsize=14)
    plt.legend(title="Treatment", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    plt.subplots_adjust(left=0.06, right=0.87, bottom=0.24, top=0.9)
    plt.show()

def plot_genotype_averages(df):

    plt.figure(figsize=(16, 8))

    df = strip_all_columns(df)
    
    trait_columns = [col for col in df.columns if col not in ["file_name"]]

    scaler = StandardScaler()
    df_normalized = df.copy()
    df_normalized[trait_columns] = scaler.fit_transform(df[trait_columns])

    df_normalized["variability"] = df_normalized[trait_columns].std(axis=1)
    
    df_top = df_normalized.nlargest(10, "variability")

    for index, row in df_normalized.iterrows():
        plt.plot(trait_columns, row[trait_columns], 
                 marker="o", alpha=0.1, color="gray", linewidth=0.5)

    for index, row in df_top.iterrows():
        plt.plot(trait_columns, row[trait_columns], 
                 marker="o", label=row["file_name"], alpha=0.8, linewidth=2)

    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.xlabel("Trait", fontsize=12)
    plt.ylabel("Normalized Value", fontsize=12)
    plt.title("Top 10 Most Variable Genotypes (Normalized)", fontsize=14)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.yscale("linear")

    if len(df["file_name"].unique()) > 15:
        plt.legend(title="Genotype", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8, ncol=2)
    else:
        plt.legend(title="Genotype", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()

def strip_all_columns(df):
    df.columns = [col.replace('.1', '') if col.endswith('.1') else col for col in df.columns]
    return df

def plot_normalized_traits_clusters(df, treat, n_clusters):
    title = f"Normalized Traits for {treat} (K-Means Clustering, {n_clusters} Clusters)"
    
    # Filter by treatment
    df_treat = df[df["Treat"] == treat]

    trait_columns, df_normalized = normalize_data(df)

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df_normalized["Cluster"] = kmeans.fit_predict(df_normalized[trait_columns])

    # Melt the DataFrame for plotting
    df_melted = df_normalized.melt(
        id_vars=["Genotype", "Cluster"], 
        value_vars=trait_columns, 
        var_name="Trait", 
        value_name="Normalized Value"
    )

    # Define a color palette for the clusters
    palette = sns.color_palette("tab10", n_colors=n_clusters)

    plt.figure(figsize=(14, 8))

    # Plot each line with the color corresponding to its cluster
    sns.lineplot(
        data=df_melted, 
        x="Trait", 
        y="Normalized Value", 
        hue="Cluster",
        marker="o", 
        alpha=0.6, 
        linewidth=1.5, 
        palette=palette, 
        ci=None
    )

    plt.title(title, fontsize=16, fontweight="bold")
    plt.xticks(rotation=60, ha="right", fontsize=12)
    plt.xlabel("Trait", fontsize=14)
    plt.ylabel("Normalized Value", fontsize=14)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Cluster", fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()

def plot_elbow_method(df, max_clusters=10):
    trait_columns, blank = normalize_data(df)
    
    sse = []
    for k in range(1, max_clusters+1):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(df[trait_columns])
        sse.append(kmeans.inertia_)
    
    plt.figure(figsize=(8, 6))
    plt.plot(range(1, max_clusters+1), sse, marker="o")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Sum of Squared Errors (SSE)")
    plt.title("Elbow Method for Determining Optimal K")
    plt.grid(True)
    plt.show()

def plot_normalized_traits_by_cluster(df, n_clusters=5):
    plt.figure(figsize=(16, 8))

    df = strip_all_columns(df)

    # Select the trait columns (exclude 'file_name' or other non-trait columns)
    trait_columns = [col for col in df.columns if col not in ["file_name", "root system volume"]]

    # Normalize the data
    scaler = StandardScaler()
    df_normalized = df.copy()
    df_normalized[trait_columns] = scaler.fit_transform(df[trait_columns])

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df_normalized["Cluster"] = kmeans.fit_predict(df_normalized[trait_columns])

    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    palette = sns.color_palette("tab10", n_clusters)

    for cluster_index, center in enumerate(cluster_centers):
        plt.plot(trait_columns, center, 
                 marker="o", label=f"Cluster {cluster_index}", 
                 alpha=0.8, linewidth=2.5, color=palette[cluster_index])

    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.xlabel("Trait", fontsize=12)
    plt.ylabel("Normalized Value", fontsize=12)
    plt.title(f"Normalized Trait Measurements by K-Means Clustering ({n_clusters} Clusters)", fontsize=14)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    if "Cluster" in df_normalized.columns and len(df_normalized["Cluster"].unique()) > 10:
        plt.legend(title="Cluster", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8, ncol=2)
    else:
        plt.legend(title="Cluster", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()
    
def main():
    all_samples = load_data("traits_all_samples.xlsx")
    traits_and_sorghums = load_data("traits_and_sorghums.xlsx")
    traits_by_genotype_and_averages = load_data("traits_by_genotype.xlsx")
    traits_by_genotype, traits_by_genotype_averages = split_df(traits_by_genotype_and_averages)

    
main()