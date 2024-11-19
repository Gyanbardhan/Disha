import streamlit as st
from dotenv import load_dotenv
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from fpdf import FPDF

load_dotenv()
os.getenv("GOOGLE_API_KEY")

RESPONSE_JSON = {
    "name": "Teacher's name here",
    "department": "Department name here",    
    "position": "Teacher's position here",
    "phone_no": "Phone number here",
    "email": "Email here",
    "joining_date": "Joining date here",
    "education": [
        {"degree_year": "Degree year here", "college_name": "College name here", "university": "University name here"},
    ],
    "teaching_experience": [
        {"institution": "Institution name here", "position": "Position here", "start_date": "Start date here", "end_date": "End date here"}
    ],
    "industrial_experience": [
        {"institution": "Institution name here", "position": "Position here", "start_date": "Start date here", "end_date": "End date here"}
    ],
    "laboratory_development": [
        {"lab_name": "Lab name here", "position": "Position here", "institution": "Institution name here", "software_used": "Software used here"}
    ],
    "areas_of_interest": ["Area of interest here"],
    "projects": [
        {"title": "Project title here", "funding_agency": "Funding agency here", "role": "Role here", "start_date": "Start date here", "end_date": "End date here", "funding_amount": "Funding amount here"}
    ],
    "publications": {
        "0" :"First Publication Here (all details)",
        "1" :"Second Publication Here (all details)",
        "2" :"Third Publication Here (all details)",
        "3" :"Fourth Publication Here (all details)",
    },
    "supervision": {
        "pg_dissertation": "PG dissertation here",
        "ug_dissertation": "UG dissertation here",
        "phd_dissertation": "PhD dissertation here",
        "mtech_dissertation": "MTech dissertation here"
    },
    "fellowships": [
        {"organization": "Organization name here", "membership_id": "Membership ID here", "type": "Membership type here", "year": "Year here"}
    ]
}

TEMPLATE1 = """\
Text: {text}
You are an expert in information extraction. Given the above text, your job is to extract all relevant details of teachers from the provided text, including the following categories:

1. Name
2. Department (Computer Science Engeneering(CSE)/Electronics Communication Engineering(ECE)/Basic Sciences(BS))
3. Position if not given position give there "Other"
4. Phone number
5. Email
6. Joining date
7. Educational Qualifications ** (all degrees, with university and year) if the information about which degree then also add a column about "degree": degree name here. its compulsory
8. Teaching Experience (institutions, positions, and dates)
9. Industrial Experience (institutions, positions, and dates)
10. Laboratory Development (lab name, position, institution, and software used)
11. Areas of Interest
12. Projects (title, funding agency, role, start and end date, funding amount)
13. Workshops and Continuing Education (title, dates)
14. Publications add all publications below make serial number for all publications and add in json if total=8 then make 0-7 publications add them below there in json.
15. Supervision (PG, UG, PhD, MTech dissertation supervision)
16. Fellowships (organization, membership ID, type, year)

Ensure that all details are correctly formatted and conform to the provided text. If the text does not contain specific information for any key, fill it with 'NA'. Also, ensure phone numbers are properly formatted, and email addresses use '.' instead of 'dot'. If additional relevant information is present that does not fall into the provided categories, create a new key and include it in the final JSON.

### RESPONSE_JSON
{response_json}
"""

TEMPLATE2 = """\
Text: {text}
Extracted_JSON: {result}
You are an expert evaluator and data corrector. Given the text and extracted JSON, your job is to:

1. Evaluate the extracted details for each teacher based on the provided text, ensuring the following categories are correctly evaluated:
   - **Name**
   - **Department** (Computer Science Engineering (CSE)/Electronics Communication Engineering (ECE)/Basic Sciences (BS))
   - **Position** (If the position is not specified, ensure 'Other' is used)
   - **Phone number** (Ensure proper formatting)
   - **Email** (Correct formatting, replacing 'dot' with '.')
   - **Joining date**
   - **Educational Qualifications** (Include all degrees with university and year; fill 'degree' if any are missing) if the information about which degree then also add a column about "degree": degree name here. its ****compulsory ****
   - **Teaching Experience** (Institutions, positions, and dates)
   - **Industrial Experience** (Institutions, positions, and dates)
   - **Laboratory Development** (Lab name, position, institution, software used)
   - **Areas of Interest**
   - **Projects** (Title, funding agency, role, start and end dates, funding amount)
   - **Workshops and Continuing Education** (Title, dates)
   - **Publications** (All publications should be numbered and included in the JSON)
   - **Supervision** (PG, UG, PhD, MTech dissertation supervision)
   - **Fellowships** (Organization, membership ID, type, year)

2. Correct any missing or incorrect information in the provided JSON:
   - Fill missing fields with 'NA' if the information is not available.
   - Ensure phone numbers are formatted correctly.
   - Correct emails that use 'dot' instead of '.'
   - Ensure publications are serialized (e.g., total = 8, serialized as 0-7).
   
3. If any additional relevant information is present that does not fall under these categories, create a new key and include it in the final JSON output.

Make sure to format your response as the final, corrected JSON below.

### Corrected_JSON
{response_json}

"""

def create_pdf(json_data):
    try:
        # Convert JSON data to a string with formatting
        json_string = json.dumps(json_data, indent=4)

        # Extract the teacher's name from the JSON data for the file name
        teacher_name = json_data.get("name", "default_name").replace(" ", "_")  # Replace spaces with underscores
        pdf_file_name = f"{teacher_name}.pdf"

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

        # Write each line of the JSON string to the PDF using multi_cell
        for line in json_string.splitlines():
            pdf.multi_cell(0, 10, line)  # Use multi_cell to handle long text

        # Save the PDF to a file
        pdf.output(pdf_file_name)

        return pdf_file_name
    except Exception as e:
        st.error(f"An error occurred while generating the PDF: {e}")
        return None

def show():
    st.set_page_config(page_title="Faculty", page_icon=":material/edit:")

    st.header("Faculty")
    TEXT = st.text_input("Input Prompt: ", key="input")

    submit = st.button("Submit", key="submit_button")

    if submit and TEXT:
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
            from langchain.prompts import PromptTemplate
            from langchain.chains import LLMChain
            from langchain.chains import SequentialChain

            generation_prompt = PromptTemplate(
                input_variables=["text", "response_json"],
                template=TEMPLATE1
            )
            chain = LLMChain(llm=llm, prompt=generation_prompt, output_key="result", verbose=True)
            evaluation_prompt = PromptTemplate(input_variables=["text", "result", "response_json"], template=TEMPLATE2)
            review_chain = LLMChain(llm=llm, prompt=evaluation_prompt, output_key="review", verbose=True)

            generate_evaluate_chain = SequentialChain(
                chains=[chain, review_chain],
                input_variables=["text", "response_json"],
                output_variables=["result", "review"],
                verbose=True,
            )

            response = generate_evaluate_chain(
                {
                    "text": TEXT,
                    "response_json": json.dumps(RESPONSE_JSON)
                }
            )

            result = response["review"]
            if '### Corrected_JSON\n' in result:
                result = result.split('### Corrected_JSON\n')[1]
                result = json.loads(result)
            elif '### RESPONSE_JSON\n' in result:
                result = result.split('### RESPONSE_JSON\n')[1]
                result = json.loads(result)
            else:
                result = json.loads(result)

            # Store the result in session state
            st.session_state.result = result
            st.success("Data processed successfully!")

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")

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