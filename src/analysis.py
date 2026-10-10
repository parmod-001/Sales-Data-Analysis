import pandas as pd
import os

input_file = "../Data/sales_data.csv"
output_file = "../Data/cleaned_sales_data.csv"

df = pd.read_csv(input_file)

print("Original Shape:", df.shape)

df["Order_Date"] = pd.to_datetime(df["Order_Date"])

df["Region"] = df["Region"].fillna("Unknown")

df = df.drop_duplicates()

df = df[df["Quantity"] > 0]

df = df[df["Unit_Price"] > 0]

df["Sales"] = df["Quantity"] * df["Unit_Price"]

df["Year"] = df["Order_Date"].dt.year
df["Month"] = df["Order_Date"].dt.month_name()
df["Month_Number"] = df["Order_Date"].dt.month

df["Year_Month"] = df["Order_Date"].dt.to_period("M").astype(str)

df.to_csv(output_file, index=False)

print("Cleaned Shape:", df.shape)
print("Cleaned dataset saved!")


print("\nTotal Sales:")
print(df["Sales"].sum())

print("\nTotal Quantity Sold:")
print(df["Quantity"].sum())

print("\nSales by Region:")
print(
    df.groupby("Region")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\nSales by Product:")
print(
    df.groupby("Product")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\nSales by Category:")
print(
    df.groupby("Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\nMonthly Sales:")
print(
    df.groupby("Year_Month")["Sales"]
    .sum()
)

print("\nTop 5 Products:")
print(
    df.groupby("Product")["Sales"]
    .sum()
    .nlargest(5)
)

print("\nTop Region:")
print(
    df.groupby("Region")["Sales"]
    .sum()
    .idxmax()
)