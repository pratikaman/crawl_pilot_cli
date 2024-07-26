import os
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv, dotenv_values

from urllib.parse import urlparse
from bs4 import BeautifulSoup

from art import text2art  
import inquirer

from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document


def main():
    """
    The main function that orchestrates the web crawling and summarization process.

    This function performs the following steps:
    1. Displays the application title.
    2. Loads the API key.
    3. Fetches content from a user-specified URL.
    4. Scrapes the content to extract text and title.
    5. Summarizes the extracted text.
    6. Creates a ScrapedPage object with the title and summary.
    7. Prints the scraped page information.
    8. Saves the summary to a file.

    The function doesn't take any parameters and doesn't return any value.
    It serves as the entry point for the Crawl Pilot application.
    """

    print(text2art("Crawl  Pilot"))

    load_api_key()

    questions = [
        inquirer.List('input_type', message="Choose input type", choices=['Single URL', 'CSV file with URLs']),
    ]

    answers = inquirer.prompt(questions)


    if answers['input_type'] == 'Single URL':
        response = fetch_content()
        process_single_url(response)
    else:
        file_path = input("Enter the path to your CSV file: ")
        urls = read_urls_from_csv(file_path)
        process_multiple_urls(urls)
    


def read_urls_from_csv(file_path):
    """
    Reads URLs from a CSV file.

    Parameters:
    file_path (str): Path to the CSV file containing URLs.

    Returns:
    list: A list of URLs read from the CSV file.
    """
    urls = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:  # Check if the row is not empty
                urls.append(row[0])  # Assume URL is in the first column
    return urls


def process_single_url(response):

    page_text, page_title = scrape_content(response.content)

    summary = summarize_text(page_text)

    page = ScrapedPage(title=page_title, summary=summary['output_text'])

    print(page)

    save_summary(page)

def process_multiple_urls(urls):
    for url in urls:
        print(f"\nProcessing URL: {url}")
        try:
            response = requests.get(url, timeout=30, allow_redirects=True)
            process_single_url(response)
        except requests.RequestException as e:
            print(f"Error processing URL {url}: {str(e)}")


def fetch_content():
    """
    Fetches the content of a web page from a user-provided URL.

    This function prompts the user to enter a URL, validates it, and attempts to retrieve
    the content of the web page. If the URL is invalid or the request fails, it will
    continue to prompt the user until a valid URL is provided and content is successfully retrieved.

    Parameters:
    None

    Returns:
    requests.Response: A Response object containing the content of the requested web page
                       and other metadata about the request.

    Raises:
    No exceptions are raised as they are caught and handled within the function.
    """

    while True:
        page_url = input("Enter url: ")

        try:
            parsed_url = urlparse(page_url)

            # If no scheme is present, add 'https://'
            if not parsed_url.scheme:
                page_url = 'https://' + page_url

            response = requests.get(page_url,timeout=30, allow_redirects=True)


            break

        except requests.RequestException as e:

            print("\nInvalid url\n")

            continue

    return response


def scrape_content(content):
    """
    Scrapes the content of a web page to extract text and title.

    This function uses BeautifulSoup to parse the HTML content of a web page,
    extract all paragraph texts, and determine the page title.

    Parameters:
    content (str): The HTML content of the web page to be scraped.

    Returns:
    tuple: A tuple containing two elements:
        - page_text (str): The concatenated text of all paragraphs found on the page.
        - page_title (str): The title of the page, either from the first H1 tag or the page title.

    """

    # using lxml as recommended by BS4 documentation
    soup = BeautifulSoup(content, 'lxml')
    titles = soup.find_all('h1')

    page_text = ''.join(paragraph.get_text() for paragraph in soup.find_all('p'))

    # if there is no H1 tag containing the title use web page title.
    page_title = titles[0].text.strip() if titles else soup.title.string.strip()

    return page_text, page_title



def summarize_text(text):
    """
    Summarizes the given text using OpenAI's language model.

    This function creates a ChatOpenAI instance and uses it to generate a summary of the input text.
    If an authentication error occurs, it attempts to reload the API key and retry the summarization.

    Parameters:
    text (str): The input text to be summarized.

    Returns:
    dict: A dictionary containing the summarized text under the key 'output_text'.

    Raises:
    Exception: If there's an authentication error, which is caught and handled internally.
    """

    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

    chain = load_summarize_chain(llm, chain_type="stuff")

    try:
        output = chain.invoke([Document(page_content=text)])
        return output

    except Exception as e:

        print("\nAuthentication error")

        load_api_key(delete=True)

        return summarize_text(text)


def save_summary(page):
    """
    Prompts the user to save the summary of a scraped page and saves it to a CSV file if confirmed.

    This function presents a yes/no option to the user for saving the summary. If the user chooses 'yes',
    it saves the page title, summary, and current date to a CSV file named 'summary.csv'. If the file
    doesn't exist, it creates a new one with appropriate headers.

    Parameters:
    page (ScrapedPage): An object containing the title and summary of the scraped page.
                        It should have 'title' and 'summary' attributes.

    Returns:
    None

    Side effects:
    - Interacts with the user via command line input.
    - May create or append to a file named 'summary.csv' in the current directory.
    - Prints "Done!!" to the console if the summary is saved.
    """

    options = ["yes", "no"]

    questions = [
        inquirer.List('save', message="Save summary?", choices=options),
    ]

    answers = inquirer.prompt(questions)

    chosen_option = answers["save"]


    if chosen_option == options[0]:

        current_datetime = datetime.now()

        file_exists = os.path.isfile("summary.csv")

        with open("summary.csv", 'a', newline='') as file:

            writer = csv.DictWriter(file, fieldnames=["title", "summary", "date"])

            if not file_exists:
                writer.writeheader()

            writer.writerow({"title": page.title, "summary": page.summary, "date": current_datetime})

        print("\nDone!!\n")



def load_api_key(delete=False):
    """
    Load or update the OpenAI API key from a .env file or user input.

    This function manages the OpenAI API key used for authentication. It can optionally
    delete the existing key, prompt the user for a new key if one doesn't exist,
    and update the environment variables with the API key.

    Parameters:
    delete (bool): If True, deletes the existing content of the .env file before processing.
                   Defaults to False.

    Returns:
    None

    Side effects:
    - May create or modify a .env file in the current directory.
    - Updates the OPENAI_API_KEY environment variable.
    - Prompts the user for input if no API key is found.
    """

    if delete:
        with open(".env", "w") as file:
            file.close()

    config = dotenv_values(".env")

    if 'OPENAI_API_KEY' not in config:

        while True:
            api_key = input("Enter api key: ")

            if api_key:

                with open(".env", "w") as file:
                    file.write(f"OPENAI_API_KEY = {api_key}")

                break

        os.environ["OPENAI_API_KEY"] = api_key


    # take environment variables from .env.
    load_dotenv()


class ScrapedPage:

    def __init__(self, title, summary):
        self.title = title
        self.summary = summary

    def __str__(self):
        return f"\nTitle- {self.title}\nSummary- {self.summary}\n"



if __name__ == "__main__":
    main()

