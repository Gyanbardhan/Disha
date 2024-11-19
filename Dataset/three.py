import streamlit as st
from dotenv import load_dotenv
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from fpdf import FPDF

load_dotenv()
os.getenv("GOOGLE_API_KEY")



TEMPLATE1 = """\
Text: {text}

You are an expert in information extraction. Based on the text provided above, extract all relevant details in a structured format. Each detail should be assigned to a specific key with the corresponding value. The keys must be clearly named and the values should reflect the content accurately.
If specific details are missing or incomplete in the text, mark the values as 'NA'. Ensure phone numbers, emails, and names are properly formatted, and replace any placeholder symbols like 'dot' in emails with a period ('.').

The output should be in valid JSON formatin details with appropriate details.
Remove all special characters.
"""

TEMPLATE2 = """\
Text: {text}
Extracted_JSON: {result}

You are an expert evaluator and data corrector. Based on the provided text and extracted JSON, your task is to:

1. Evaluate the extracted details, ensuring that all relevant information is correctly captured and structured.
   - Remove all special characters.

   
2. Ensure that all keys and values are accurately extracted. If there are any missing or incorrect details, update the corresponding values. 
   - If any required details are not available in the text, make sure they are marked as 'NA.'
   - Verify that any additional information not covered by predefined categories is placed under `additional_info`.

3. Correct any formatting issues or inaccuracies found in the extracted JSON. 
   - Ensure the final output is well-formatted JSON.
   - Remove all special characters.

The final JSON output.
"""



def create_pdf(json_like_str):
    try:
        # Remove 'json' from the start if it exists
        if json_like_str.startswith("```json"):
            json_like_str = json_like_str.replace("```json\n", "").replace("```", "").strip()

        if json_like_str.startswith("```JSON"):
            json_like_str = json_like_str.replace("```JSON\n", "").replace("```", "").strip()
        
        # Assume the input is a string formatted similarly to JSON
        json_string = json_like_str  # Keep the input as is

        # Extract the teacher's name manually if the string has a "name" field pattern
        pdf_file_name = f"x.pdf"

        # Create a PDF class without header and footer
        class PDF(FPDF):
            def header(self):
                pass  # No header

            def footer(self):
                pass  # No footer

        # Create a PDF instance
        pdf = PDF()
        pdf.add_page()

        # Set font for the body
        pdf.set_font("Courier", size=10)

        # Write each line of the string to the PDF using multi_cell
        for line in json_string.splitlines():
            pdf.multi_cell(0, 10, line)  # Use multi_cell to handle long text

        # Save the PDF to a file
        pdf.output(pdf_file_name)

        return pdf_file_name
    except Exception as e:
        st.error(f"An error occurred while generating the PDF: {e}")
        return None

def show():
    st.set_page_config(page_title="Staff", page_icon=":material/edit:")

    st.header("Staff")
    TEXT = st.text_input("Input Prompt: ", key="input")

    submit = st.button("Submit", key="submit_button")

    if submit and TEXT:
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        from langchain.chains import SequentialChain
        generation_prompt = PromptTemplate(
            input_variables=["text"],
            template=TEMPLATE1
        )
        chain = LLMChain(llm=llm, prompt=generation_prompt, output_key="result", verbose=True)
        evaluation_prompt = PromptTemplate(input_variables=["text", "result"], template=TEMPLATE2)
        review_chain = LLMChain(llm=llm, prompt=evaluation_prompt, output_key="review", verbose=True)
        generate_evaluate_chain = SequentialChain(
            chains=[chain, review_chain],
            input_variables=["text"],
            output_variables=["result", "review"],
            verbose=True,
        )
        response = generate_evaluate_chain(
            {
                "text": TEXT
            }
        )
        result = response["review"]
        st.write(result)
#        if '```json\n' in result:
#            # Split the text on the code block and grab the JSON part
#            result = result.split('```json\n')[1]
#            result = result.split('```')[0]  # Ensure no extra content after JSON
#        elif '```JSON\n' in result:
#            result = result.split('```JSON\n')[1]
#            result = result.split('```')[0]  # Ensure no extra content after JSON
#        else:
#            # If the JSON block is not wrapped, this step ensures the data is parsed correctly.
#            try:
#                result = json.loads(result)
#            except json.JSONDecodeError:
#                st.error("Failed to parse the JSON data. Please check the format.")
#                return
#        
#        # Now safely load the JSON
#        try:
#            result = json.loads(result)
#            # Store the result in session state
#            st.session_state.result = result
#            st.success("Data processed successfully!")
#        except json.JSONDecodeError as e:
#            st.error(f"An error occurred: {e}")

        st.session_state.result = result
        st.success("Data processed successfully!")

    if st.button("Generate PDF", key="generate_pdf_button") and 'result' in st.session_state:
        pdf_file = create_pdf(st.session_state.result)
        if pdf_file:
            st.success("PDF generated successfully!")

            # Provide a download link for the generated PDF
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="Download PDF",
                    data=file,
                    file_name=pdf_file,
                    mime="application/pdf"
                )
    elif st.button("Download PDF", key="generate_pdf_button_no_result"):
        st.warning("Please process the data first before generating the PDF.")

show()