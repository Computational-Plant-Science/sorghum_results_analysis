import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler

file_path_hi = "./average_trait_values/traits_and_sorghums_HI_avg.xlsx"
file_path_li = "./average_trait_values/traits_and_sorghums_LI_avg.xlsx"

df_hi = pd.read_excel(file_path_hi)
df_li = pd.read_excel(file_path_li)

non_numeric_columns = df_hi.select_dtypes(include=['object']).columns
genotype_column = 'Genotype' if 'Genotype' in non_numeric_columns else non_numeric_columns[0]

df_hi_genotypes = df_hi[genotype_column]
df_li_genotypes = df_li[genotype_column]

df_hi = df_hi.drop("Plot_Number", axis=1)
df_li = df_li.drop("Plot_Number", axis=1)

df_hi_numeric = df_hi.drop(columns=non_numeric_columns, errors='ignore')
df_li_numeric = df_li.drop(columns=non_numeric_columns, errors='ignore')

scaler = StandardScaler()
df_hi_normalized = pd.DataFrame(scaler.fit_transform(df_hi_numeric), columns=df_hi_numeric.columns)
df_li_normalized = pd.DataFrame(scaler.fit_transform(df_li_numeric), columns=df_li_numeric.columns)

df_hi_normalized['Genotype'] = df_hi_genotypes
df_li_normalized['Genotype'] = df_li_genotypes

df_hi_melted = df_hi_normalized.melt(id_vars='Genotype', var_name='Trait', value_name='Normalized Value')
df_li_melted = df_li_normalized.melt(id_vars='Genotype', var_name='Trait', value_name='Normalized Value')

fig_hi = px.line(
    df_hi_melted,
    x='Trait',
    y='Normalized Value',
    color='Genotype',
    title='Normalized Traits for HI',
    markers=True
)
fig_hi.update_layout(xaxis_tickangle=-45)
fig_hi.show()

fig_li = px.line(
    df_li_melted,
    x='Trait',
    y='Normalized Value',
    color='Genotype',
    title='Normalized Traits for LI',
    markers=True
)
fig_li.update_layout(xaxis_tickangle=-45)
fig_li.show()