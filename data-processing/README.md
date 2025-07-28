# Meeting Data Processing Tools

This directory contains tools for converting Google Sheets event data into the JSON format required by the NLP SIG website.

## Quick Start

1. **Export your Google Sheets** as CSV (File → Download → CSV)
2. **Place the CSV file** in this directory (it should automatically be named `NLP SIG (all previous talks from 2021) - Sheet1.csv`)
3. **Run the conversion script**:
   ```bash
   python convert_events.py
   ```
   Or with a custom filename:
   ```bash
   python convert_events.py your_custom_file.csv
   ```
4. **Upload the generated `meetings-data.json`** to the website root directory

## Files

```
data-processing/
├── README.md                                              # This file
├── convert_events.py                                      # Main conversion script
├── NLP SIG (all previous talks from 2021) - Sheet1.csv   # Your Google Sheets export
└── meetings-data.json                                     # Generated output (after running script)
```

## Google Sheets to CSV Export

1. Open your Google Sheets with the events data
2. Go to **File** → **Download** → **Comma Separated Values (.csv)**
3. The file will be automatically named `NLP SIG (all previous talks from 2021) - Sheet1.csv`
4. Save it in this directory

## Expected CSV Format

Your spreadsheet should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Date | Event date | `30/10/2025` or `24.11.22` |
| Presenter | Speaker name | `Joseph Boyle` |
| Event Name | Talk/session title | `Building Useful Agents` |
| Type of Session | Session type | `seminar` or `journal club` |
| Zoom Link | Online meeting link | `https://zoom.us/...` |
| Room | Meeting room | `Ada Lovelace` |
| Abstract | Talk/session abstract | `This talk presents...` |
| Bio for Speaker | Speaker biography | `Dr. Smith is a researcher...` |
| Paper Links | Comma-separated paper URLs | `https://..., https://...` |

### Optional Columns
You can also add:
- `authors` - Paper authors

### Date Format Handling
The script automatically handles different date formats:
- **Before/including 9/29/2022**: MM/DD/YYYY format
- **After 9/29/2022**: DD/MM/YYYY or DD.MM.YYYY format

### Information Rules
- **Past events (before July 28, 2025)**: Only basic info (no abstracts, bios, paper links)
- **Future events (after July 28, 2025)**:
  - **Seminars**: Abstract gets "TBA" if empty, Bio optional (no TBA if empty)
  - **Journal clubs**: Abstract optional (no TBA if empty), no bios
  - **Paper links**: Optional for all (no TBA if empty)

### Location Rules
- **Past events**: No location information stored
- **Future events**: Room + Zoom info if available, otherwise "TBA"

## Running the Conversion Script

```bash
# Default usage (uses "NLP SIG (all previous talks from 2021) - Sheet1.csv")
python convert_events.py

# Custom filename
python convert_events.py your_custom_file.csv

# The script will:
# 1. Read and parse your CSV file
# 2. Convert dates to DD.MM.YYYY format
# 3. Skip "free for booking" slots
# 4. Generate meetings-data.json
```

## Script Features

- **Date Flexibility**: Handles various date formats (DD/MM/YYYY, DD-MM-YYYY, etc.)
- **Smart Filtering**: Automatically skips empty slots and "free for booking" entries
- **Data Cleaning**: Removes extra whitespace and normalizes text
- **Error Handling**: Provides clear feedback on any parsing issues
- **Sorting**: Orders meetings chronologically (most recent first)

## Output Format

The generated `meetings-data.json` follows this structure:

**Past events (before July 28, 2025):**
```json
{
  "date": "10.05.2025",
  "presenter": "Dr. Jane Smith",
  "title": "Advanced NLP Techniques", 
  "type": "seminar"
}
```

**Future events (after July 28, 2025):**
```json
{
  "date": "15.08.2025",
  "presenter": "Joseph Boyle", 
  "title": "Building Useful Agents",
  "type": "seminar",
  "location": "Ada Lovelace (Alan Turing Institute) & online",
  "abstract": "TBA",
  "presenterBio": "Joseph is a researcher at...",
  "paper_links": ["https://paper1.com", "https://paper2.com"]
}
```

**Journal club example:**
```json
{
  "date": "22.08.2025",
  "presenter": "Reading Group",
  "title": "Recent Advances in LLMs",
  "type": "journal_club",
  "location": "TBA",
  "abstract": "We'll discuss recent papers on..."
}
```

**Notes**: 
- Past events only include basic information
- Future seminars get "TBA" for abstract if empty
- Journal clubs don't include speaker bios
- Paper links and bios are optional (no "TBA" if empty)

## Website Integration

After generating the JSON file:

1. **Copy `meetings-data.json`** to the website root directory
2. **The website automatically**:
   - Loads the meeting data
   - Categorizes into "This Week", "Upcoming", and "Previous" 
   - Displays with proper formatting

## Troubleshooting

### Common Issues

**"Could not parse date" errors:**
- Ensure dates are in DD/MM/YYYY format in your spreadsheet
- Check for typos or invalid dates

**"Skipping entry" messages:**
- Normal for "free for booking" slots
- Check that required fields (Date, Presenter/Event Name) aren't empty

**Encoding problems:**
- The script handles UTF-8 encoding automatically
- Ensure your CSV is saved with proper encoding

### Getting Help

If you encounter issues:
1. Check the detailed console output for specific error messages
2. Verify your CSV format matches the expected structure
3. Contact the organizers if problems persist

## Meeting Schedule Context

- **Weekly meetings**: Every Thursday, 4-5pm UK time
- **Exception**: No meeting on the 3rd Thursday of each month  
- **Location**: Ada Lovelace meeting room (Alan Turing Institute) & online

## Organizers

For questions about this tool, contact:
**Anthony Hills, Guneet Singh Kohli, Yuxiang Zhou, Maria Liakata**