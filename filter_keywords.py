#!/usr/bin/env python3
"""
Script to filter output-keywords.txt to only include lines that contain
keywords from input-keywords.txt
"""

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

def filter_output_keywords(input_keywords, output_file, filtered_output_file):
    """Filter output keywords to only include those containing input keywords"""
    matched_lines = []
    total_lines = 0
    
    try:
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
        
        # Write filtered results to new file
        with open(filtered_output_file, 'w', encoding='utf-8') as f:
            for line in matched_lines:
                f.write(line + '\n')
        
        print(f"Filtered keywords written to: {filtered_output_file}")
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
    filtered_output_file = 'filtered-output-keywords.txt'
    
    print("Starting keyword filtering process...")
    print(f"Input keywords file: {input_file}")
    print(f"Output keywords file: {output_file}")
    print(f"Filtered output file: {filtered_output_file}")
    print("-" * 50)
    
    # Load input keywords
    input_keywords = load_input_keywords(input_file)
    if not input_keywords:
        print("No input keywords found. Exiting.")
        return
    
    print("Input keywords:")
    for keyword in input_keywords:
        print(f"  - {keyword}")
    print("-" * 50)
    
    # Filter output keywords
    success = filter_output_keywords(input_keywords, output_file, filtered_output_file)
    
    if success:
        print("Filtering completed successfully!")
        
        # Show some statistics
        try:
            with open(filtered_output_file, 'r') as f:
                filtered_count = sum(1 for line in f if line.strip())
            print(f"Final filtered keywords count: {filtered_count}")
        except:
            pass
    else:
        print("Filtering failed!")

if __name__ == "__main__":
    main()
