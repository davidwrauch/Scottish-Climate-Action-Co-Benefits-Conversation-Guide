# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 15:25:25 2026

@author: RauchD
"""

# %%
# imports
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import spearmanr


# %%
# set working folder
# change this if your files are somewhere else
os.chdir(r"C:\data exercises\Edinburgh")

# make pandas print regular numbers instead of scientific notation
pd.options.display.float_format = "{:,.6f}".format


# %%
# load main data
climate_action_data = pd.read_excel("Edinburgh climate change comp Level_1.xlsx")

print(climate_action_data.head())
print(climate_action_data.columns.tolist())


# %%
# split Scotland vs England
# looks like Scottish small areas start with S and English ones with E
SC_climate_action_data = climate_action_data[
    climate_action_data["small_area"].astype(str).str.contains("S", na=False)
].copy()

EN_climate_action_data = climate_action_data[
    climate_action_data["small_area"].astype(str).str.contains("E", na=False)
].copy()

print(SC_climate_action_data.dtypes)
print(SC_climate_action_data.shape)
print(EN_climate_action_data.shape)


# %%
# load lookup files
geo_lookups = pd.read_excel("lookups.xlsx")

SIMD2020 = (
    pd.read_excel("SIMD Scotland 2020.xlsm")
    .assign(small_area=lambda df: df["DZ11CD"])
    .drop(columns=["DZ11CD"])
)

English_IMD2025 = (
   pd.read_excel("IMD England 2025_clean.xlsx")
    .assign(small_area=lambda df: df["LSOA Code"])
    .drop(columns=["LSOA Code"])
)

print(English_IMD2025.columns.tolist())


# %%
# join Scotland data
sc_join = (
    SC_climate_action_data
    .merge(SIMD2020, on="small_area", how="left")
    .merge(geo_lookups, on="small_area", how="left")
)

# qcut is the closest thing to ntile here
# labels=False gives 0-based bins, so add 1 to get 1-5 / 1-10
sc_join["simd_quintile"] = pd.qcut(
    sc_join["IMD20"],
    q=5,
    labels=False,
    duplicates="drop"
) + 1

sc_join["simd_decile"] = pd.qcut(
    sc_join["IMD20"],
    q=10,
    labels=False,
    duplicates="drop"
) + 1

print(sc_join.head())


# %%
# quick checks on negative total co-benefit values
num_negative_sum_sc = (sc_join["sum"] < 0).sum()
num_total_sc = len(sc_join)

print("Scottish neighborhoods with negative total co-benefit:", num_negative_sum_sc)
print("Total Scottish neighborhoods:", num_total_sc)
print("Share negative:", num_negative_sum_sc / num_total_sc)

# should be around that 1.5% you noted in R


# %%
# save joined Scotland file
sc_join.to_csv("sc_join.csv", index=False)


# %%
# join England data
en_join = (
    EN_climate_action_data
    .merge(English_IMD2025, on="small_area", how="left")
    .merge(geo_lookups, on="small_area", how="left")
)

en_join["imd_quintile"] = pd.qcut(
    en_join["LSOA IMD Ranking"],
    q=5,
    labels=False,
    duplicates="drop"
) + 1

print(en_join.head())


# %%
# helper for spearman correlation
def spearman_df(df, x_col, y_cols):
    rows = []
    for y_col in y_cols:
        tmp = df[[x_col, y_col]].dropna()
        corr, pval = spearmanr(tmp[x_col], tmp[y_col])
        rows.append({
            "x": x_col,
            "y": y_col,
            "spearman_corr": corr,
            "p_value": pval,
            "n": len(tmp)
        })
    return pd.DataFrame(rows)


# %%
# Scotland overall correlation: deprivation rank vs total co-benefit
sc_cor_df = spearman_df(sc_join, "IMD20", ["sum"])
print(sc_cor_df)

plt.figure(figsize=(8, 6))
sns.scatterplot(data=sc_join, x="IMD20", y="sum", alpha=0.3)
sns.regplot(
    data=sc_join,
    x="IMD20",
    y="sum",
    lowess=True,
    scatter=False,
    line_kws={"color": "red"}
)
plt.xlabel("SIMD Rank (1 = most deprived)")
plt.ylabel("Total Co-benefit")
plt.title("Relationship Between Deprivation and Total Co-benefits")
plt.show()


# %%
# Scotland using deciles instead
sc_cor_df_decile = spearman_df(sc_join, "simd_decile", ["sum"])
print(sc_cor_df_decile)

plt.figure(figsize=(8, 6))
sns.scatterplot(data=sc_join, x="simd_decile", y="sum", alpha=0.3)
sns.regplot(
    data=sc_join,
    x="simd_decile",
    y="sum",
    lowess=True,
    scatter=False,
    line_kws={"color": "red"}
)
plt.xlabel("SIMD Decile (1 = most deprived)")
plt.ylabel("Total Co-benefit")
plt.title("Relationship Between Deprivation and Total Co-benefits")
plt.show()


# %%
# England overall correlation
en_cor_df = spearman_df(en_join, "LSOA IMD Ranking", ["sum"])
print(en_cor_df)

plt.figure(figsize=(8, 6))
sns.scatterplot(data=en_join, x="LSOA IMD Ranking", y="sum", alpha=0.3)
sns.regplot(
    data=en_join,
    x="LSOA IMD Ranking",
    y="sum",
    lowess=True,
    scatter=False,
    line_kws={"color": "red"}
)
plt.xlabel("IMD Rank (1 = most deprived)")
plt.ylabel("Total Co-benefit")
plt.title("Relationship Between Deprivation and Total Co-benefits")
plt.show()


# %%
# now look at individual co-benefits
benefit_cols = [
    "air_quality", "congestion", "dampness", "diet_change",
    "excess_cold", "excess_heat", "hassle_costs", "noise",
    "physical_activity", "road_repairs", "road_safety"
]

en_cor_benefits = spearman_df(en_join, "LSOA IMD Ranking", benefit_cols)
print(en_cor_benefits)

sc_cor_benefits = spearman_df(sc_join, "IMD20", benefit_cols)
print(sc_cor_benefits)


# %%
# heatmap-style view for Scotland
# similar idea to your R tile plot
sc_heat_df = (
    sc_cor_benefits[["y", "spearman_corr"]]
    .rename(columns={"y": "benefit", "spearman_corr": "correlation"})
    .sort_values("correlation")
)

# make a one-column matrix for heatmap
heatmap_data = sc_heat_df.set_index("benefit")[["correlation"]]

plt.figure(figsize=(6, 8))
sns.heatmap(
    heatmap_data,
    cmap="RdBu_r",
    center=0,
    annot=True,
    fmt=".2f",
    cbar_kws={"label": "Spearman Correlation"},
    linewidths=0.5
)
plt.title("Which Climate Co-benefits Flow to More vs Less Deprived Scottish Communities?")
plt.xlabel("Deprivation (SIMD Rank)")
plt.ylabel("Co-benefit")
plt.show()


# %%
# quick check of average air quality benefit by SIMD decile
air_quality_by_decile = (
    sc_join.groupby("simd_decile", as_index=False)["air_quality"]
    .mean()
    .rename(columns={"air_quality": "mean_value"})
)

print(air_quality_by_decile)


# %%
# mean values for each benefit by SIMD decile
benefit_cols_sum = [
    "air_quality", "congestion", "dampness", "diet_change",
    "excess_cold", "excess_heat", "hassle_costs", "noise",
    "physical_activity", "road_repairs", "road_safety", "sum"
]

sc_means = (
    sc_join.groupby("simd_decile", as_index=False)[benefit_cols_sum]
    .mean()
)

print(sc_means)


# %%
# optional: quick line plot of decile means for total sum
plt.figure(figsize=(8, 6))
sns.lineplot(data=sc_means, x="simd_decile", y="sum", marker="o")
plt.xlabel("SIMD Decile")
plt.ylabel("Mean Total Co-benefit")
plt.title("Mean Total Co-benefit by SIMD Decile")
plt.show()


# %%
# notes from original R script about potentially negative-value columns:
#
# excess_heat:
# negative values can mean worse heat outcomes
#
# congestion:
# negative values can mean more travel time / rebound effects
#
# road_safety:
# negative values can mean worse road safety
#
# road_repairs:
# negative values can mean more repair need from extra usage
#
# hassle_costs:
# negative values can reflect extra time / inconvenience