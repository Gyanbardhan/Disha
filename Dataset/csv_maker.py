import streamlit as st
import pandas as pd
import os

# Streamlit app
st.title("CSV Merger")
st.write("Upload multiple CSV files to merge them into a single file.")

uploaded_files = st.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True)

if st.button("Merge Files") and uploaded_files:
    merged_data = pd.DataFrame()
    
    for uploaded_file in uploaded_files:
        # Read each CSV file into a DataFrame
        df = pd.read_csv(uploaded_file)
        # Append to the merged DataFrame
        merged_data = pd.concat([merged_data, df], ignore_index=True)
    
    # Save the merged data to a new CSV file
    output_path = "merged_output.csv"
    merged_data.to_csv(output_path, index=False)
    
    st.success(f"Files merged successfully! Download the merged file below:")
    st.download_button(label="Download Merged CSV", data=merged_data.to_csv(index=False), file_name=output_path, mime="text/csv")
    
    st.write("Merged Data Preview:")
    st.dataframe(merged_data)
else:
    st.write("No files uploaded yet.")
