# CRAWL PILOT

#### Video Demo: https://youtu.be/U_si7EKJaf4

#### Description

Crawl Pilot is a Python-based web scraping and summarization tool that allows users to extract content from web pages and generate concise summaries using OpenAI's language model.

### Features

1. Web Content Fetching: Retrieves content from user-specified URLs or a CSV file containing multiple URLs.
2. Content Scraping: Extracts text and title from web pages using BeautifulSoup.
3. Text Summarization: Utilizes OpenAI's GPT model to generate summaries of scraped content.
4. Summary Storage: Option to save summaries to a CSV file for future reference.
5. User-friendly Interface: Employs ASCII art for the title and interactive prompts for user inputs.

### How It Works

1. The user chooses between entering a single URL or providing a CSV file with multiple URLs.
2. The application fetches the content from the provided URL.
3. It then scrapes the content to extract the main text and title.
4. The extracted text is summarized using OpenAI's language model.
5. The summary is displayed to the user.
6. The user is given an option to save the summary to a CSV file.

### Code Structure

The `project.py` file contains the following functions and classes:

1. `main()`: 
   - The entry point of the application.
   - Orchestrates the web crawling and summarization process.
   - Calls other functions to fetch content, scrape, summarize, and save results.

2. `read_urls_from_csv()`:
   - Reads URLs from a CSV file.
   - Returns a List of urls.

3. `process_single_url()`:
   - Processes a single URL response.

4. `process_multiple_urls()`:
   - Processes multiple URLs from a list.

5. `fetch_content()`:
   - Prompts the user for a URL and retrieves the web page content.
   - Handles URL validation and automatically adds 'https://' if missing.
   - Returns a `requests.Response` object.

6. `scrape_content(content)`:
   - Parses HTML content using BeautifulSoup.
   - Extracts all paragraph texts and the page title.
   - Returns a tuple of (page_text, page_title).

7. `summarize_text(text)`:
   - Uses OpenAI's language model to generate a summary of the input text.
   - Handles authentication errors by reloading the API key if needed.
   - Returns a dictionary with the summarized text.

8. `save_summary(page)`:
   - Prompts the user to save the summary.
   - If confirmed, saves the title, summary, and date to a CSV file.

9. `load_api_key(delete=False)`:
   - Manages the OpenAI API key.
   - Can delete existing key, prompt for a new one, and update environment variables.

10. `class ScrapedPage`:
   - A simple class to represent a scraped web page.
   - Contains title and summary attributes.
   - Provides a string representation for easy printing.


### Error Handling

- The program includes error handling for invalid URLs and API authentication issues.
- It will continually prompt for a valid URL or API key until successful.


### Dependencies

- requests: For making HTTP requests
- beautifulsoup4: For parsing HTML content
- python-dotenv: For managing environment variables
- art: For ASCII art generation
- inquirer: For interactive command-line user interfaces
- langchain: For text summarization using language models
- openai: For accessing OpenAI's API

### Setup

1. Clone the repository
2. Install the required dependencies:
```
 pip install -r requirements.txt
```
3. Set up your OpenAI API key in a `.env` file or when prompted by the application


### Usage

Run the script using Python:
```
python project.py
```
Follow the prompts to enter a URL and interact with the application.

### Future Improvements

- Enhance the summarization algorithm and try to implment using localy installed model.
