import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import time

# Hardcode your API key here
api_key = ""

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


def process_text(client, raw_text):
    message = ''

    # Open the file and read the content
    with open("prompt.txt", 'r') as file:
        message = file.read()

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
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
            # Extracting title from JSON for the file name
            title = json_data.get('title', 'grant_data').replace('/', '_')
            file_name = f"{title}.txt"
            with open(file_name, 'w') as file:
                json.dump(json_data, file, indent=4)
            print(f"Output saved to {file_name}")
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
        raw_text = scrape_website(url)
        if raw_text:
            print("Processing...", end="")
            process_text(client, raw_text)
    elif choice == 'list':
        file_path = input("Enter the file path of the list: ").strip()
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    url = line.strip()
                    if url:
                        print(f"Processing URL: {url} ...", end="")
                        raw_text = scrape_website(url)
                        if raw_text:
                            process_text(client, raw_text)
                        time.sleep(2)  # Wait for 2 seconds before processing the next URL
        except FileNotFoundError:
            print("File not found. Please check the path and try again.")
    else:
        print("Invalid choice. Please enter 'URL' or 'list'.")


if __name__ == "__main__":
    main()
