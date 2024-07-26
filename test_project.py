import pytest
from unittest.mock import patch, mock_open, call
import requests
from datetime import datetime
from project import fetch_content, scrape_content, save_summary, ScrapedPage, summarize_text



def test_fetch_content():
    # Test with valid URL
    with patch('builtins.input', return_value='https://example.com'), patch('requests.get') as mock_get:
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = fetch_content()
        assert isinstance(result, requests.Response)
        assert result.status_code == 200

    # Test with URL missing scheme
    with patch('builtins.input', return_value='example.com'), patch('requests.get') as mock_get:
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = fetch_content()
        assert isinstance(result, requests.Response)
        assert result.status_code == 200
        mock_get.assert_called_with('https://example.com', timeout=30, allow_redirects=True)

    # Test with invalid URL, then valid URL
    with patch('builtins.input', side_effect=['invalid_url', 'https://example.com']), patch('requests.get') as mock_get:
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_get.side_effect = [requests.RequestException, mock_response]
        
        result = fetch_content()
        assert isinstance(result, requests.Response)
        assert result.status_code == 200
        assert mock_get.call_count == 2


def test_scrape_content():
    # Test case 1: HTML with h1 and paragraphs
    html_content1 = """
    <html>
        <head><title>Page Title</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
        </body>
    </html>
    """
    text1, title1 = scrape_content(html_content1)
    assert text1 == "Paragraph 1Paragraph 2"
    assert title1 == "Main Heading"

    # Test case 2: HTML without h1 but with title
    html_content2 = """
    <html>
        <head><title>Page Title</title></head>
        <body>
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
        </body>
    </html>
    """
    text2, title2 = scrape_content(html_content2)
    assert text2 == "Paragraph 1Paragraph 2"
    assert title2 == "Page Title"

    # Test case 3: HTML without paragraphs
    html_content3 = """
    <html>
        <head><title>Empty Page</title></head>
        <body>
            <h1>No Content</h1>
        </body>
    </html>
    """
    text3, title3 = scrape_content(html_content3)
    assert text3 == ""
    assert title3 == "No Content"

    # Test case 4: Empty HTML
    html_content4 = "<html></html>"
    with pytest.raises(AttributeError):
        scrape_content(html_content4)


@pytest.fixture
def mock_page():
    return ScrapedPage(title="Test Title", summary="Test Summary")

@pytest.fixture
def mock_datetime(monkeypatch):
    mock_date = datetime(2023, 1, 1, 12, 0, 0)
    class MockDatetime:
        @classmethod
        def now(cls):
            return mock_date
    monkeypatch.setattr('project.datetime', MockDatetime)
    return mock_date

def test_save_summary_yes(mock_page, mock_datetime):
    with patch('inquirer.prompt', return_value={"save": "yes"}), \
         patch('os.path.isfile', return_value=False), \
         patch('builtins.open', mock_open()) as mock_file:
        
        save_summary(mock_page)
        
        mock_file.assert_called_once_with("summary.csv", 'a', newline='')
        handle = mock_file()
        handle.write.assert_any_call("title,summary,date\n")
        handle.write.assert_any_call(f"Test Title,Test Summary,{mock_datetime}\n")

def test_save_summary_yes(mock_page, mock_datetime):
    with patch('inquirer.prompt', return_value={"save": "yes"}), \
         patch('os.path.isfile', return_value=False), \
         patch('builtins.open', mock_open()) as mock_file:
        
        save_summary(mock_page)
        
        mock_file.assert_called_once_with("summary.csv", 'a', newline='')
        handle = mock_file()
        handle.write.assert_has_calls([
            call("title,summary,date\r\n"),
            call(f"Test Title,Test Summary,{mock_datetime}\r\n")
        ], any_order=True)

def test_save_summary_file_exists(mock_page, mock_datetime):
    with patch('inquirer.prompt', return_value={"save": "yes"}), \
         patch('os.path.isfile', return_value=True), \
         patch('builtins.open', mock_open()) as mock_file:
        
        save_summary(mock_page)
        
        mock_file.assert_called_once_with("summary.csv", 'a', newline='')
        handle = mock_file()
        handle.write.assert_called_once_with(f"Test Title,Test Summary,{mock_datetime}\r\n")
    assert "title,summary,date\r\n" not in [call[0][0] for call in handle.write.call_args_list]




def test_summarize_text_valid_input():
    text = "This is a sample text to be summarized."
    expected_output = {"output_text": "Summary of the sample text."}

    with patch('project.load_summarize_chain') as mock_load_chain, patch('project.ChatOpenAI') as mock_chat_openai:

        mock_llm = mock_chat_openai.return_value
        mock_chain = mock_load_chain.return_value
        mock_chain.invoke.return_value = expected_output

        result = summarize_text(text)

        assert result == expected_output
        mock_load_chain.assert_called_once_with(mock_llm, chain_type="stuff")
        mock_chat_openai.assert_called_once_with(temperature=0, model_name="gpt-4o-mini")