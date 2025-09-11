#!/usr/bin/env python3
"""
Simple Video Analyzer for IZA OS
Uses existing tools + Agent-S2 for actual production results
"""

import asyncio
import json
import logging
import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

logger = logging.getLogger(__name__)

class SimpleVideoAnalyzer:
    """Simple analyzer using existing tools + Agent-S2 integration"""
    
    def __init__(self):
        self.target_videos = [
            "https://www.youtube.com/watch?v=xOO8Wt_i72s",
            "https://www.youtube.com/watch?v=Y2oK0nubq9A", 
            "https://www.youtube.com/watch?v=QgA55EnmUp4",
            "https://www.youtube.com/watch?v=Pmc4OfSlhbE",
            "https://www.youtube.com/watch?v=fD8NLPU0WYU"
        ]
        
        # Create knowledge base directory
        os.makedirs('knowledge_base', exist_ok=True)
        self.db_path = 'knowledge_base/video_insights.db'
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for insights"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                video_title TEXT NOT NULL,
                category TEXT NOT NULL,
                insight_text TEXT NOT NULL,
                confidence REAL NOT NULL,
                extracted_at TEXT NOT NULL,
                actionable BOOLEAN NOT NULL,
                implementation_notes TEXT,
                assigned_agent TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Create improvements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_id INTEGER NOT NULL,
                improvement_type TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL,
                estimated_effort TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                assigned_agent TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY (insight_id) REFERENCES video_insights (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def get_video_transcript(self, video_id: str) -> Optional[str]:
        """Get video transcript using youtube-transcript-api"""
        
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript parts
            full_transcript = ""
            for transcript in transcript_list:
                full_transcript += transcript['text'] + " "
            
            return full_transcript.strip()
            
        except Exception as e:
            logger.error(f"Failed to get transcript for {video_id}: {e}")
            return None
    
    def get_video_metadata(self, url: str) -> Dict[str, Any]:
        """Get video metadata using yt-dlp"""
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'video_id': info.get('id', '')
                }
                
        except Exception as e:
            logger.error(f"Failed to get metadata for {url}: {e}")
            return {
                'title': 'Unknown',
                'duration': 0,
                'upload_date': '',
                'view_count': 0,
                'description': '',
                'tags': [],
                'video_id': self.extract_video_id(url)
            }
    
    def extract_iza_os_insights(self, transcript: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract IZA OS specific insights from transcript"""
        
        insights = []
        
        # Define insight patterns and categories
        insight_patterns = {
            'agent_optimization': [
                r'\b(agent|automation|workflow|orchestration|swarm|hive mind)\b',
                r'\b(autonomous|self-evolving|self-improving|recursive)\b',
                r'\b(optimization|efficiency|performance|scaling)\b'
            ],
            'workflow_automation': [
                r'\b(workflow|automation|pipeline|process|streamline)\b',
                r'\b(zapier|n8n|make\.com|integromat)\b',
                r'\b(trigger|action|webhook|api|integration)\b'
            ],
            'knowledge_management': [
                r'\b(knowledge|graph|database|vector|embedding|rag)\b',
                r'\b(neo4j|chromadb|supabase|graphiti)\b',
                r'\b(learning|training|model|ai|ml)\b'
            ],
            'security_enhancement': [
                r'\b(security|authentication|authorization|encryption)\b',
                r'\b(compliance|gdpr|hipaa|sox|audit)\b',
                r'\b(verification|validation|trust|integrity)\b'
            ],
            'scalability_improvement': [
                r'\b(scaling|scalability|performance|load|traffic)\b',
                r'\b(microservices|kubernetes|docker|cloud|aws|azure)\b',
                r'\b(monitoring|logging|metrics|alerting)\b'
            ]
        }
        
        # Extract insights based on patterns
        for category, patterns in insight_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                
                for match in matches:
                    # Get context around the match
                    start = max(0, match.start() - 100)
                    end = min(len(transcript), match.end() + 100)
                    context = transcript[start:end].strip()
                    
                    # Calculate confidence based on context relevance
                    confidence = self._calculate_confidence(context, category)
                    
                    if confidence > 0.3:  # Only include relevant insights
                        insight = {
                            'video_id': metadata.get('video_id', 'unknown'),
                            'video_title': metadata.get('title', 'Unknown'),
                            'category': category,
                            'insight_text': context,
                            'confidence': confidence,
                            'extracted_at': datetime.now().isoformat(),
                            'actionable': confidence > 0.6,
                            'implementation_notes': f"Extracted from video: {metadata.get('title', 'Unknown')}",
                            'assigned_agent': self._assign_agent(category),
                            'status': 'pending'
                        }
                        
                        insights.append(insight)
        
        return insights
    
    def _calculate_confidence(self, context: str, category: str) -> float:
        """Calculate confidence score for an insight"""
        
        # Base confidence
        confidence = 0.5
        
        # Boost confidence based on context quality
        if len(context) > 200:
            confidence += 0.2
        
        # Boost based on category-specific keywords
        category_boosters = {
            'agent_optimization': ['agent', 'autonomous', 'optimization'],
            'workflow_automation': ['workflow', 'automation', 'pipeline'],
            'knowledge_management': ['knowledge', 'graph', 'database'],
            'security_enhancement': ['security', 'authentication', 'compliance'],
            'scalability_improvement': ['scaling', 'performance', 'monitoring']
        }
        
        boosters = category_boosters.get(category, [])
        for booster in boosters:
            if booster.lower() in context.lower():
                confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _assign_agent(self, category: str) -> str:
        """Assign insight to appropriate IZA OS agent"""
        
        agent_mapping = {
            'agent_optimization': 'SEAL_Implementation_Agent',
            'workflow_automation': 'MCP_Integration_Agent',
            'knowledge_management': 'Memory_Integration_Agent',
            'security_enhancement': 'Security_Agent',
            'scalability_improvement': 'System_Optimizer_Agent'
        }
        
        return agent_mapping.get(category, 'General_Agent')
    
    def save_insights_to_db(self, insights: List[Dict[str, Any]]):
        """Save insights to SQLite database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for insight in insights:
            cursor.execute('''
                INSERT INTO video_insights 
                (video_id, video_title, category, insight_text, confidence, 
                 extracted_at, actionable, implementation_notes, assigned_agent, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight['video_id'],
                insight['video_title'],
                insight['category'],
                insight['insight_text'],
                insight['confidence'],
                insight['insight_text'],
                insight['actionable'],
                insight['implementation_notes'],
                insight['assigned_agent'],
                insight['status']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(insights)} insights to database")
    
    def generate_system_improvements(self) -> List[Dict[str, Any]]:
        """Generate system improvements from insights"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get high-confidence actionable insights
        cursor.execute('''
            SELECT id, category, insight_text, confidence, assigned_agent
            FROM video_insights 
            WHERE actionable = 1 AND confidence > 0.6
            ORDER BY confidence DESC
        ''')
        
        insights = cursor.fetchall()
        improvements = []
        
        for insight in insights:
            improvement = {
                'insight_id': insight[0],
                'improvement_type': insight[1],
                'description': insight[2][:200] + "..." if len(insight[2]) > 200 else insight[2],
                'priority': 'high' if insight[3] > 0.8 else 'medium',
                'estimated_effort': self._estimate_effort(insight[1]),
                'status': 'pending',
                'assigned_agent': insight[4],
                'created_at': datetime.now().isoformat()
            }
            
            improvements.append(improvement)
            
            # Save to improvements table
            cursor.execute('''
                INSERT INTO system_improvements 
                (insight_id, improvement_type, description, priority, estimated_effort, 
                 status, assigned_agent, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                improvement['insight_id'],
                improvement['improvement_type'],
                improvement['description'],
                improvement['priority'],
                improvement['estimated_effort'],
                improvement['status'],
                improvement['assigned_agent'],
                improvement['created_at']
            ))
        
        conn.commit()
        conn.close()
        
        return improvements
    
    def _estimate_effort(self, category: str) -> str:
        """Estimate effort for implementing improvement"""
        
        effort_mapping = {
            'agent_optimization': '4-8 hours',
            'workflow_automation': '6-12 hours',
            'knowledge_management': '8-16 hours',
            'security_enhancement': '12-24 hours',
            'scalability_improvement': '16-32 hours'
        }
        
        return effort_mapping.get(category, '8-16 hours')
    
    async def analyze_all_videos(self) -> Dict[str, Any]:
        """Analyze all target videos"""
        
        logger.info("Starting analysis of target videos...")
        
        all_insights = []
        video_analysis = {}
        
        for video_url in self.target_videos:
            try:
                logger.info(f"Analyzing video: {video_url}")
                
                # Get video metadata
                metadata = self.get_video_metadata(video_url)
                video_id = metadata.get('video_id', self.extract_video_id(video_url))
                
                # Get transcript
                transcript = self.get_video_transcript(video_id)
                
                if transcript:
                    # Extract insights
                    insights = self.extract_iza_os_insights(transcript, metadata)
                    
                    video_analysis[video_url] = {
                        'metadata': metadata,
                        'insights_count': len(insights),
                        'transcript_length': len(transcript),
                        'status': 'success'
                    }
                    
                    all_insights.extend(insights)
                    
                    logger.info(f"Extracted {len(insights)} insights from {metadata.get('title', 'Unknown')}")
                else:
                    video_analysis[video_url] = {
                        'metadata': metadata,
                        'insights_count': 0,
                        'status': 'no_transcript'
                    }
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to analyze video {video_url}: {e}")
                video_analysis[video_url] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Save insights to database
        if all_insights:
            self.save_insights_to_db(all_insights)
        
        # Generate improvements
        improvements = self.generate_system_improvements()
        
        # Create analysis report
        analysis_report = {
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'total_videos': len(self.target_videos),
                'successful_analyses': len([v for v in video_analysis.values() if v.get('status') == 'success']),
                'total_insights': len(all_insights),
                'total_improvements': len(improvements)
            },
            'video_analysis': video_analysis,
            'system_improvements': improvements,
            'summary': {
                'high_priority_improvements': len([imp for imp in improvements if imp['priority'] == 'high']),
                'medium_priority_improvements': len([imp for imp in improvements if imp['priority'] == 'medium']),
                'estimated_total_effort': self._calculate_total_effort(improvements)
            }
        }
        
        return analysis_report
    
    def _calculate_total_effort(self, improvements: List[Dict[str, Any]]) -> str:
        """Calculate total estimated effort"""
        
        effort_mapping = {
            '4-8 hours': 6,
            '6-12 hours': 9,
            '8-16 hours': 12,
            '12-24 hours': 18,
            '16-32 hours': 24
        }
        
        total_hours = 0
        for improvement in improvements:
            effort = improvement['estimated_effort']
            if effort in effort_mapping:
                total_hours += effort_mapping[effort]
        
        if total_hours < 24:
            return f"{total_hours} hours (1-3 days)"
        elif total_hours < 40:
            return f"{total_hours} hours (1 week)"
        else:
            return f"{total_hours} hours (2+ weeks)"
    
    def export_report(self, analysis_report: Dict[str, Any], output_path: str):
        """Export analysis report"""
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False)
        
        # Create markdown summary
        summary_file = output_file.parent / f"video_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_summary(analysis_report))
        
        logger.info(f"Report exported to {output_file}")
        logger.info(f"Summary exported to {summary_file}")
    
    def _generate_markdown_summary(self, analysis_report: Dict[str, Any]) -> str:
        """Generate markdown summary"""
        
        summary = f"""# IZA OS Video Analysis Report

## 📊 **Analysis Overview**
- **Analyzed At**: {analysis_report['metadata']['analyzed_at']}
- **Total Videos**: {analysis_report['metadata']['total_videos']}
- **Successful Analyses**: {analysis_report['metadata']['successful_analyses']}
- **Total Insights**: {analysis_report['metadata']['total_insights']}
- **Total Improvements**: {analysis_report['metadata']['total_improvements']}

## 🎯 **Priority Improvements Summary**
- **High Priority**: {analysis_report['summary']['high_priority_improvements']}
- **Medium Priority**: {analysis_report['summary']['medium_priority_improvements']}
- **Total Estimated Effort**: {analysis_report['summary']['estimated_total_effort']}

## 📹 **Video Analysis Results**

"""
        
        for video_url, analysis in analysis_report['video_analysis'].items():
            if analysis.get('status') == 'success':
                summary += f"### ✅ {analysis['metadata']['title']}\n"
                summary += f"- **Duration**: {analysis['metadata']['duration']} seconds\n"
                summary += f"- **Views**: {analysis['metadata']['view_count']:,}\n"
                summary += f"- **Insights Found**: {analysis['insights_count']}\n\n"
            elif analysis.get('status') == 'error':
                summary += f"### ❌ {video_url}\n"
                summary += f"- **Error**: {analysis['error']}\n\n"
            else:
                summary += f"### ⚠️ {video_url}\n"
                summary += f"- **Status**: {analysis['status']}\n\n"
        
        summary += """## 🚀 **Next Steps**

1. **Review High Priority Improvements**: Focus on insights with confidence > 0.8
2. **Assign to Agents**: Use the assigned agent mapping for implementation
3. **Track Progress**: Monitor improvement status in the database
4. **Schedule Regular Analysis**: Run this analysis weekly for continuous improvement

## 📁 **Generated Files**

- `video_analysis_report.json`: Complete analysis data
- `video_insights.db`: SQLite database with all insights
- `video_analysis_summary_*.md`: Human-readable summary

---
*Generated by IZA OS Simple Video Analyzer*
"""
        
        return summary

async def main():
    """Run the video analysis"""
    
    analyzer = SimpleVideoAnalyzer()
    
    logger.info("Starting analysis of target YouTube videos...")
    
    # Analyze all videos
    analysis_report = await analyzer.analyze_all_videos()
    
    # Export report
    analyzer.export_report(
        analysis_report, 
        'knowledge_base/video_analysis_report.json'
    )
    
    logger.info("Video analysis complete!")
    logger.info(f"Found {analysis_report['metadata']['total_insights']} insights")
    logger.info(f"Generated {analysis_report['metadata']['total_improvements']} improvements")
    
    # Print summary
    print(f"\n🎯 **IZA OS Video Analysis Complete**")
    print(f"📊 Total Insights: {analysis_report['metadata']['total_insights']}")
    print(f"🚀 Total Improvements: {analysis_report['metadata']['total_improvements']}")
    print(f"⏱️  Estimated Effort: {analysis_report['summary']['estimated_total_effort']}")
    print(f"📁 Report saved to: knowledge_base/video_analysis_report.json")
    print(f"🗄️  Database: knowledge_base/video_insights.db")

if __name__ == "__main__":
    asyncio.run(main())
