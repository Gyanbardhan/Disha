import pandas as pd

# Load the CSV file
df = pd.read_csv("ece.csv")

# Process the 'name' column
df['Details'] = df['Details'].str.replace('_', ' ').str.replace('```JSON', ' ').str.replace('.', ' ')

# Save the modified DataFrame to a new CSV file
df.to_csv("ece.csv", index=False)
