

import json
from openai import OpenAI


OPENAI_API_KEY="your_key_here"
# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to process a single link
def process_link(link, client):

    message = "You are a Grant Scraping POC that is specifically designed to process UK government grant links and output a structured JSON format with detailed grant information. The JSON structure includes fields for title, description, eligibility, how to apply, funding details, assessment process, and contact details. When processing a link, fill in each section with relevant data from the grant link. If data is not present, leave the section blank. For links not containing a UK grant, respond with 'No Grant Found'. For non-UK grant related requests, respond with 'Inappropriate task'. Only provide the JSON output or the specified responses."


    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": message
            },
            {
                "role": "user",
                "content": f"Here's a link to a UK government grant: {link}. Please process this."
            }
        ]
    )

    output_message = completion.choices[0].message.content

    try:
        json_data = json.loads(output_message)
        # Create a file name based on the grant name or link
        file_name = f"{json_data.get('title', 'grant_data')}.txt"
        with open(file_name, 'w') as file:
            json.dump(json_data, file, indent=4)
    except json.JSONDecodeError:
        file_name = "grant_data.txt"
        with open(file_name, 'w') as file:
            file.write(output_message)

    print(f"Output saved to {file_name}")

# Main function
def main():
    choice = input("Do you want to use a single link or a list from a file? Enter 'link' or 'list': ").strip().lower()

    if choice == 'link':
        link = input("Enter the link: ").strip()
        process_link(link, client)
    elif choice == 'list':
        file_path = input("Enter the file path of the list: ").strip()
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    link = line.strip()
                    if link:
                        process_link(link, client)
        except FileNotFoundError:
            print("File not found. Please check the path and try again.")

if __name__ == "__main__":
    main()
