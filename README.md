# Ktuvit Subtitle Automation

An automated tool for downloading Hebrew subtitles from Ktuvit.me. This tool uses Selenium WebDriver to automate the process of logging in, navigating to TV show pages, and downloading subtitles for entire seasons.

## Features

- Automated login to Ktuvit.me
- Bulk download of subtitles for entire seasons
- Automatic file naming in standard format (e.g., `The.Big.Bang.Theory.S01E01.srt`)
- Download retry mechanism for failed downloads
- Progress tracking and detailed logging
- Downloads saved to local project directory

## Prerequisites

- Python 3.8+
- Chrome browser installed
- Git (for cloning the repository)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LironeFitoussi/Ktuvit-Python-Automation.git
cd ktuvit-automation
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `config.py` file in the project root:
```python
# Ktuvit login credentials
KTUVIT_EMAIL = "your.email@example.com"
KTUVIT_PASSWORD = "your-encrypted-password"  # Get this from browser console
```

To get your encrypted password:
1. Go to Ktuvit.me
2. Open browser console (F12)
3. Run this JavaScript:
```javascript
x = { value: 'YOUR-PASSWORD' };
loginHandler.EncryptPassword({}, x, 'YOUR-EMAIL');
copy(x.value);
```

## Project Structure

```
ktuvit-automation/
├── config.py                 # Configuration settings
├── main.py                  # Main script
├── downloads/               # Downloaded subtitles
├── pages/
│   ├── __init__.py
│   ├── base_page.py        # Base page object
│   └── subtitle_page.py    # Subtitle page handling
└── utils/
    └── driver_factory.py   # WebDriver setup
```

## Usage

1. Run the script:
```bash
python main.py
```

2. Enter the TV show URL when prompted

3. Select the season number when prompted

4. The script will:
   - Log in to Ktuvit
   - Navigate to the show page
   - Download subtitles for all episodes in the selected season
   - Save files in the `downloads` folder

## Features in Detail

### Automatic Login
- Handles login process with encrypted password
- Verifies successful login

### Season Processing
- Lists all available seasons
- Downloads all episodes in selected season
- Proper error handling and retry mechanism

### Download Retry Mechanism
- 3 retry attempts for failed downloads
- 3-second interval between retries
- Error detection and handling

### File Naming
Files are saved in the format:
```
The.Big.Bang.Theory.S01E01.srt
[Series.Name].[Season][Episode].srt
```

## Error Handling

- Failed downloads are automatically retried
- Detailed error logging
- Progress tracking for each episode
- Session management and recovery

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
