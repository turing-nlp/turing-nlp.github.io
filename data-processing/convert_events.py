import json
import sys
from datetime import datetime

import pandas as pd


def clean_multiline_text(text):
    """Clean multiline text by removing extra whitespace and normalizing line breaks"""
    if pd.isna(text) or text == '':
        return ""
    
    # Convert to string and normalize whitespace
    text = str(text).strip()
    # Replace multiple whitespace with single space
    import re
    text = re.sub(r'\s+', ' ', text)
    return text

def convert_csv_to_json(csv_filename, output_filename=None):
    """Convert CSV to meetings-data.json format"""
    
    if output_filename is None:
        output_filename = "meetings-data.json"
    
    try:
        # Try reading with different encoding and robust CSV parsing
        print(f"Attempting to read CSV file: {csv_filename}")
        
        # Try multiple CSV reading strategies
        df = None
        reading_strategies = [
            # Strategy 1: Standard pandas with robust settings
            {
                'encoding': 'utf-8',
                'quotechar': '"',
                'escapechar': '\\',
                'skipinitialspace': True,
                'on_bad_lines': 'skip'
            },
            # Strategy 2: More permissive settings
            {
                'encoding': 'utf-8',
                'quotechar': '"',
                'skipinitialspace': True,
                'on_bad_lines': 'skip',
                'doublequote': True,
                'quoting': 1  # QUOTE_ALL
            },
            # Strategy 3: Try with different delimiter detection
            {
                'encoding': 'utf-8',
                'sep': None,  # Auto-detect
                'engine': 'python',
                'on_bad_lines': 'skip'
            }
        ]
        
        for i, strategy in enumerate(reading_strategies):
            try:
                print(f"Trying reading strategy {i+1}...")
                df = pd.read_csv(csv_filename, **strategy)
                print(f"Success with strategy {i+1}")
                break
            except Exception as e:
                print(f"Strategy {i+1} failed: {e}")
                continue
        
        if df is None:
            raise Exception("All reading strategies failed")
        
        print(f"Successfully read CSV with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        meetings = []
        
        for index, row in df.iterrows():
            # Check if the date field actually contains a date
            date_str = str(row['Date']).strip()
            
            # Skip if date field doesn't look like a date
            if not any(char.isdigit() for char in date_str) or len(date_str) > 50:
                print(f"Skipping row {index}: Invalid date format: '{date_str[:50]}...'")
                continue
            
            # Skip rows that are marked as 'free for booking' or have no presenter
            if (pd.isna(row.get('Presenter', '')) or 
                str(row.get('Presenter', '')).strip() == '' or
                'free for booking' in str(row.get('Presenter', '')).lower() or
                str(row.get('Presenter', '')).strip() == 'TBA'):
                continue
            
            # Parse various date formats to DD.MM.YYYY format
            # Before 4/10/2022: MM/DD/YYYY format
            # From 4/10/2022 onwards: DD/MM/YYYY or DD.MM.YY format
            date_obj = None
            
            try:
                # First, try to parse in different formats to determine which period this date belongs to
                potential_us_date = None
                potential_uk_date = None
                
                # Try MM/DD/YYYY (US format)
                try:
                    potential_us_date = datetime.strptime(date_str, '%m/%d/%Y')
                except ValueError:
                    pass
                
                # Try DD/MM/YYYY (UK format) 
                try:
                    potential_uk_date = datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    pass
                
                transition_date = datetime(2022, 10, 4)  # 4/10/2022
                
                # If we have a potential US date and it's before transition, use US format
                if potential_us_date and potential_us_date < transition_date:
                    date_obj = potential_us_date
                # For dates after transition, prefer DD/MM/YYYY but handle edge cases
                elif potential_uk_date:
                    date_obj = potential_uk_date
                elif potential_us_date:
                    # Edge case: date could be parsed as US but is after transition
                    # Check if it makes sense as DD/MM (e.g., 11/27 would be invalid as DD/MM)
                    try:
                        # Try parsing as DD/MM/YYYY first
                        test_date = datetime.strptime(date_str, '%d/%m/%Y')
                        date_obj = test_date
                    except ValueError:
                        # If DD/MM fails, use the US parsing
                        date_obj = potential_us_date
                else:
                    # Try other post-transition formats
                    post_transition_formats = [
                        '%d.%m.%Y',    # 30.10.2025  
                        '%d.%m.%y',    # 21.09.23
                        '%d/%m/%y',    # 21/09/23
                    ]
                    
                    for date_format in post_transition_formats:
                        try:
                            date_obj = datetime.strptime(date_str, date_format)
                            break
                        except ValueError:
                            continue
                
                if date_obj is None:
                    print(f"Skipping row {index}: Unrecognized date format: '{date_str}'")
                    continue
                    
                date_formatted = date_obj.strftime('%d.%m.%Y')
                
            except Exception as e:
                print(f"Skipping row {index}: Error parsing date '{date_str}': {e}")
                continue
            
            # Create meeting entry
            meeting = {
                "date": date_formatted,
                "presenter": clean_multiline_text(row.get('Presenter', '')),
                "title": clean_multiline_text(row.get('Event Name', '')),
                "abstract": clean_multiline_text(row.get('Abstract', '')),
                "location": clean_multiline_text(row.get('Room', 'TBA')) + " (Alan Turing Institute) & online"
            }
            
            # Add optional fields if they exist and are not empty
            if 'Bio for Speaker' in row and not pd.isna(row['Bio for Speaker']):
                bio = clean_multiline_text(row['Bio for Speaker'])
                if bio:
                    meeting["presenterBio"] = bio
            
            # Handle paper links if they exist
            if 'Paper Links' in row and not pd.isna(row['Paper Links']):
                links = clean_multiline_text(row['Paper Links'])
                if links and links not in ['', 'TBA']:
                    meeting["paperLinks"] = links
            
            # Only add meeting if it has essential information
            if meeting["presenter"] and meeting["title"]:
                meetings.append(meeting)
        
        # Sort meetings by date (newest first)
        meetings.sort(key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'), reverse=True)
        
        # Create output structure
        output_data = {"meetings": meetings}
        
        # Write to JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Successfully converted {len(meetings)} meetings to {output_filename}")
        print(f"📅 Date range: {meetings[-1]['date'] if meetings else 'N/A'} to {meetings[0]['date'] if meetings else 'N/A'}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: File '{csv_filename}' not found.")
        print("Make sure the CSV file exists in the current directory.")
        return False
        
    except pd.errors.EmptyDataError:
        print("❌ Error: The CSV file is empty.")
        return False
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the CSV file has proper headers")
        print("2. Check that multiline fields are properly quoted")
        print("3. Ensure the file is saved in UTF-8 encoding")
        print("4. Try opening the CSV in Excel and re-saving it")
        return False

def main():
    # Get filename from command line argument or use default
    if len(sys.argv) > 1:
        csv_filename = sys.argv[1]
    else:
        csv_filename = "NLP SIG (all previous talks from 2021) - Sheet1.csv"
        print(f"No filename provided, using default: {csv_filename}")
    
    print("Converting CSV to meetings-data.json format...")
    print("=" * 50)
    
    success = convert_csv_to_json(csv_filename)
    
    if not success:
        print("\n💡 If you're still having issues, try:")
        print("1. Open the CSV in a text editor and check for malformed quotes")
        print("2. Make sure multiline content is properly enclosed in quotes")
        print("3. Save the file with UTF-8 encoding")
        print("4. Run: python convert_events.py your-filename.csv")

if __name__ == "__main__":
    main()