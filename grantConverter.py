import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# Hardcode your API key here
api_key = "your_api_key_here"

# Initialize the OpenAI client with the hardcoded API key
client = OpenAI(api_key=api_key)

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator='\n')
        with open('raw.txt', 'w') as file:
            file.write(text)
        return text
    except requests.RequestException as e:
        print(f"Error during website scraping: {e}")
        return None

def process_text(client):
    with open('raw.txt', 'r') as file:
        raw_text = file.read()

    message = ''

    # Open the file and read the content
    with open("prompt.txt", 'r') as file:
        message = file.read()

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": message
                },
                {
                    "role": "user",
                    "content": raw_text
                }
            ]
        )

        output_message = completion.choices[0].message.content

        try:
            json_data = json.loads(output_message)
            title = json_data.get('title', 'grant_data').replace('/', '_')  # Replace '/' in title to avoid file path issues
            file_name = f"{title}.txt"
            with open(file_name, 'w') as file:
                json.dump(json_data, file, indent=4)
        except json.JSONDecodeError:
            file_name = "grant_data.txt"
            with open(file_name, 'w') as file:
                file.write(output_message)

        print(f"Output saved to {file_name}")
        os.remove('raw.txt')

    except Exception as e:
        print(f"An error occurred while processing the text: {e}")

def main():
    choice = input("Do you want to use a single URL or a list from a file? Enter 'URL' or 'list': ").strip().lower()

    if choice == 'url':
        url = input("Enter the URL to scrape: ").strip()
        if scrape_website(url):
            process_text(client)
    elif choice == 'list':
        file_path = input("Enter the file path of the list: ").strip()
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    url = line.strip()
                    if url and scrape_website(url):
                        process_text(client)
        except FileNotFoundError:
            print("File not found. Please check the path and try again.")
    else:
        print("Invalid choice. Please enter 'URL' or 'list'.")


if __name__ == "__main__":
    main()
