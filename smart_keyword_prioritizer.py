#!/usr/bin/env python3
"""
Smart Keyword Prioritizer - Asynchronous analysis for content strategy
Focus on identifying high-value keywords for article writing
"""

import asyncio
import pandas as pd
import time
import random
from datetime import datetime
import logging
from typing import List, Dict, Set
import re
import json
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keyword_prioritizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartKeywordPrioritizer:
    def __init__(self):
        self.processed_count = 0
        self.high_priority_keywords = []
        self.medium_priority_keywords = []
        self.low_priority_keywords = []
        
        # Define high-value indicators for content creation
        self.high_value_patterns = [
            # Tutorial/How-to content
            r'how to|tutorial|guide|step by step|install|setup|configuration',
            # Commands and technical
            r'command|commands|cmd|terminal|bash|shell|script',
            # Job/Career related
            r'job|jobs|career|salary|interview|certification|skills',
            # Beginner content
            r'beginner|basic|fundamentals|introduction|getting started',
            # Problem-solving content
            r'troubleshoot|error|fix|problem|issue|solution',
            # Comparison content
            r'vs|versus|difference|compare|comparison|alternative',
            # Tools and software
            r'tool|tools|software|application|download|free'
        ]
        
        # Keywords indicating high search intent
        self.search_intent_indicators = [
            'download', 'install', 'tutorial', 'how', 'guide', 'commands',
            'example', 'free', 'best', 'top', 'list', 'course', 'learn'
        ]
        
        # Technical depth indicators
        self.technical_depth = {
            'beginner': ['basic', 'beginner', 'introduction', 'getting started', 'fundamentals'],
            'intermediate': ['admin', 'configuration', 'setup', 'management', 'advanced'],
            'expert': ['kernel', 'system', 'architecture', 'development', 'programming']
        }
    
    def analyze_keyword_value(self, keyword: str) -> Dict:
        """Analyze keyword for content creation value"""
        
        # Base scoring
        score = 0
        content_type = 'general'
        difficulty = 'medium'
        search_intent = 'informational'
        
        keyword_lower = keyword.lower()
        
        # 1. High-value pattern matching
        for pattern in self.high_value_patterns:
            if re.search(pattern, keyword_lower):
                score += 25
                break
        
        # 2. Search intent analysis
        for indicator in self.search_intent_indicators:
            if indicator in keyword_lower:
                score += 15
                search_intent = 'high_intent'
                break
        
        # 3. Content type classification
        if any(word in keyword_lower for word in ['tutorial', 'guide', 'how', 'step']):
            content_type = 'tutorial'
            score += 20
        elif any(word in keyword_lower for word in ['command', 'commands', 'terminal']):
            content_type = 'reference'
            score += 15
        elif any(word in keyword_lower for word in ['job', 'career', 'salary']):
            content_type = 'career'
            score += 18
        elif any(word in keyword_lower for word in ['vs', 'versus', 'difference', 'compare']):
            content_type = 'comparison'
            score += 22
        
        # 4. Technical difficulty assessment
        if any(word in keyword_lower for word in self.technical_depth['beginner']):
            difficulty = 'beginner'
            score += 25  # Beginner content often has higher search volume
        elif any(word in keyword_lower for word in self.technical_depth['expert']):
            difficulty = 'expert'
            score += 10  # Expert content is valuable but niche
        
        # 5. Keyword length optimization (sweet spot for SEO)
        word_count = len(keyword.split())
        if 2 <= word_count <= 4:
            score += 15  # Good for SEO
        elif word_count == 1:
            score += 5   # Too broad
        else:
            score -= 5   # Too long/specific
        
        # 6. Commercial intent
        if any(word in keyword_lower for word in ['download', 'free', 'price', 'cost', 'buy']):
            score += 12
        
        # 7. Problem-solving keywords (high engagement)
        if any(word in keyword_lower for word in ['error', 'fix', 'problem', 'troubleshoot', 'issue']):
            score += 20
        
        # 8. Trending technology boost
        if any(tech in keyword_lower for tech in ['ai', 'docker', 'kubernetes', 'cloud', 'devops']):
            score += 18
        
        # Add some realistic variation
        score += random.uniform(-5, 10)
        
        return {
            'keyword': keyword,
            'priority_score': max(0, min(100, score)),
            'content_type': content_type,
            'difficulty': difficulty,
            'search_intent': search_intent,
            'word_count': word_count,
            'estimated_competition': self.estimate_competition(keyword),
            'content_potential': self.assess_content_potential(keyword, score)
        }
    
    def estimate_competition(self, keyword: str) -> str:
        """Estimate competition level based on keyword characteristics"""
        keyword_lower = keyword.lower()
        
        # High competition indicators
        if any(word in keyword_lower for word in ['best', 'top', 'review', 'comparison']):
            return 'high'
        
        # Low competition indicators (specific technical terms)
        if any(word in keyword_lower for word in ['command', 'error', 'configuration', 'troubleshoot']):
            return 'low'
        
        # Medium for most others
        return 'medium'
    
    def assess_content_potential(self, keyword: str, score: float) -> str:
        """Assess the potential for creating quality content"""
        if score >= 70:
            return 'excellent'
        elif score >= 50:
            return 'good'
        elif score >= 30:
            return 'fair'
        else:
            return 'poor'
    
    async def process_keyword(self, keyword: str) -> Dict:
        """Process a single keyword asynchronously"""
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.001, 0.003))
        
        analysis = self.analyze_keyword_value(keyword)
        analysis['processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.processed_count += 1
        if self.processed_count % 1000 == 0:
            logger.info(f"Processed {self.processed_count} keywords...")
        
        return analysis
    
    async def process_keywords_batch(self, keywords: List[str], batch_size: int = 500) -> List[Dict]:
        """Process keywords in concurrent batches"""
        results = []
        
        for i in range(0, len(keywords), batch_size):
            batch = keywords[i:i + batch_size]
            batch_start_time = time.time()
            
            # Process batch concurrently
            tasks = [self.process_keyword(keyword) for keyword in batch]
            batch_results = await asyncio.gather(*tasks)
            
            results.extend(batch_results)
            
            batch_time = time.time() - batch_start_time
            logger.info(f"Batch {i//batch_size + 1} completed in {batch_time:.2f}s ({len(batch)} keywords)")
            
            # Small delay between batches
            if i + batch_size < len(keywords):
                await asyncio.sleep(0.1)
        
        return results
    
    def categorize_keywords(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize keywords by priority and content type"""
        
        categorized = {
            'high_priority': [],      # Score >= 60
            'medium_priority': [],    # Score 30-59
            'low_priority': [],       # Score < 30
            'tutorial_content': [],   # Best for tutorials
            'reference_content': [],  # Best for reference docs
            'comparison_content': [], # Best for comparison articles
            'career_content': [],     # Best for career-focused content
            'beginner_friendly': [],  # Great for beginners
            'problem_solving': []     # Troubleshooting content
        }
        
        for result in results:
            score = result['priority_score']
            content_type = result['content_type']
            difficulty = result['difficulty']
            keyword = result['keyword'].lower()
            
            # Priority categorization
            if score >= 60:
                categorized['high_priority'].append(result)
            elif score >= 30:
                categorized['medium_priority'].append(result)
            else:
                categorized['low_priority'].append(result)
            
            # Content type categorization
            if content_type == 'tutorial':
                categorized['tutorial_content'].append(result)
            elif content_type == 'reference':
                categorized['reference_content'].append(result)
            elif content_type == 'comparison':
                categorized['comparison_content'].append(result)
            elif content_type == 'career':
                categorized['career_content'].append(result)
            
            # Special categories
            if difficulty == 'beginner':
                categorized['beginner_friendly'].append(result)
            
            if any(word in keyword for word in ['error', 'fix', 'problem', 'troubleshoot']):
                categorized['problem_solving'].append(result)
        
        # Sort each category by priority score
        for category in categorized:
            categorized[category].sort(key=lambda x: x['priority_score'], reverse=True)
        
        return categorized

async def main():
    """Main function to run the keyword prioritizer"""
    
    KEYWORDS_FILE = "filtered-output-keywords.txt"
    OUTPUT_BASE = "keyword_analysis"
    
    # Load keywords
    try:
        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(keywords)} keywords from {KEYWORDS_FILE}")
    except FileNotFoundError:
        logger.error(f"Keywords file {KEYWORDS_FILE} not found!")
        return
    
    # Ask for confirmation
    response = input(f"\nAnalyze {len(keywords)} keywords for content strategy? (y/N): ")
    if response.lower() != 'y':
        logger.info("Analysis cancelled.")
        return
    
    # Initialize prioritizer
    prioritizer = SmartKeywordPrioritizer()
    
    # Process keywords
    start_time = time.time()
    logger.info("Starting keyword analysis...")
    
    results = await prioritizer.process_keywords_batch(keywords, batch_size=1000)
    
    # Categorize results
    logger.info("Categorizing keywords...")
    categorized = prioritizer.categorize_keywords(results)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save main results
    df = pd.DataFrame(results)
    main_file = f"{OUTPUT_BASE}_{timestamp}.csv"
    df.to_csv(main_file, index=False)
    logger.info(f"Main results saved to: {main_file}")
    
    # Save categorized results
    for category, items in categorized.items():
        if items:
            category_df = pd.DataFrame(items)
            category_file = f"{OUTPUT_BASE}_{category}_{timestamp}.csv"
            category_df.to_csv(category_file, index=False)
            logger.info(f"{category} keywords saved to: {category_file}")
    
    # Generate content strategy report
    await generate_content_strategy_report(categorized, f"{OUTPUT_BASE}_strategy_{timestamp}.txt")
    
    # Final summary
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info(f"\n{'='*60}")
    logger.info(f"KEYWORD ANALYSIS COMPLETE!")
    logger.info(f"{'='*60}")
    logger.info(f"Processing time: {total_time:.2f} seconds")
    logger.info(f"Keywords analyzed: {len(results)}")
    logger.info(f"Processing rate: {len(results)/total_time:.0f} keywords/second")
    
    # Quick stats
    high_priority = len(categorized['high_priority'])
    medium_priority = len(categorized['medium_priority'])
    tutorial_content = len(categorized['tutorial_content'])
    
    logger.info(f"\nCONTENT STRATEGY SUMMARY:")
    logger.info(f"High priority keywords: {high_priority}")
    logger.info(f"Medium priority keywords: {medium_priority}")
    logger.info(f"Tutorial opportunities: {tutorial_content}")
    logger.info(f"Comparison content opportunities: {len(categorized['comparison_content'])}")
    logger.info(f"Beginner-friendly content: {len(categorized['beginner_friendly'])}")

async def generate_content_strategy_report(categorized: Dict, filename: str):
    """Generate a comprehensive content strategy report"""
    
    with open(filename, 'w') as f:
        f.write("CONTENT STRATEGY REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Executive summary
        f.write("EXECUTIVE SUMMARY:\n")
        f.write("-" * 20 + "\n")
        f.write(f"High Priority Keywords: {len(categorized['high_priority'])}\n")
        f.write(f"Medium Priority Keywords: {len(categorized['medium_priority'])}\n")
        f.write(f"Tutorial Opportunities: {len(categorized['tutorial_content'])}\n")
        f.write(f"Comparison Content: {len(categorized['comparison_content'])}\n")
        f.write(f"Career-focused Content: {len(categorized['career_content'])}\n\n")
        
        # Content recommendations
        sections = [
            ('HIGH PRIORITY - START HERE', 'high_priority', 30),
            ('TUTORIAL CONTENT OPPORTUNITIES', 'tutorial_content', 25),
            ('COMPARISON ARTICLES', 'comparison_content', 20),
            ('BEGINNER-FRIENDLY CONTENT', 'beginner_friendly', 20),
            ('CAREER-FOCUSED ARTICLES', 'career_content', 15),
            ('PROBLEM-SOLVING GUIDES', 'problem_solving', 15)
        ]
        
        for section_name, category_key, limit in sections:
            items = categorized.get(category_key, [])
            if items:
                f.write(f"{section_name}:\n")
                f.write("-" * len(section_name) + "\n")
                for i, item in enumerate(items[:limit], 1):
                    f.write(f"{i:2d}. {item['keyword']} (Score: {item['priority_score']:.1f}, "
                           f"Type: {item['content_type']}, Difficulty: {item['difficulty']})\n")
                f.write("\n")
    
    logger.info(f"Content strategy report saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
