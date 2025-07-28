#!/usr/bin/env python3
"""
Google Sheets to JSON Converter for Alan Turing Institute NLP Special Interest Group
Converts exported CSV data to JSON format required by the website.

Usage:
1. Download your Google Sheets as CSV (File > Download > CSV)
2. Place the CSV file in the same directory as this script (should be named "NLP SIG (all previous talks from 2021) - Sheet1.csv")
3. Run: python convert_events.py (uses default filename automatically)
   OR: python convert_events.py your_custom_filename.csv
4. Output will be saved as meetings-data.json
"""

import csv
import json
import re
import sys
from datetime import datetime


def parse_date(date_str):
    """Convert date string to standardized format DD.MM.YYYY
    
    Handles different date formats:
    - Before/including 9/29/2022: MM/DD/YYYY format
    - After 9/29/2022: DD/MM/YYYY or DD.MM.YYYY format
    """
    if not date_str or date_str.strip() == "":
        return None
    
    # Handle different date formats
    date_str = date_str.strip()
    
    # Cutoff date to determine format (9/29/2022)
    cutoff_date = datetime(2022, 9, 29)
    
    # Try DD.MM.YYYY format first (most common recent format)
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        return date_str  # Already in correct format
    except ValueError:
        pass
    
    # Try DD/MM/YYYY format (recent format)
    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        # Check if this date is after cutoff to confirm format
        if date_obj > cutoff_date:
            return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        pass
    
    # Try MM/DD/YYYY format (old format, before/including 9/29/2022)
    try:
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        # Only use this format for dates before/including cutoff
        if date_obj <= cutoff_date:
            return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        pass
    
    # Handle ambiguous dates by checking if they're in the old period
    # Try both formats and pick the most logical one
    try:
        # Try as MM/DD/YYYY first
        date_obj_mdy = datetime.strptime(date_str, "%m/%d/%Y")
        if date_obj_mdy <= cutoff_date:
            return date_obj_mdy.strftime("%d.%m.%Y")
    except ValueError:
        pass
    
    try:
        # Try as DD/MM/YYYY 
        date_obj_dmy = datetime.strptime(date_str, "%d/%m/%Y")
        if date_obj_dmy > cutoff_date:
            return date_obj_dmy.strftime("%d.%m.%Y")
    except ValueError:
        pass
    
    # Try other less common formats
    other_formats = [
        "%d-%m-%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y",
        "%m-%d-%Y"  # Alternative old format
    ]
    
    for fmt in other_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime("%d.%m.%Y")
        except ValueError:
            continue
    
    print(f"Warning: Could not parse date '{date_str}', skipping this entry")
    return None

def clean_text(text):
    """Clean and format text fields"""
    if not text or text.strip() == "":
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def determine_session_type(row):
    """Determine session type from the data"""
    type_field = clean_text(row.get('Type of Session', ''))
    event_name = clean_text(row.get('Event Name', ''))
    
    if type_field.lower() in ['seminar', 'talk', 'presentation']:
        return 'seminar'
    elif type_field.lower() in ['journal club', 'reading group']:
        return 'journal_club'
    elif 'reading group' in event_name.lower() or 'journal club' in event_name.lower():
        return 'journal_club'
    elif event_name.lower() in ['tba', 'to be announced', '']:
        return 'seminar'  # Default for TBA events
    else:
        return 'seminar'  # Default fallback

def is_free_slot(row):
    """Check if this is a free booking slot"""
    presenter = clean_text(row.get('Presenter', ''))
    event_name = clean_text(row.get('Event Name', ''))
    
    return (presenter.lower() == 'free for booking' or 
            event_name.lower() == 'free for booking' or
            (presenter == '' and event_name == ''))

def get_location_info(row, meeting_date):
    """Determine location information based on date and available data
    
    Rules:
    - For past events: return empty string
    - For future events: return room info if available, otherwise "TBA"
    """
    today = datetime.now()
    
    # If meeting is in the past, don't include location
    if meeting_date <= today:
        return ""
    
    # For future events, check for room/location information
    room_field = clean_text(row.get('Room', ''))
    zoom_field = clean_text(row.get('Zoom Link', ''))
    
    # Check if any location info is provided
    if room_field and zoom_field:
        return f"{room_field} (Alan Turing Institute) & online"
    elif room_field:
        return f"{room_field} (Alan Turing Institute) & online"
    elif zoom_field:
        return "Online (Zoom)"
    else:
        return "TBA"

def should_include_detailed_info(meeting_date):
    """Check if we should include detailed information (abstracts, bios, etc.)
    
    Only include detailed info for talks after July 28, 2025
    """
    cutoff_date = datetime(2025, 7, 28)
    return meeting_date > cutoff_date

def get_abstract_info(row, meeting_date, session_type):
    """Get abstract information based on rules
    
    Rules:
    - Before July 28, 2025: Don't include abstracts
    - After July 28, 2025: 
      - For seminars: Include if exists, otherwise "TBA"
      - For journal clubs: Include if exists, otherwise don't include
    """
    if not should_include_detailed_info(meeting_date):
        return None
    
    abstract = clean_text(row.get('Abstract', ''))
    
    if abstract:
        return abstract
    elif session_type == 'seminar':
        return "TBA"
    else:
        # Journal club - don't include if empty
        return None

def get_bio_info(row, meeting_date, session_type):
    """Get speaker bio information based on rules
    
    Rules:
    - Before July 28, 2025: Don't include bios
    - After July 28, 2025:
      - For seminars: Include if exists, otherwise don't include (no TBA)
      - For journal clubs: Don't include bios
    """
    if not should_include_detailed_info(meeting_date):
        return None
    
    if session_type != 'seminar':
        return None
    
    bio = clean_text(row.get('Bio for Speaker', ''))
    return bio if bio else None

def get_paper_links(row, meeting_date):
    """Get paper links information
    
    Rules:
    - Before July 28, 2025: Don't include paper links
    - After July 28, 2025: Include if exists, split by comma, no TBA if empty
    """
    if not should_include_detailed_info(meeting_date):
        return None
    
    paper_links = clean_text(row.get('Paper Links', ''))
    if paper_links:
        # Split by comma and clean up each link
        links = [link.strip() for link in paper_links.split(',') if link.strip()]
        return links if links else None
    return None

def convert_csv_to_json(csv_file_path, output_file_path='meetings-data.json'):
    """Convert CSV file to JSON format required by the website"""
    
    meetings = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for spreadsheet row numbers
                try:
                    # Parse date first to determine if it's future/past
                    date_str = parse_date(row.get('Date', ''))
                    if not date_str:
                        print(f"Row {row_num}: Skipping entry with invalid date")
                        continue
                    
                    # Convert to datetime object for comparison
                    meeting_date = datetime.strptime(date_str, "%d.%m.%Y")
                    
                    # Skip free booking slots
                    if is_free_slot(row):
                        print(f"Row {row_num}: Skipping free booking slot for {date_str}")
                        continue
                    
                    # Extract basic information
                    presenter = clean_text(row.get('Presenter', ''))
                    event_name = clean_text(row.get('Event Name', ''))
                    session_type = determine_session_type(row)
                    
                    if not presenter and not event_name:
                        print(f"Row {row_num}: Skipping entry with no presenter or event name")
                        continue
                    
                    # Get location info based on date
                    location = get_location_info(row, meeting_date)
                    
                    # Create meeting object
                    meeting = {
                        "date": date_str,
                        "presenter": presenter if presenter else "TBA",
                        "title": event_name if event_name else "TBA",
                        "type": session_type
                    }
                    
                    # Only add location if it's not empty (for future events)
                    if location:
                        meeting["location"] = location
                    
                    # Add detailed information based on date and rules
                    abstract = get_abstract_info(row, meeting_date, session_type)
                    if abstract is not None:
                        meeting["abstract"] = abstract
                    
                    bio = get_bio_info(row, meeting_date, session_type)
                    if bio is not None:
                        meeting["presenterBio"] = bio
                    
                    paper_links = get_paper_links(row, meeting_date)
                    if paper_links is not None:
                        meeting["paper_links"] = paper_links
                    
                    # Add other optional fields if they exist
                    other_optional_fields = ['authors']
                    for field in other_optional_fields:
                        if field in row and clean_text(row[field]):
                            meeting[field] = clean_text(row[field])
                    
                    meetings.append(meeting)
                    print(f"Row {row_num}: Added meeting - {date_str}: {presenter} - {event_name}")
                    
                except Exception as e:
                    print(f"Row {row_num}: Error processing row - {e}")
                    continue
    
    except FileNotFoundError:
        print(f"Error: Could not find file '{csv_file_path}'")
        return False
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
    
    # Sort meetings by date (most recent first for website display)
    try:
        meetings.sort(key=lambda x: datetime.strptime(x['date'], "%d.%m.%Y"), reverse=True)
    except Exception as e:
        print(f"Warning: Could not sort meetings by date - {e}")
    
    # Save to JSON file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(meetings, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully converted {len(meetings)} meetings to {output_file_path}")
        print(f"Date range: {meetings[-1]['date'] if meetings else 'N/A'} to {meetings[0]['date'] if meetings else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        return False

def main():
    # Default filename
    default_filename = "NLP SIG (all previous talks from 2021) - Sheet1.csv"
    
    if len(sys.argv) == 1:
        # No arguments provided, use default filename
        csv_file_path = default_filename
        print(f"No filename provided, using default: {default_filename}")
    elif len(sys.argv) == 2:
        # Custom filename provided
        csv_file_path = sys.argv[1]
    else:
        print("Usage: python convert_events.py [csv_file_path]")
        print(f"\nExamples:")
        print(f"  python convert_events.py                    # Uses default: {default_filename}")
        print(f"  python convert_events.py custom_file.csv    # Uses custom filename")
        sys.exit(1)
    
    print(f"Converting '{csv_file_path}' to JSON format...")
    print("=" * 50)
    
    success = convert_csv_to_json(csv_file_path)
    
    if success:
        print("=" * 50)
        print("Conversion completed successfully!")
        print("\nNext steps:")
        print("1. Review the generated meetings-data.json file")
        print("2. Upload it to your website's data directory")
        print("3. The website will automatically load and display the events")
    else:
        print("Conversion failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()