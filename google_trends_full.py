#!/usr/bin/env python3
"""
Production script to check Google Trends for all keywords with better rate limiting
"""

import time
import csv
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import random
import sys

def check_google_trends_full(keywords_file, output_file, batch_size=2, delay_range=(5, 10), max_retries=3):
    """
    Check Google Trends for all keywords with robust error handling
    
    Args:
        keywords_file: Path to file containing keywords (one per line)
        output_file: Path to save results CSV
        batch_size: Number of keywords to check at once (smaller for better rate limiting)
        delay_range: Tuple of min and max delay between requests
        max_retries: Maximum number of retries for failed requests
    """
    
    # Initialize pytrends
    pytrends = TrendReq(hl='en-US', tz=360)
    
    # Read keywords from file
    with open(keywords_file, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(keywords)} keywords to check")
    print(f"Estimated time: {len(keywords) // batch_size * 7.5 / 60:.1f} minutes")
    print(f"Using batch size: {batch_size}, delay range: {delay_range}")
    
    results = []
    failed_keywords = []
    processed_count = 0
    
    # Check if we should resume from existing file
    try:
        existing_df = pd.read_csv(output_file)
        processed_keywords = set(existing_df['keyword'].tolist())
        keywords = [k for k in keywords if k not in processed_keywords]
        results = existing_df.to_dict('records')
        print(f"Resuming from existing file. {len(processed_keywords)} already processed.")
        print(f"Remaining keywords to process: {len(keywords)}")
    except FileNotFoundError:
        print("Starting fresh analysis...")
    
    # Process keywords in batches
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i+batch_size]
        processed_count += len(batch)
        progress = (processed_count / len(keywords)) * 100 if keywords else 100
        
        print(f"Processing batch {i//batch_size + 1}/{(len(keywords) + batch_size - 1)//batch_size} ({progress:.1f}%): {batch}")
        
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # Build payload for this batch
                pytrends.build_payload(batch, cat=0, timeframe='today 12-m', geo='', gprop='')
                
                # Get interest over time data
                interest_over_time = pytrends.interest_over_time()
                
                if not interest_over_time.empty:
                    # Calculate average interest for each keyword
                    for keyword in batch:
                        if keyword in interest_over_time.columns:
                            avg_interest = interest_over_time[keyword].mean()
                            max_interest = interest_over_time[keyword].max()
                            min_interest = interest_over_time[keyword].min()
                            
                            # Skip related queries to avoid rate limiting issues
                            top_queries_count = 0
                            rising_queries_count = 0
                            
                            results.append({
                                'keyword': keyword,
                                'avg_interest': round(avg_interest, 2),
                                'max_interest': max_interest,
                                'min_interest': min_interest,
                                'trend_score': round(avg_interest, 2),
                                'top_related_count': top_queries_count,
                                'rising_related_count': rising_queries_count,
                                'has_trend_data': True,
                                'checked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                            
                            print(f"  ✓ {keyword}: {avg_interest:.2f}")
                        else:
                            # Keyword not found in results
                            results.append({
                                'keyword': keyword,
                                'avg_interest': 0,
                                'max_interest': 0,
                                'min_interest': 0,
                                'trend_score': 0,
                                'top_related_count': 0,
                                'rising_related_count': 0,
                                'has_trend_data': False,
                                'checked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                            print(f"  ✗ {keyword}: No data")
                else:
                    # No data for any keyword in batch
                    for keyword in batch:
                        results.append({
                            'keyword': keyword,
                            'avg_interest': 0,
                            'max_interest': 0,
                            'min_interest': 0,
                            'trend_score': 0,
                            'top_related_count': 0,
                            'rising_related_count': 0,
                            'has_trend_data': False,
                            'checked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        print(f"  ✗ {keyword}: No data in batch")
                
                success = True
                
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                print(f"  Error (attempt {retry_count}/{max_retries}): {error_msg}")
                
                if retry_count < max_retries:
                    # Exponential backoff for retries
                    wait_time = (2 ** retry_count) * 10
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # Max retries reached, mark as failed
                    failed_keywords.extend(batch)
                    for keyword in batch:
                        results.append({
                            'keyword': keyword,
                            'avg_interest': 0,
                            'max_interest': 0,
                            'min_interest': 0,
                            'trend_score': 0,
                            'top_related_count': 0,
                            'rising_related_count': 0,
                            'has_trend_data': False,
                            'checked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'error': error_msg
                        })
                    print(f"  Failed after {max_retries} attempts")
        
        # Save progress after each batch
        if success or retry_count >= max_retries:
            df = pd.DataFrame(results)
            df.to_csv(output_file, index=False)
            print(f"  Progress saved to {output_file}")
        
        # Random delay between requests to avoid rate limiting
        if i + batch_size < len(keywords):
            delay = random.uniform(delay_range[0], delay_range[1])
            print(f"  Waiting {delay:.1f} seconds...\n")
            time.sleep(delay)
    
    # Final save and summary
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    # Print summary
    print(f"\n=== GOOGLE TRENDS ANALYSIS SUMMARY ===")
    print(f"Total keywords processed: {len(df)}")
    print(f"Keywords with trend data: {df['has_trend_data'].sum()}")
    print(f"Keywords without trend data: {(~df['has_trend_data']).sum()}")
    print(f"Failed keywords: {len(failed_keywords)}")
    
    # Show top trending keywords
    trending_keywords = df[df['trend_score'] > 0].sort_values('trend_score', ascending=False)
    
    print(f"\n=== TOP 20 TRENDING KEYWORDS ===")
    for idx, row in trending_keywords.head(20).iterrows():
        print(f"{row['keyword']}: {row['trend_score']} (max: {row['max_interest']})")
    
    # Show statistics
    if len(trending_keywords) > 0:
        print(f"\n=== TRENDING STATISTICS ===")
        print(f"Keywords with trend score > 0: {len(trending_keywords)}")
        print(f"Keywords with trend score > 10: {len(trending_keywords[trending_keywords['trend_score'] > 10])}")
        print(f"Keywords with trend score > 50: {len(trending_keywords[trending_keywords['trend_score'] > 50])}")
        print(f"Average trend score: {trending_keywords['trend_score'].mean():.2f}")
        print(f"Median trend score: {trending_keywords['trend_score'].median():.2f}")
    
    print(f"\nResults saved to: {output_file}")
    
    if failed_keywords:
        print(f"\nFailed keywords: {len(failed_keywords)} total")
    
    return df

def create_trending_report(csv_file, min_trend_score=10):
    """Create a summary report of trending keywords"""
    
    df = pd.read_csv(csv_file)
    
    # Filter trending keywords
    trending = df[
        (df['trend_score'] >= min_trend_score) & 
        (df['has_trend_data'] == True)
    ].sort_values('trend_score', ascending=False)
    
    print(f"\n=== TRENDING KEYWORDS REPORT (Score >= {min_trend_score}) ===")
    print(f"Found {len(trending)} trending keywords out of {len(df)} total")
    
    if len(trending) > 0:
        # Save trending keywords to separate file
        trending_file = csv_file.replace('.csv', '_trending.csv')
        trending.to_csv(trending_file, index=False)
        
        # Create a summary text file
        summary_file = csv_file.replace('.csv', '_summary.txt')
        with open(summary_file, 'w') as f:
            f.write(f"Google Trends Analysis Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total keywords analyzed: {len(df)}\n")
            f.write(f"Keywords with trend data: {df['has_trend_data'].sum()}\n")
            f.write(f"Trending keywords (score >= {min_trend_score}): {len(trending)}\n\n")
            f.write("Top Trending Keywords:\n")
            f.write("-" * 50 + "\n")
            
            for idx, row in trending.head(50).iterrows():
                f.write(f"{row['keyword']}: {row['trend_score']}\n")
        
        print(f"Trending keywords saved to: {trending_file}")
        print(f"Summary report saved to: {summary_file}")
        
        # Show top trending
        for idx, row in trending.head(20).iterrows():
            print(f"• {row['keyword']}: {row['trend_score']}")
    
    return trending

if __name__ == "__main__":
    # File paths
    keywords_file = "filtered-output-keywords.txt"
    trends_output = "google_trends_full_results.csv"
    
    print("Starting comprehensive Google Trends analysis...")
    print("This will take several hours to complete all keywords.")
    print("Progress will be saved after each batch.")
    
    # Ask for confirmation
    response = input("\nProceed with full analysis? (y/N): ")
    if response.lower() != 'y':
        print("Analysis cancelled.")
        sys.exit(0)
    
    # Check trends for all keywords
    trends_df = check_google_trends_full(
        keywords_file=keywords_file,
        output_file=trends_output,
        batch_size=2,  # Very conservative batch size
        delay_range=(8, 15),  # Longer delays to avoid rate limiting
        max_retries=3
    )
    
    # Create trending report
    trending_df = create_trending_report(
        csv_file=trends_output,
        min_trend_score=10
    )
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
