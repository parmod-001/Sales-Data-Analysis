import pandas as pd
import numpy as np

np.random.seed(42)

n = 12000

products = [
    "Laptop", "Mobile", "Tablet", "Monitor",
    "Keyboard", "Mouse", "Headphones",
    "Printer", "Smart Watch", "Camera"
]

regions = ["North", "South", "East", "West", "Central"]

categories = {
    "Laptop": "Electronics",
    "Mobile": "Electronics",
    "Tablet": "Electronics",
    "Monitor": "Electronics",
    "Keyboard": "Accessories",
    "Mouse": "Accessories",
    "Headphones": "Accessories",
    "Printer": "Office",
    "Smart Watch": "Wearables",
    "Camera": "Electronics"
}

prices = {
    "Laptop": 60000,
    "Mobile": 25000,
    "Tablet": 30000,
    "Monitor": 15000,
    "Keyboard": 2000,
    "Mouse": 1000,
    "Headphones": 3000,
    "Printer": 12000,
    "Smart Watch": 8000,
    "Camera": 45000
}

product = np.random.choice(products, n)
quantity = np.random.randint(1, 8, n)

data = pd.DataFrame({
    "Order_ID": range(10001, 10001 + n),
    "Order_Date": pd.date_range(
        start="2024-01-01",
        end="2025-12-31",
        periods=n
    ),
    "Region": np.random.choice(regions, n),
    "Product": product,
    "Category": [categories[p] for p in product],
    "Quantity": quantity,
    "Unit_Price": [prices[p] for p in product]
})

data["Sales"] = data["Quantity"] * data["Unit_Price"]


data.loc[np.random.choice(n, 50, replace=False), "Region"] = np.nan

data.to_csv("../Data/sales_data.csv", index=False)

print("Dataset created successfully!")
print("Total records:", len(data))
print(data.head())