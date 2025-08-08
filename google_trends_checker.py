#!/usr/bin/env python3
"""
Script to check Google Trends for keywords and identify trending keywords
"""

import time
import csv
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import random

def check_google_trends(keywords_file, output_file, batch_size=5, delay_range=(1, 3)):
    """
    Check Google Trends for keywords and save results with ranking data
    
    Args:
        keywords_file: Path to file containing keywords (one per line)
        output_file: Path to save results CSV
        batch_size: Number of keywords to check at once
        delay_range: Tuple of min and max delay between requests
    """
    
    # Initialize pytrends
    pytrends = TrendReq(hl='en-US', tz=360)
    
    # Read keywords from file
    with open(keywords_file, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(keywords)} keywords to check")
    
    results = []
    failed_keywords = []
    
    # Process keywords in batches
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}: {batch}")
        
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
                        
                        # Get related queries if available
                        try:
                            related_queries = pytrends.related_queries()
                            top_related = related_queries.get(keyword, {}).get('top', pd.DataFrame())
                            rising_related = related_queries.get(keyword, {}).get('rising', pd.DataFrame())
                            
                            top_queries_count = len(top_related) if not top_related.empty else 0
                            rising_queries_count = len(rising_related) if not rising_related.empty else 0
                        except:
                            top_queries_count = 0
                            rising_queries_count = 0
                        
                        results.append({
                            'keyword': keyword,
                            'avg_interest': round(avg_interest, 2),
                            'max_interest': max_interest,
                            'min_interest': min_interest,
                            'trend_score': round(avg_interest, 2),  # Using avg as trend score
                            'top_related_count': top_queries_count,
                            'rising_related_count': rising_queries_count,
                            'has_trend_data': True,
                            'checked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
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
                    
        except Exception as e:
            print(f"Error processing batch {batch}: {e}")
            failed_keywords.extend(batch)
            
            # Add failed keywords to results with zero data
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
                    'error': str(e)
                })
        
        # Random delay between requests to avoid rate limiting
        if i + batch_size < len(keywords):
            delay = random.uniform(delay_range[0], delay_range[1])
            print(f"Waiting {delay:.1f} seconds...")
            time.sleep(delay)
    
    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    # Print summary
    print(f"\n=== GOOGLE TRENDS ANALYSIS SUMMARY ===")
    print(f"Total keywords checked: {len(keywords)}")
    print(f"Keywords with trend data: {df['has_trend_data'].sum()}")
    print(f"Keywords without trend data: {(~df['has_trend_data']).sum()}")
    print(f"Failed keywords: {len(failed_keywords)}")
    
    # Show top trending keywords
    trending_keywords = df[df['trend_score'] > 0].sort_values('trend_score', ascending=False)
    
    print(f"\n=== TOP 20 TRENDING KEYWORDS ===")
    for idx, row in trending_keywords.head(20).iterrows():
        print(f"{row['keyword']}: {row['trend_score']} (max: {row['max_interest']})")
    
    # Show keywords with rising trends
    rising_keywords = df[df['rising_related_count'] > 0].sort_values('rising_related_count', ascending=False)
    
    if not rising_keywords.empty:
        print(f"\n=== KEYWORDS WITH RISING RELATED QUERIES ===")
        for idx, row in rising_keywords.head(10).iterrows():
            print(f"{row['keyword']}: {row['rising_related_count']} rising queries")
    
    print(f"\nResults saved to: {output_file}")
    
    if failed_keywords:
        print(f"\nFailed keywords: {failed_keywords}")
    
    return df

def filter_trending_keywords(csv_file, min_trend_score=10, output_file=None):
    """
    Filter and display keywords that meet trending criteria
    
    Args:
        csv_file: Path to CSV file with trends data
        min_trend_score: Minimum trend score to consider as "trending"
        output_file: Optional path to save filtered results
    """
    
    df = pd.read_csv(csv_file)
    
    # Filter trending keywords
    trending = df[
        (df['trend_score'] >= min_trend_score) & 
        (df['has_trend_data'] == True)
    ].sort_values('trend_score', ascending=False)
    
    print(f"\n=== TRENDING KEYWORDS (Score >= {min_trend_score}) ===")
    print(f"Found {len(trending)} trending keywords:")
    
    for idx, row in trending.iterrows():
        print(f"• {row['keyword']}: {row['trend_score']} (max: {row['max_interest']}, related: {row['top_related_count']})")
    
    if output_file:
        trending.to_csv(output_file, index=False)
        print(f"\nTrending keywords saved to: {output_file}")
    
    return trending

if __name__ == "__main__":
    # File paths
    keywords_file = "filtered-output-keywords.txt"
    trends_output = "google_trends_results.csv"
    trending_output = "trending_keywords.csv"
    
    print("Starting Google Trends analysis...")
    print("Note: This will take a while due to API rate limits")
    
    # Check trends for all keywords
    trends_df = check_google_trends(
        keywords_file=keywords_file,
        output_file=trends_output,
        batch_size=3,  # Smaller batch size to avoid rate limits
        delay_range=(2, 5)  # Longer delays between requests
    )
    
    # Filter and display trending keywords
    trending_df = filter_trending_keywords(
        csv_file=trends_output,
        min_trend_score=10,
        output_file=trending_output
    )
    
    print("\nAnalysis complete!")
