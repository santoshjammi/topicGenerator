#!/usr/bin/env python3
"""
Script to filter output-keywords.txt in-place to only include lines that contain
keywords from input-keywords.txt
"""

import shutil
import os

def load_input_keywords(input_file):
    """Load and clean keywords from input file"""
    keywords = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                keyword = line.strip()
                if keyword:  # Skip empty lines
                    keywords.append(keyword.lower())  # Convert to lowercase for case-insensitive matching
        print(f"Loaded {len(keywords)} input keywords")
        return keywords
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
        return []
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return []

def filter_and_replace_output_keywords(input_keywords, output_file):
    """Filter output keywords in-place to only include those containing input keywords"""
    matched_lines = []
    total_lines = 0
    backup_file = output_file + '.backup'
    
    try:
        # Create backup first
        shutil.copy2(output_file, backup_file)
        print(f"Backup created: {backup_file}")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                line_stripped = line.strip()
                if line_stripped:  # Skip empty lines
                    line_lower = line_stripped.lower()
                    # Check if any input keyword is contained in this line
                    for keyword in input_keywords:
                        if keyword in line_lower:
                            matched_lines.append(line_stripped)
                            break  # Found a match, no need to check other keywords for this line
        
        print(f"Total lines processed: {total_lines}")
        print(f"Matched lines: {len(matched_lines)}")
        
        # Write filtered results back to original file
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in matched_lines:
                f.write(line + '\n')
        
        print(f"Original file updated: {output_file}")
        print(f"Backup available at: {backup_file}")
        return True
        
    except FileNotFoundError:
        print(f"Error: {output_file} not found")
        return False
    except Exception as e:
        print(f"Error processing files: {e}")
        return False

def main():
    input_file = 'input-keywords.txt'
    output_file = 'output-keywords.txt'
    
    print("Starting in-place keyword filtering process...")
    print(f"Input keywords file: {input_file}")
    print(f"Output keywords file: {output_file}")
    print("=" * 60)
    
    # Load input keywords
    input_keywords = load_input_keywords(input_file)
    if not input_keywords:
        print("No input keywords found. Exiting.")
        return
    
    print("Input keywords:")
    for keyword in input_keywords:
        print(f"  - {keyword}")
    print("=" * 60)
    
    # Confirm before proceeding
    response = input("This will modify the original output-keywords.txt file. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Filter output keywords in-place
    success = filter_and_replace_output_keywords(input_keywords, output_file)
    
    if success:
        print("=" * 60)
        print("Filtering completed successfully!")
        print("The original output-keywords.txt has been updated with filtered content.")
        print("A backup of the original file has been created as output-keywords.txt.backup")
    else:
        print("Filtering failed!")

if __name__ == "__main__":
    main()
