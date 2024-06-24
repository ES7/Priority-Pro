import streamlit as st
import pandas as pd
import pandas as pd
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyA_N-ScGxk5oCVV-6U7Ouc7EwuBvaSWk2Y"
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')


impact_mapping = {
    ' High ': 5,
    ' Medium ': 3,
    ' Low ': 1,
    None: 0
}

effort_mapping = {
    ' High ': 5,
    ' Medium ': 3,
    ' Low ': 1,
    None: 0
}

def processing(df):
    first_col = df.iloc[:, 0]
    
    prompt = """
    1. Sentiment Analysis and Categorization: First, analyze the sentiment of each piece of feedback to categorize it as positive, neutral, or negative. 
    2. Impact Estimation: Estimate the impact of a suggested change based on the sentiment and the content of the feedback:

    Metrics for Impact
    Frequency: The number of times a particular issue or suggestion is mentioned.
    Severity: How severely the issue impacts users (can be inferred from the strength of the sentiment).
    Influence: Feedback from more influential users (e.g., users with a larger following or those who spend more on the product) may have a higher impact.

    Approach
    High Frequency + High Severity + High Influence: High impact.
    Low Frequency + Low Severity + Low Influence: Low impact.
    Combination of these factors: Medium impact.

    3. Effort Estimation: Estimate the effort to make the suggested change by analyzing:

    Metrics for Effort
    Complexity: Technical difficulty of implementing the change.
    Resource Requirements: Number of resources (e.g., developers, designers) needed.
    Time: Estimated time to implement the change.

    Approach
    Complexity Assessment: Categorize feedback into different types of changes (e.g., UI/UX changes, backend changes, new features) and assess the complexity.
    Historical Data: Use historical data to estimate the effort required for similar changes in the past.
    Expert Input: Consult with domain experts to estimate the effort required.

    4. Combining Impact and Effort: To make an informed decision, combine the impact and effort estimations:

    Impact-Effort Matrix
    Create an impact-effort matrix to prioritize changes:

    High Impact, Low Effort: High priority.
    High Impact, High Effort: Consider if resources allow.
    Low Impact, Low Effort: Low priority but can be quick wins.
    Low Impact, High Effort: Generally lower priority.

    Example Workflow 
    Sentiment Analysis: Classify feedback into positive, neutral, or negative.
    Categorization: Identify common themes or issues.
    Impact Scoring: Score each theme based on frequency, severity, and influence.
    Effort Scoring: Score each theme based on complexity, resources, and time required.
    Prioritization: Use the impact-effort matrix to prioritize changes.

    Example
    Feedback: "The app crashes frequently when I try to upload photos."
    Sentiment: Negative
    Impact: High (frequent and severe issue affecting core functionality)
    Effort: High (may require significant debugging and testing)
    Priority: High (critical issue affecting user experience)

    Generate the output in tabular format, table should contain columns: ['Feedbacks', 'Sentiment', 'Impact', 'Effort', 'Priority'].
    """

    for text in first_col:
        prompt += "\n" + text
    
    response = model.generate_content(prompt)
    
    txt = response.text
    lines = txt.strip().split("\n")
    data = [line.strip("|").strip().split("|") for line in lines[1:]]
    df = pd.DataFrame(data, columns=[x.strip() for x in lines[0].strip("|").split("|")])

    df = df.drop(df.index[0]).reset_index(drop=True)

    # Apply mappings to the DataFrame
    df['Impact'] = df['Impact'].map(impact_mapping)
    df['Effort'] = df['Effort'].map(effort_mapping)
    
    # Calculate Priority as the average of Impact and Effort
    df['Priority'] = (df['Impact'] + df['Effort']) / 2
    df = df.sort_values(by='Priority', ascending=False)

    return df


def main():
    st.title("Priority Pro")

    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        st.write("File Uploaded Successfully")
        submit = st.button("Prioritize")
        
        if submit:
            if uploaded_file is not None:
                df = pd.read_excel(uploaded_file)
                pdf = processing(df)
                st.write("Impact, Effort and Priority on a scale of 1(low) to 5(high)")
                st.write(pdf)
                
                st.download_button(label="Download Processed Data as CSV", data=pdf.to_csv(index=False), file_name='processed_data.csv', mime='text/csv')
            else:
                st.write("Please uplaod the resume")

        
        
if __name__ == "__main__":
    main()