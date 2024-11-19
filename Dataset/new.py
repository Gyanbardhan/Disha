import streamlit as st
import pdfplumber
import csv
import os
import pandas as pd

def extract_text_from_pdf(file):
    """Extracts complete text from a PDF file object using pdfplumber."""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # Append text or empty string if no text on page
    return text

def save_to_csv(data, csv_path="output.csv"):
    """Appends data to a CSV file with 'Name' and 'Details' columns."""
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Name", "Details"])
        writer.writerows(data)

# Streamlit app
st.title("PDF to CSV Converter")
st.write("Upload multiple PDF files to extract their contents and save to a CSV file.")

uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if st.button("Process Files") and uploaded_files:
    data = []
    for uploaded_file in uploaded_files:
        pdf_content = extract_text_from_pdf(uploaded_file)
        
        # Remove the .pdf extension from the file name
        file_name = os.path.splitext(uploaded_file.name)[0]
        
        data.append([file_name, pdf_content])
    
    # Append data to CSV
    save_to_csv(data)

    # Convert data to a DataFrame and display it
    df = pd.DataFrame(data, columns=["Name", "Details"])
    st.success("Data extracted and saved to output.csv!")
    st.write("Extracted Data:")
    st.dataframe(df)
else:
    st.write("No files uploaded yet.")
