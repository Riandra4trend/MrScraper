# Intelligent Cattle Ranch Scraper

An intelligent web scraper that uses AI-powered natural language processing to search cattle ranch directories. The system interprets user commands in plain English and converts them into structured API calls to retrieve ranch information from the Shorthorn Digital Beef platform.

## My Approach: From Browser Automation to API Reverse-Engineering

The development of this scraper followed a path of discovery, moving from a conventional but fragile method to a far more robust and efficient solution.

### 1. Initial Attempt with Browser Automation
The first approach involved using browser automation tools like Selenium to simulate a user's actions. This included navigating to the website, clicking the "Ranch Search" tab, selecting a value from the "Search Location" dropdown, and clicking the search button. However, this method proved to be slow and unreliable, frequently failing with `TimeoutException` errors due to the website's dynamic loading behavior.

### 2. Network Traffic Analysis
To overcome these issues, I shifted my focus to analyzing the website's network activity using the browser's Developer Tools. I observed that when a search was performed, the page did not perform a full reload. Instead, it made a background **AJAX** (Asynchronous JavaScript and XML) request to fetch the search results.

### 3. API Endpoint and Payload Discovery
By inspecting this AJAX call, I identified the direct API endpoint responsible for fetching data: `.../ajax/search_results_ranch.php`

Further analysis of the Request URL revealed the parameter pattern used for searches. I discovered that the location was passed in a single parameter `l` with a clear structure: `Country|ProvinceCode`.

* `United States - Alabama` became `l=United States|AL`
* `Canada - All` became `l=Canada|`
* `Argentina` became `l=Argentina|`

### 4. Final API-Driven Architecture
This discovery was a breakthrough. I abandoned the Selenium approach entirely and re-architected the scraper to communicate directly with this API endpoint using the `requests` library. The final step was to leverage a Large Language Model (LLM) to parse natural language commands into the structured `Country|ProvinceCode` format required by the API.

This resulted in the current solution, which is significantly faster, more stable, and independent of the website's visual layout.

## Features

- **Natural Language Processing**: Uses Google's Gemini AI to interpret search commands in plain English
- **Multi-Country Support**: Supports searches across United States, Canada, and Argentina
- **Flexible Search Parameters**: Search by location (country/state/province) and/or ranch name
- **Robust Error Handling**: Gracefully handles edge cases including no results scenarios
- **Comprehensive Testing**: Includes automated test suite with various search scenarios

## Architecture

The system consists of three main components:

1. **AIProcessor**: Uses Google's Gemini AI to parse natural language commands into structured JSON
2. **ShorthornApiScraper**: Handles API communication and data extraction
3. **Location Mapping System**: Maps human-readable locations to API-specific codes

## Prerequisites

- Python 3.8+
- Google AI (Gemini) API key
- Internet connection for API access

## Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Clone the repository**:
```bash
git clone <repository-url>
cd MrScraper
```

2. **Run the automated setup script**:
```bash
python setup.py
```

The setup script will automatically:
- Check system requirements (Python 3.8+)
- Install all required dependencies
- Create `.env` configuration file
- Run installation tests
- Display usage examples

### Option 2: Manual Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd MrScraper
```

2. **Install required dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file in the project root:
```bash
GOOGLE_API_KEY=your_google_ai_api_key_here
```

## API Key Configuration

To get a Google AI API key:
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create or select a project
- Generate an API key
- Copy the key to your `.env` file

**Note**: The scraper will work without an API key using fallback parsing, but AI-powered natural language processing requires a valid Google AI API key.

## Usage

### Command Line Interface

Run searches directly from the command line:

```bash
python intelligent_scraper.py -c "Find all ranches in Texas"
python intelligent_scraper.py -c "Show me breeders from Alberta, Canada"
python intelligent_scraper.py -c "Search for ranches named 'Creek' in Iowa"
python intelligent_scraper.py -c "List all for Canada"
python intelligent_scraper.py -c "argentina any?"
```

### Programmatic Usage

```python
from intelligent_scraper import ShorthornApiScraper

# Initialize the scraper
scraper = ShorthornApiScraper()

# Perform a search
result = scraper.search("Find ranches in California")

# Process results
if "error" not in result:
    print(f"Found {len(result['data'])} ranches")
    print(f"Columns: {result['header']}")
    for row in result['data']:
        print(row)
else:
    print(f"Error: {result['error']}")
```

## Supported Search Patterns

The AI can understand various natural language patterns:

### Location-Based Searches
- `"Find all ranches in Texas"`
- `"Show me breeders from Alberta, Canada"`
- `"List everything in Argentina"`
- `"Any ranches in Wyoming?"`

### Name-Based Searches
- `"Search for ranches named 'Creek'"`
- `"Find 'Circle M' ranch"`
- `"Show me Sullivan farms"`

### Combined Searches
- `"Search for ranches named 'Creek' in Iowa"`
- `"Find 'Circle M' in Texas"`
- `"Sullivan farms in kansas"`

### Informal Queries
- `"argentina any?"`
- `"texas stuff"`
- `"canada all"`

## Supported Locations

### United States
All 50 states are supported using standard 2-letter abbreviations (TX, CA, NY, etc.)

### Canada
- Alberta (AB)
- Ontario (ON)
- Quebec (QC)
- Saskatchewan (SK)

### Argentina
Supported as a country-wide search (no provinces configured)

## API Response Format

The scraper returns results in the following format:

```json
{
  "header": ["Column1", "Column2", "Column3"],
  "data": [
    ["Row1Col1", "Row1Col2", "Row1Col3"],
    ["Row2Col1", "Row2Col2", "Row2Col3"]
  ]
}
```

For errors:
```json
{
  "error": "Error description",
  "details": "Additional error details (optional)"
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_scraper_validation.py
```

### Test Coverage

The test suite includes:

1. **Basic Location Search**: Standard US state search (Texas)
2. **International Search**: Canadian province search (Alberta)
3. **Combined Search**: Name + location search
4. **Country-Wide Search**: Broad location queries
5. **Edge Case Handling**: Non-existent ranch names
6. **Informal Commands**: Vague and informal language processing

### Test Requirements

- Valid Google AI API key in `.env` file
- Active internet connection
- All dependencies installed

## Error Handling

The system handles various error scenarios:

- **Invalid API Key**: Clear error message about missing/invalid credentials
- **Network Issues**: Timeout and connection error handling
- **No Results Found**: Graceful handling of empty search results
- **Invalid Locations**: Helpful messages for unsupported locations
- **AI Parsing Errors**: Fallback error messages when NLP fails

## Logging

The system provides detailed logging at INFO level:

- AI command interpretation results
- API request parameters
- Data retrieval success/failure
- Column headers discovered
- Error details for troubleshooting

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Performance Considerations

- **API Rate Limits**: The Shorthorn API doesn't specify rate limits, but implement delays if needed
- **Caching**: Consider implementing result caching for repeated queries
- **Batch Processing**: Process multiple queries sequentially to avoid overwhelming the API

## Dependencies

- `requests`: HTTP client for API communication
- `pandas`: Data manipulation and HTML table parsing
- `python-dotenv`: Environment variable management
- `google-generativeai`: Google AI integration
- `html5lib`: HTML parsing support
- `beautifulsoup4`: Alternative HTML parser
- `lxml`: XML/HTML processing library

## Project Structure

```
MrScraper/
├── intelligent_scraper.py      # Main scraper implementation
├── test_scraper_validation.py  # Comprehensive test suite
├── setup.py                    # Automated setup script
├── requirements.txt            # Python dependencies
├── .env                       # Your API keys (created by setup)
└── README.md                  # This documentation
```

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY not found"**
   - Ensure `.env` file exists with valid API key
   - Check API key permissions in Google AI Studio

2. **"No tables found matching regex"**
   - This usually indicates no search results
   - Try broader search terms
   - Check if the location is supported

3. **"Failed to parse AI response"**
   - Check internet connection
   - Verify API key is valid and has quota remaining
   - Try simpler search commands

4. **Import errors for HTML parsers**
   - Install missing dependencies: `pip install html5lib beautifulsoup4 lxml`

### Debug Mode

Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is intended for educational and research purposes. Please respect the terms of service of the Shorthorn Digital Beef platform when using this scraper.

## Disclaimer

This tool is designed for legitimate research and data analysis purposes. Users are responsible for ensuring their usage complies with applicable terms of service and legal requirements. The authors are not responsible for any misuse of this tool.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the test cases for usage examples
3. Enable debug logging to identify specific issues
4. Create an issue with detailed error messages and logs