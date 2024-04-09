import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import BytesIO

# Function to perform the scraping
def scrape_website(domain):
    data = []
    from_page = 1
    to_page = 10  # You may adjust the range as needed

    for i in range(from_page, to_page + 1):
        response = requests.get(f"https://www.trustpilot.com/review/{domain}?page={i}")
        web_page = response.text
        soup = BeautifulSoup(web_page, "html.parser")

        for e in soup.select('article'):
            data.append({
                'review_title': e.h2.text,
                'review_date_original': e.select_one('[data-service-review-date-of-experience-typography]').text.split(': ')[-1],
                'review_rating': e.select_one('[data-service-review-rating] img').get('alt'),
                'review_text': e.select_one('[data-service-review-text-typography]').text if e.select_one('[data-service-review-text-typography]') else None,
                'page_number': i
            })

    return pd.DataFrame(data)

# Function to convert DataFrame to Excel format for download
def to_excel(df):
    output = BytesIO()
    # No need to explicitly call save(), it's handled by the context manager
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    # Important: Seek to the beginning of the stream before returning
    output.seek(0)
    return output

# Streamlit UI components
st.title('Trustpilot Review Scraper')

# User inputs the URL part for Trustpilot reviews
user_input_url = st.text_input('Enter Trustpilot part of the URL (e.g., www.lego.com):', '')

if st.button('Scrape'):
    if user_input_url:
        domain = user_input_url.strip()
        result_df = scrape_website(domain)
        
        if not result_df.empty:
            st.write('Scraping Completed Successfully!')
            st.dataframe(result_df.head())  # Display the first few results as an example

            # Convert DataFrame to Excel and create a download button
            df_xlsx = to_excel(result_df)
            st.download_button(label='📥 Download Result as Excel',
                               data=df_xlsx,
                               file_name='scraped_reviews.xlsx',
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            st.write("No data scraped. Please check the URL.")
    else:
        st.write('Please enter a valid Trustpilot URL part.')
