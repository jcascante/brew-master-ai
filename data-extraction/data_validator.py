"""
Data validation and quality assessment tools for Brew Master AI.
"""

import os
import json
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path
import logging
from datetime import datetime
from collections import Counter, defaultdict
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Warning: matplotlib/seaborn not available. Visualization features will be disabled.")

from processor import DataValidator
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataQualityAnalyzer:
    """Analyzes the quality of text data and provides insights"""
    
    def __init__(self, config: Config | None = None):
        if config is None:
            config = Config()
        self.config = config
        self.validator = DataValidator(config)
        
        # Brewing-specific keywords for content analysis
        self.brewing_keywords = {
            'process': ['mash', 'boil', 'ferment', 'condition', 'bottle', 'keg'],
            'ingredients': ['malt', 'hops', 'yeast', 'water', 'barley', 'wheat', 'rye'],
            'equipment': ['kettle', 'mash tun', 'fermenter', 'bottles', 'kegs', 'thermometer'],
            'styles': ['lager', 'ale', 'stout', 'ipa', 'pilsner', 'porter', 'wheat'],
            'measurements': ['gravity', 'abv', 'ibu', 'srm', 'ph', 'temperature'],
            'techniques': ['dry hopping', 'cold crashing', 'lagering', 'sparging']
        }
        
        # Quality metrics
        self.quality_metrics = {
            'total_files': 0,
            'valid_files': 0,
            'total_chunks': 0,
            'valid_chunks': 0,
            'avg_chunk_size': 0,
            'content_coverage': 0,
            'duplicate_content': 0,
            'low_quality_chunks': 0
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            analysis = {
                'file_path': file_path,
                'file_size': len(text),
                'word_count': len(text.split()),
                'sentence_count': len(text.split('.')),
                'paragraph_count': len(text.split('\n\n')),
                'is_valid': False,
                'validation_reason': '',
                'brewing_keywords_found': [],
                'content_quality_score': 0.0,
                'issues': []
            }
            
            # Validate text
            is_valid, reason = self.validator.validate_text(text)
            analysis['is_valid'] = is_valid
            analysis['validation_reason'] = reason
            
            # Analyze brewing content
            brewing_analysis = self._analyze_brewing_content(text)
            analysis.update(brewing_analysis)
            
            # Calculate quality score
            analysis['content_quality_score'] = self._calculate_quality_score(analysis)
            
            # Identify issues
            analysis['issues'] = self._identify_issues(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {
                'file_path': file_path,
                'error': str(e),
                'is_valid': False
            }
    
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """Analyze all text files in a directory"""
        results = {
            'directory': directory_path,
            'files_analyzed': 0,
            'valid_files': 0,
            'total_text_length': 0,
            'total_words': 0,
            'file_analyses': [],
            'content_summary': {},
            'quality_issues': defaultdict(int),
            'brewing_keyword_summary': defaultdict(int)
        }
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.txt'):
                file_path = os.path.join(directory_path, filename)
                analysis = self.analyze_file(file_path)
                results['file_analyses'].append(analysis)
                results['files_analyzed'] += 1
                
                if analysis.get('is_valid', False):
                    results['valid_files'] += 1
                    results['total_text_length'] += analysis.get('file_size', 0)
                    results['total_words'] += analysis.get('word_count', 0)
                
                # Collect issues
                for issue in analysis.get('issues', []):
                    results['quality_issues'][issue] += 1
                
                # Collect brewing keywords
                for keyword in analysis.get('brewing_keywords_found', []):
                    results['brewing_keyword_summary'][keyword] += 1
        
        # Calculate summary statistics
        if results['files_analyzed'] > 0:
            results['validity_rate'] = results['valid_files'] / results['files_analyzed']
            results['avg_file_size'] = results['total_text_length'] / results['files_analyzed']
            results['avg_words_per_file'] = results['total_words'] / results['files_analyzed']
        
        return results
    
    def _analyze_brewing_content(self, text: str) -> Dict[str, Any]:
        """Analyze brewing-specific content in text"""
        text_lower = text.lower()
        found_keywords = []
        keyword_categories = defaultdict(int)
        
        for category, keywords in self.brewing_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
                    keyword_categories[category] += 1
        
        return {
            'brewing_keywords_found': found_keywords,
            'brewing_keyword_count': len(found_keywords),
            'brewing_keyword_categories': dict(keyword_categories),
            'brewing_content_ratio': len(found_keywords) / max(len(text.split()), 1)
        }
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate a quality score for the content"""
        score = 0.0
        
        # Base score for valid content
        if analysis.get('is_valid', False):
            score += 0.3
        
        # Score based on content length
        word_count = analysis.get('word_count', 0)
        if 100 <= word_count <= 5000:
            score += 0.2
        elif word_count > 5000:
            score += 0.1
        
        # Score based on brewing content
        brewing_ratio = analysis.get('brewing_content_ratio', 0)
        if brewing_ratio > 0.01:  # 1% brewing keywords
            score += 0.3
        elif brewing_ratio > 0.005:  # 0.5% brewing keywords
            score += 0.2
        
        # Score based on sentence structure
        sentence_count = analysis.get('sentence_count', 0)
        if sentence_count > 5:
            score += 0.1
        
        # Penalty for issues
        issue_count = len(analysis.get('issues', []))
        score -= min(issue_count * 0.1, 0.3)
        
        return max(0.0, min(1.0, score))
    
    def _identify_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify quality issues in the content"""
        issues = []
        
        if not analysis.get('is_valid', False):
            issues.append('validation_failed')
        
        word_count = analysis.get('word_count', 0)
        if word_count < 50:
            issues.append('too_short')
        elif word_count > 10000:
            issues.append('too_long')
        
        brewing_ratio = analysis.get('brewing_content_ratio', 0)
        if brewing_ratio < 0.001:  # Less than 0.1% brewing keywords
            issues.append('low_brewing_content')
        
        sentence_count = analysis.get('sentence_count', 0)
        if sentence_count < 3:
            issues.append('insufficient_sentences')
        
        return issues
    
    def generate_report(self, analysis_results: Dict[str, Any], output_file: str | None = None) -> str:
        """Generate a comprehensive quality report"""
        report = []
        report.append("=" * 60)
        report.append("BREW MASTER AI - DATA QUALITY ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Directory: {analysis_results['directory']}")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY STATISTICS:")
        report.append("-" * 30)
        report.append(f"Files analyzed: {analysis_results['files_analyzed']}")
        report.append(f"Valid files: {analysis_results['valid_files']}")
        report.append(f"Validity rate: {analysis_results.get('validity_rate', 0):.1%}")
        report.append(f"Total text length: {analysis_results['total_text_length']:,} characters")
        report.append(f"Total words: {analysis_results['total_words']:,}")
        report.append(f"Average file size: {analysis_results.get('avg_file_size', 0):.0f} characters")
        report.append(f"Average words per file: {analysis_results.get('avg_words_per_file', 0):.0f}")
        report.append("")
        
        # Quality issues
        if analysis_results['quality_issues']:
            report.append("QUALITY ISSUES:")
            report.append("-" * 30)
            for issue, count in sorted(analysis_results['quality_issues'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"{issue}: {count} files")
            report.append("")
        
        # Brewing keyword summary
        if analysis_results['brewing_keyword_summary']:
            report.append("BREWING KEYWORDS FOUND:")
            report.append("-" * 30)
            for keyword, count in sorted(analysis_results['brewing_keyword_summary'].items(), key=lambda x: x[1], reverse=True)[:20]:
                report.append(f"{keyword}: {count} occurrences")
            report.append("")
        
        # Individual file analysis
        report.append("INDIVIDUAL FILE ANALYSIS:")
        report.append("-" * 30)
        for file_analysis in analysis_results['file_analyses']:
            if 'error' in file_analysis:
                report.append(f"❌ {os.path.basename(file_analysis['file_path'])}: ERROR - {file_analysis['error']}")
            else:
                status = "✅" if file_analysis.get('is_valid', False) else "❌"
                score = file_analysis.get('content_quality_score', 0)
                report.append(f"{status} {os.path.basename(file_analysis['file_path'])}: "
                           f"Score {score:.2f}, {file_analysis.get('word_count', 0)} words, "
                           f"{file_analysis.get('brewing_keyword_count', 0)} brewing keywords")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Quality report saved to: {output_file}")
        
        return report_text
    
    def create_visualizations(self, analysis_results: Dict[str, Any], output_dir: str = "quality_plots"):
        """Create visualizations of the analysis results"""
        os.makedirs(output_dir, exist_ok=True)
        
        # File quality scores distribution
        scores = [a.get('content_quality_score', 0) for a in analysis_results['file_analyses'] if 'error' not in a]
        if scores:
            plt.figure(figsize=(10, 6))
            plt.hist(scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.xlabel('Quality Score')
            plt.ylabel('Number of Files')
            plt.title('Distribution of File Quality Scores')
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(output_dir, 'quality_scores_distribution.png'))
            plt.close()
        
        # Brewing keywords frequency
        if analysis_results['brewing_keyword_summary']:
            keywords = list(analysis_results['brewing_keyword_summary'].keys())[:15]
            counts = [analysis_results['brewing_keyword_summary'][k] for k in keywords]
            
            plt.figure(figsize=(12, 8))
            plt.barh(keywords, counts, color='lightcoral')
            plt.xlabel('Frequency')
            plt.title('Top 15 Brewing Keywords Found')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'brewing_keywords_frequency.png'))
            plt.close()
        
        # Quality issues breakdown
        if analysis_results['quality_issues']:
            issues = list(analysis_results['quality_issues'].keys())
            counts = list(analysis_results['quality_issues'].values())
            
            plt.figure(figsize=(10, 6))
            plt.pie(counts, labels=issues, autopct='%1.1f%%', startangle=90)
            plt.title('Quality Issues Breakdown')
            plt.axis('equal')
            plt.savefig(os.path.join(output_dir, 'quality_issues_breakdown.png'))
            plt.close()

def main():
    """Main function for data validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Quality Analyzer for Brew Master AI')
    parser.add_argument('--analyze', type=str, help='Directory to analyze')
    parser.add_argument('--report', type=str, help='Output file for quality report')
    parser.add_argument('--visualize', action='store_true', help='Create visualizations')
    parser.add_argument('--output-dir', type=str, default='quality_plots', help='Output directory for plots')
    
    args = parser.parse_args()
    
    if not args.analyze:
        print("Please specify a directory to analyze with --analyze")
        return
    
    if not os.path.exists(args.analyze):
        print(f"Directory not found: {args.analyze}")
        return
    
    # Initialize analyzer
    analyzer = DataQualityAnalyzer()
    
    # Analyze directory
    print(f"Analyzing directory: {args.analyze}")
    results = analyzer.analyze_directory(args.analyze)
    
    # Generate report
    report = analyzer.generate_report(results, args.report)
    print(report)
    
    # Create visualizations
    if args.visualize:
        print(f"Creating visualizations in: {args.output_dir}")
        analyzer.create_visualizations(results, args.output_dir)

if __name__ == "__main__":
    main() 