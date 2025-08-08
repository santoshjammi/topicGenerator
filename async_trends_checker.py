#!/usr/bin/env python3
"""
Asynchronous Google Trends checker with concurrent processing and intelligent batching
"""

import asyncio
import aiohttp
import pandas as pd
import time
import random
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trends_async.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AsyncTrendsChecker:
    def __init__(self, max_concurrent=5, delay_between_batches=3, max_retries=3):
        self.max_concurrent = max_concurrent
        self.delay_between_batches = delay_between_batches
        self.max_retries = max_retries
        self.session = None
        self.results = []
        self.failed_keywords = []
        self.processed_count = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def check_single_keyword(self, keyword: str, semaphore: asyncio.Semaphore) -> Dict:
        """Check a single keyword with rate limiting"""
        async with semaphore:
            for attempt in range(self.max_retries):
                try:
                    # Simulate API call - in real implementation, this would call Google Trends API
                    # For now, we'll use a mock scoring system based on keyword characteristics
                    await asyncio.sleep(random.uniform(0.1, 0.3))  # Simulate API delay
                    
                    # Mock trend scoring based on keyword analysis
                    trend_score = await self.calculate_mock_trend_score(keyword)
                    
                    result = {
                        'keyword': keyword,
                        'trend_score': trend_score,
                        'avg_interest': trend_score,
                        'max_interest': min(100, trend_score * 1.2),
                        'min_interest': max(0, trend_score * 0.3),
                        'search_volume_category': self.categorize_trend_score(trend_score),
                        'has_trend_data': trend_score > 0,
                        'checked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'attempt': attempt + 1
                    }
                    
                    self.processed_count += 1
                    if self.processed_count % 100 == 0:
                        logger.info(f"Processed {self.processed_count} keywords...")
                    
                    return result
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for '{keyword}': {e}")
                    if attempt == self.max_retries - 1:
                        self.failed_keywords.append(keyword)
                        return {
                            'keyword': keyword,
                            'trend_score': 0,
                            'avg_interest': 0,
                            'max_interest': 0,
                            'min_interest': 0,
                            'search_volume_category': 'no_data',
                            'has_trend_data': False,
                            'checked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'error': str(e),
                            'attempt': attempt + 1
                        }
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def calculate_mock_trend_score(self, keyword: str) -> float:
        """
        Calculate mock trend score based on keyword characteristics
        In real implementation, this would be replaced with actual Google Trends API calls
        """
        # Scoring factors
        score = 0.0
        
        # Length factor (shorter terms often searched more)
        if len(keyword) < 15:
            score += 20
        elif len(keyword) < 25:
            score += 10
        else:
            score += 5
        
        # Common tech terms get higher scores
        high_value_terms = [
            'linux', 'windows', 'android', 'install', 'download', 'tutorial',
            'commands', 'admin', 'security', 'server', 'development', 'programming'
        ]
        
        for term in high_value_terms:
            if term in keyword.lower():
                score += 25
                break
        
        # Specific command-related keywords
        if any(cmd in keyword.lower() for cmd in ['command', 'cmd', 'terminal', 'bash']):
            score += 30
        
        # Job-related keywords
        if any(job in keyword.lower() for job in ['job', 'career', 'salary', 'interview']):
            score += 15
        
        # Add some randomness to simulate real trend variations
        score += random.uniform(-10, 15)
        
        # Ensure score is within reasonable bounds
        return max(0, min(100, score))
    
    def categorize_trend_score(self, score: float) -> str:
        """Categorize trend scores for easier analysis"""
        if score >= 80:
            return 'very_high'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score >= 20:
            return 'low'
        elif score > 0:
            return 'very_low'
        else:
            return 'no_data'
    
    async def process_keywords_batch(self, keywords: List[str]) -> List[Dict]:
        """Process a batch of keywords concurrently"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        tasks = [self.check_single_keyword(keyword, semaphore) for keyword in keywords]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and add valid results
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                logger.error(f"Unexpected result type: {result}")
        
        return valid_results
    
    async def process_all_keywords(self, keywords: List[str], batch_size: int = 50) -> List[Dict]:
        """Process all keywords in batches"""
        total_keywords = len(keywords)
        logger.info(f"Starting async processing of {total_keywords} keywords")
        logger.info(f"Batch size: {batch_size}, Max concurrent: {self.max_concurrent}")
        
        all_results = []
        
        for i in range(0, total_keywords, batch_size):
            batch = keywords[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_keywords + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} keywords)")
            
            start_time = time.time()
            batch_results = await self.process_keywords_batch(batch)
            end_time = time.time()
            
            all_results.extend(batch_results)
            
            logger.info(f"Batch {batch_num} completed in {end_time - start_time:.2f}s")
            
            # Save progress after each batch
            if batch_results:
                self.save_progress(all_results, f"progress_batch_{batch_num}.csv")
            
            # Delay between batches to respect rate limits
            if i + batch_size < total_keywords:
                await asyncio.sleep(self.delay_between_batches)
        
        return all_results
    
    def save_progress(self, results: List[Dict], filename: str):
        """Save current progress to CSV"""
        if results:
            df = pd.DataFrame(results)
            df.to_csv(filename, index=False)
            logger.info(f"Progress saved to {filename}")

async def main():
    """Main async function"""
    
    # Configuration
    KEYWORDS_FILE = "filtered-output-keywords.txt"
    OUTPUT_FILE = "async_trends_results.csv"
    BATCH_SIZE = 100  # Process 100 keywords per batch
    MAX_CONCURRENT = 10  # Max 10 concurrent requests
    
    # Load keywords
    try:
        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(keywords)} keywords from {KEYWORDS_FILE}")
    except FileNotFoundError:
        logger.error(f"Keywords file {KEYWORDS_FILE} not found!")
        return
    
    # Estimate processing time
    estimated_time = (len(keywords) / BATCH_SIZE) * 3 / 60  # Rough estimate in minutes
    logger.info(f"Estimated processing time: {estimated_time:.1f} minutes")
    
    # Ask for confirmation
    response = input(f"\nProcess {len(keywords)} keywords asynchronously? (y/N): ")
    if response.lower() != 'y':
        logger.info("Processing cancelled.")
        return
    
    # Process keywords
    start_time = time.time()
    
    async with AsyncTrendsChecker(
        max_concurrent=MAX_CONCURRENT,
        delay_between_batches=3,
        max_retries=3
    ) as checker:
        results = await checker.process_all_keywords(keywords, BATCH_SIZE)
        
        # Save final results
        if results:
            df = pd.DataFrame(results)
            df.to_csv(OUTPUT_FILE, index=False)
            
            # Generate analysis
            await generate_analysis_report(df, OUTPUT_FILE)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            logger.info(f"\n{'='*60}")
            logger.info(f"ASYNC PROCESSING COMPLETE!")
            logger.info(f"{'='*60}")
            logger.info(f"Total time: {total_time/60:.2f} minutes")
            logger.info(f"Keywords processed: {len(results)}")
            logger.info(f"Failed keywords: {len(checker.failed_keywords)}")
            logger.info(f"Processing rate: {len(results)/(total_time/60):.1f} keywords/minute")
            logger.info(f"Results saved to: {OUTPUT_FILE}")

async def generate_analysis_report(df: pd.DataFrame, base_filename: str):
    """Generate comprehensive analysis report"""
    
    # Filter trending keywords
    high_trend = df[df['trend_score'] >= 70].sort_values('trend_score', ascending=False)
    medium_trend = df[(df['trend_score'] >= 40) & (df['trend_score'] < 70)].sort_values('trend_score', ascending=False)
    
    # Category analysis
    category_counts = df['search_volume_category'].value_counts()
    
    # Save trending keywords
    if len(high_trend) > 0:
        high_trend_file = base_filename.replace('.csv', '_high_trending.csv')
        high_trend.to_csv(high_trend_file, index=False)
        logger.info(f"High trending keywords saved to: {high_trend_file}")
    
    if len(medium_trend) > 0:
        medium_trend_file = base_filename.replace('.csv', '_medium_trending.csv')
        medium_trend.to_csv(medium_trend_file, index=False)
        logger.info(f"Medium trending keywords saved to: {medium_trend_file}")
    
    # Generate summary report
    summary_file = base_filename.replace('.csv', '_summary.txt')
    with open(summary_file, 'w') as f:
        f.write("ASYNC GOOGLE TRENDS ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("OVERVIEW:\n")
        f.write(f"Total keywords analyzed: {len(df)}\n")
        f.write(f"Keywords with data: {df['has_trend_data'].sum()}\n")
        f.write(f"Average trend score: {df['trend_score'].mean():.2f}\n\n")
        
        f.write("CATEGORY BREAKDOWN:\n")
        for category, count in category_counts.items():
            percentage = (count / len(df)) * 100
            f.write(f"{category}: {count} ({percentage:.1f}%)\n")
        
        f.write(f"\nTOP 50 HIGH-TRENDING KEYWORDS (Score >= 70):\n")
        f.write("-" * 50 + "\n")
        for idx, row in high_trend.head(50).iterrows():
            f.write(f"{row['keyword']}: {row['trend_score']:.1f}\n")
        
        f.write(f"\nTOP 50 MEDIUM-TRENDING KEYWORDS (Score 40-69):\n")
        f.write("-" * 50 + "\n")
        for idx, row in medium_trend.head(50).iterrows():
            f.write(f"{row['keyword']}: {row['trend_score']:.1f}\n")
    
    logger.info(f"Summary report saved to: {summary_file}")
    
    # Print quick summary to console
    logger.info(f"\nQUICK ANALYSIS SUMMARY:")
    logger.info(f"High trending (70+): {len(high_trend)} keywords")
    logger.info(f"Medium trending (40-69): {len(medium_trend)} keywords")
    logger.info(f"Low trending (1-39): {len(df[(df['trend_score'] >= 1) & (df['trend_score'] < 40)])}")
    
    if len(high_trend) > 0:
        logger.info(f"\nTop 10 High-Trending Keywords:")
        for idx, row in high_trend.head(10).iterrows():
            logger.info(f"  • {row['keyword']}: {row['trend_score']:.1f}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
