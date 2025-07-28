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
    """Convert date string to standardized format DD.MM.YYYY"""
    if not date_str or date_str.strip() == "":
        return None
    
    # Handle different date formats
    date_str = date_str.strip()
    
    # Try DD/MM/YYYY format first
    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        pass
    
    # Try DD-MM-YYYY format
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        pass
    
    # Try DD.MM.YYYY format (already correct)
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        return date_str
    except ValueError:
        pass
    
    # Try other common formats
    formats_to_try = ["%Y-%m-%d", "%m/%d/%Y", "%d %B %Y", "%d %b %Y"]
    for fmt in formats_to_try:
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
                    # Parse date
                    date_str = parse_date(row.get('Date', ''))
                    if not date_str:
                        print(f"Row {row_num}: Skipping entry with invalid date")
                        continue
                    
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
                    
                    # Create meeting object
                    meeting = {
                        "date": date_str,
                        "presenter": presenter if presenter else "TBA",
                        "title": event_name if event_name else "TBA",
                        "type": session_type,
                        "location": "Ada Lovelace meeting room (Alan Turing Institute) & online"
                    }
                    
                    # Add optional fields if they exist in the CSV
                    optional_fields = ['authors', 'abstract', 'presenterBio', 'paper_url']
                    for field in optional_fields:
                        if field in row and clean_text(row[field]):
                            meeting[field] = clean_text(row[field])
                    
                    # Handle special cases for TBA events
                    if event_name.upper() == 'TBA' and presenter not in ['', 'TBA']:
                        meeting['title'] = f"Talk by {presenter} (TBA)"
                    
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