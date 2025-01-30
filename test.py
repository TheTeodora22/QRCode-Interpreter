import pandas as pd

# URL of the website
url = "https://www.thonky.com/qr-code-tutorial/character-capacities"

# Read all tables from the webpage
tables = pd.read_html(url)

# Check how many tables were found
print(f"Number of tables found: {len(tables)}")

# Display the first table
df = tables[1]
print(df)