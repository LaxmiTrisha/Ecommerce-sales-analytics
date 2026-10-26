
import pandas as pd
from pathlib import Path

data_folder = Path(__file__).resolve().parent.parent / "Data"

for file in data_folder.glob("*.csv"):
    print(f"\n--- {file.name} ---")

    df = pd.read_csv(file)

    print("Rows and columns:", df.shape)
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nMissing values:")
    print(df.isnull().sum().sum())

    print("\nFirst 5 rows:")
    print(df.head())
