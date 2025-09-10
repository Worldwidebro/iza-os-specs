#!/usr/bin/env python3
"""
IZA OS Business Model: BM003 - AI Local Business SEO Service

This template implements an automated local SEO service that:
- Provides automated local SEO content, GMB posting, and backlink outreach
- Scrapes competitor pages & local citations using Firecrawl
- Generates structured local SEO content using PromptLab templates
- Automates Google My Business posting and monitoring
- Provides client dashboard for subscription management

Stack Integration:
- Firecrawl: Scrape competitor pages & local citations
- PromptLab: Structured local SEO prompt templates
- Playwright: Verify post publishing and form submissions
- shadcn/ui: Client dashboard interface
- n8n: Workflow automation for outreach and posting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import sqlite3
import uuid
import os
import re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# Core framework imports
from fastmcp import FastMCP, Context

# Browser automation - conditional imports with fallbacks
try:
    from stagehand import Stagehand
    STAGEHAND_AVAILABLE = True
except ImportError:
    STAGEHAND_AVAILABLE = False
    logging.warning("Stagehand not available, using requests fallback")

# Web scraping with Firecrawl fallback
try:
    import firecrawl
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    logging.warning("Firecrawl not available, using requests fallback")

@dataclass
class ClientData:
    """Client data structure"""
    id: str
    business_name: str
    industry: str
    location: str
    website: str
    gmb_profile: str
    target_keywords: List[str]
    competitors: List[str]
    subscription_tier: str
    created_at: datetime
    status: str = "active"

@dataclass
class SEOAudit:
    """SEO audit data structure"""
    id: str
    client_id: str
    audit_date: datetime
    current_rankings: Dict[str, int]
    competitor_analysis: Dict[str, Any]
    content_gaps: List[str]
    technical_issues: List[str]
    recommendations: List[str]
    priority_score: float

@dataclass
class ContentPiece:
    """Content piece data structure"""
    id: str
    client_id: str
    title: str
    content: str
    content_type: str  # blog_post, gmb_post, meta_description, etc.
    target_keyword: str
    seo_score: float
    created_at: datetime
    published: bool = False
    platform: str = "website"

@dataclass
class BacklinkOpportunity:
    """Backlink opportunity data structure"""
    id: str
    client_id: str
    target_url: str
    target_domain: str
    opportunity_type: str  # guest_post, resource_page, directory, etc.
    contact_email: str
    outreach_status: str
    priority_score: float
    created_at: datetime

class LocalSEOService:
    """
    AI Local Business SEO Service
    
    Features:
    - Automated competitor analysis and keyword research
    - AI-generated local SEO content
    - Google My Business posting automation
    - Backlink outreach and tracking
    - Client dashboard and reporting
    - Performance monitoring and optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_path = Path("local_seo_service.db")
        self.content_dir = Path("content")
        self.reports_dir = Path("reports")
        self.outreach_dir = Path("outreach")
        
        # Create directories
        for dir_path in [self.content_dir, self.reports_dir, self.outreach_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Initialize FastMCP
        self.mcp = FastMCP("LocalSEOService")
        
        # API configurations
        self.google_api_key = config.get("google_api_key", "")
        self.gmb_api_key = config.get("gmb_api_key", "")
        self.serp_api_key = config.get("serp_api_key", "")
        
        # Business metrics
        self.metrics = {
            "total_clients": 0,
            "active_campaigns": 0,
            "content_pieces_created": 0,
            "backlinks_acquired": 0,
            "average_ranking_improvement": 0.0,
            "monthly_revenue": 0.0
        }
    
    def _init_database(self):
        """Initialize SQLite database for local SEO service"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    business_name TEXT NOT NULL,
                    industry TEXT,
                    location TEXT,
                    website TEXT,
                    gmb_profile TEXT,
                    target_keywords TEXT,
                    competitors TEXT,
                    subscription_tier TEXT,
                    created_at TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # SEO audits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seo_audits (
                    id TEXT PRIMARY KEY,
                    client_id TEXT,
                    audit_date TIMESTAMP,
                    current_rankings TEXT,
                    competitor_analysis TEXT,
                    content_gaps TEXT,
                    technical_issues TEXT,
                    recommendations TEXT,
                    priority_score REAL,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)
            
            # Content pieces table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_pieces (
                    id TEXT PRIMARY KEY,
                    client_id TEXT,
                    title TEXT,
                    content TEXT,
                    content_type TEXT,
                    target_keyword TEXT,
                    seo_score REAL,
                    created_at TIMESTAMP,
                    published BOOLEAN DEFAULT FALSE,
                    platform TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)
            
            # Backlink opportunities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backlink_opportunities (
                    id TEXT PRIMARY KEY,
                    client_id TEXT,
                    target_url TEXT,
                    target_domain TEXT,
                    opportunity_type TEXT,
                    contact_email TEXT,
                    outreach_status TEXT,
                    priority_score REAL,
                    created_at TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)
            
            # Rankings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rankings (
                    id TEXT PRIMARY KEY,
                    client_id TEXT,
                    keyword TEXT,
                    position INTEGER,
                    search_volume INTEGER,
                    competition_level TEXT,
                    tracked_date TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)
            
            conn.commit()
    
    async def onboard_client(self, client_data: Dict[str, Any]) -> ClientData:
        """
        Onboard a new client for SEO services
        
        Agent-S Task: client_onboarding_agent
        """
        self.logger.info(f"Onboarding client: {client_data.get('business_name', 'Unknown')}")
        
        client = ClientData(
            id=str(uuid.uuid4()),
            business_name=client_data.get("business_name", ""),
            industry=client_data.get("industry", ""),
            location=client_data.get("location", ""),
            website=client_data.get("website", ""),
            gmb_profile=client_data.get("gmb_profile", ""),
            target_keywords=client_data.get("target_keywords", []),
            competitors=client_data.get("competitors", []),
            subscription_tier=client_data.get("subscription_tier", "basic"),
            created_at=datetime.now()
        )
        
        # Store client
        await self._store_client(client)
        
        # Perform initial SEO audit
        audit = await self.perform_seo_audit(client.id)
        
        self.logger.info(f"Client {client.business_name} onboarded successfully")
        return client
    
    async def _store_client(self, client: ClientData):
        """Store client in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO clients 
                (id, business_name, industry, location, website, gmb_profile, 
                 target_keywords, competitors, subscription_tier, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client.id,
                client.business_name,
                client.industry,
                client.location,
                client.website,
                client.gmb_profile,
                json.dumps(client.target_keywords),
                json.dumps(client.competitors),
                client.subscription_tier,
                client.created_at,
                client.status
            ))
            
            conn.commit()
    
    async def perform_seo_audit(self, client_id: str) -> SEOAudit:
        """
        Perform comprehensive SEO audit for client
        
        Agent-S Task: audit_agent
        """
        self.logger.info(f"Performing SEO audit for client {client_id}")
        
        # Get client data
        client = await self._get_client(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Analyze current rankings
        current_rankings = await self._analyze_current_rankings(client)
        
        # Perform competitor analysis
        competitor_analysis = await self._analyze_competitors(client)
        
        # Identify content gaps
        content_gaps = await self._identify_content_gaps(client, competitor_analysis)
        
        # Check technical issues
        technical_issues = await self._check_technical_issues(client)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            current_rankings, competitor_analysis, content_gaps, technical_issues
        )
        
        # Calculate priority score
        priority_score = await self._calculate_priority_score(
            current_rankings, content_gaps, technical_issues
        )
        
        audit = SEOAudit(
            id=str(uuid.uuid4()),
            client_id=client_id,
            audit_date=datetime.now(),
            current_rankings=current_rankings,
            competitor_analysis=competitor_analysis,
            content_gaps=content_gaps,
            technical_issues=technical_issues,
            recommendations=recommendations,
            priority_score=priority_score
        )
        
        # Store audit
        await self._store_audit(audit)
        
        self.logger.info(f"SEO audit completed for client {client_id}")
        return audit
    
    async def _analyze_current_rankings(self, client: ClientData) -> Dict[str, int]:
        """Analyze current keyword rankings"""
        rankings = {}
        
        for keyword in client.target_keywords:
            try:
                # Simplified ranking check (would use SERP API in production)
                position = await self._check_keyword_ranking(keyword, client.location)
                rankings[keyword] = position
                
                # Store ranking data
                await self._store_ranking(client.id, keyword, position)
                
            except Exception as e:
                self.logger.error(f"Error checking ranking for {keyword}: {e}")
                rankings[keyword] = 0
        
        return rankings
    
    async def _check_keyword_ranking(self, keyword: str, location: str) -> int:
        """Check keyword ranking (simplified implementation)"""
        # In production, this would use Google Search API or SERP API
        # For now, return a simulated ranking
        return hash(f"{keyword}_{location}") % 50 + 1
    
    async def _analyze_competitors(self, client: ClientData) -> Dict[str, Any]:
        """
        Analyze competitor websites and strategies
        
        Agent-S Task: competitor_analysis_agent
        """
        competitor_data = {}
        
        for competitor_url in client.competitors:
            try:
                if FIRECRAWL_AVAILABLE:
                    analysis = await self._scrape_competitor_firecrawl(competitor_url)
                else:
                    analysis = await self._scrape_competitor_requests(competitor_url)
                
                competitor_data[competitor_url] = analysis
                
            except Exception as e:
                self.logger.error(f"Error analyzing competitor {competitor_url}: {e}")
                continue
        
        return competitor_data
    
    async def _scrape_competitor_firecrawl(self, url: str) -> Dict[str, Any]:
        """Scrape competitor using Firecrawl"""
        # Firecrawl implementation would go here
        # For now, return sample data
        return {
            "title": f"Competitor Analysis for {url}",
            "meta_description": "Sample meta description",
            "headings": ["H1", "H2", "H3"],
            "keywords": ["local", "business", "service"],
            "content_length": 1500,
            "internal_links": 25,
            "external_links": 10,
            "images": 8,
            "page_speed": 85
        }
    
    async def _scrape_competitor_requests(self, url: str) -> Dict[str, Any]:
        """Fallback competitor scraping using requests"""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic SEO data
            title = soup.find('title')
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            headings = soup.find_all(['h1', 'h2', 'h3'])
            
            return {
                "title": title.text if title else "",
                "meta_description": meta_desc.get('content') if meta_desc else "",
                "headings": [h.text.strip() for h in headings],
                "keywords": [],  # Would need keyword extraction
                "content_length": len(soup.get_text()),
                "internal_links": len(soup.find_all('a', href=True)),
                "external_links": 0,  # Would need to analyze external links
                "images": len(soup.find_all('img')),
                "page_speed": 0  # Would need page speed testing
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return {}
    
    async def _identify_content_gaps(self, client: ClientData, competitor_analysis: Dict[str, Any]) -> List[str]:
        """Identify content gaps compared to competitors"""
        gaps = []
        
        # Analyze competitor content themes
        competitor_themes = set()
        for competitor_data in competitor_analysis.values():
            if "headings" in competitor_data:
                competitor_themes.update(competitor_data["headings"])
        
        # Identify gaps based on industry and location
        industry_gaps = [
            f"{client.industry} services in {client.location}",
            f"Best {client.industry} near me",
            f"{client.industry} reviews {client.location}",
            f"How to choose {client.industry}",
            f"{client.industry} tips and tricks"
        ]
        
        gaps.extend(industry_gaps)
        
        return gaps[:10]  # Return top 10 gaps
    
    async def _check_technical_issues(self, client: ClientData) -> List[str]:
        """Check for technical SEO issues"""
        issues = []
        
        try:
            # Check website accessibility
            response = requests.get(client.website, timeout=10)
            
            if response.status_code != 200:
                issues.append(f"Website returns {response.status_code} status code")
            
            # Check for basic SEO elements
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if not soup.find('title'):
                issues.append("Missing title tag")
            
            if not soup.find('meta', attrs={'name': 'description'}):
                issues.append("Missing meta description")
            
            if not soup.find('h1'):
                issues.append("Missing H1 tag")
            
            # Check for mobile responsiveness (simplified)
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport_meta:
                issues.append("Missing viewport meta tag")
            
        except Exception as e:
            self.logger.error(f"Error checking technical issues for {client.website}: {e}")
            issues.append(f"Unable to access website: {e}")
        
        return issues
    
    async def _generate_recommendations(self, rankings: Dict[str, int], 
                                       competitor_analysis: Dict[str, Any],
                                       content_gaps: List[str], 
                                       technical_issues: List[str]) -> List[str]:
        """Generate SEO recommendations"""
        recommendations = []
        
        # Ranking-based recommendations
        low_ranking_keywords = [kw for kw, pos in rankings.items() if pos > 10]
        if low_ranking_keywords:
            recommendations.append(f"Focus on improving rankings for: {', '.join(low_ranking_keywords)}")
        
        # Content gap recommendations
        if content_gaps:
            recommendations.append(f"Create content for these topics: {', '.join(content_gaps[:3])}")
        
        # Technical issue recommendations
        if technical_issues:
            recommendations.append(f"Fix technical issues: {', '.join(technical_issues[:3])}")
        
        # Competitor-based recommendations
        if competitor_analysis:
            recommendations.append("Analyze competitor content strategies and adapt successful approaches")
        
        return recommendations
    
    async def _calculate_priority_score(self, rankings: Dict[str, int], 
                                      content_gaps: List[str], 
                                      technical_issues: List[str]) -> float:
        """Calculate priority score for SEO efforts"""
        score = 0.0
        
        # Ranking factor (lower rankings = higher priority)
        avg_ranking = sum(rankings.values()) / len(rankings) if rankings else 50
        score += (50 - avg_ranking) / 50 * 40  # Max 40 points
        
        # Content gap factor
        score += min(len(content_gaps) * 2, 30)  # Max 30 points
        
        # Technical issue factor
        score += min(len(technical_issues) * 5, 30)  # Max 30 points
        
        return min(score, 100.0)
    
    async def _store_audit(self, audit: SEOAudit):
        """Store SEO audit in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO seo_audits 
                (id, client_id, audit_date, current_rankings, competitor_analysis,
                 content_gaps, technical_issues, recommendations, priority_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit.id,
                audit.client_id,
                audit.audit_date,
                json.dumps(audit.current_rankings),
                json.dumps(audit.competitor_analysis),
                json.dumps(audit.content_gaps),
                json.dumps(audit.technical_issues),
                json.dumps(audit.recommendations),
                audit.priority_score
            ))
            
            conn.commit()
    
    async def generate_content(self, client_id: str, content_gaps: List[str]) -> List[ContentPiece]:
        """
        Generate SEO-optimized content
        
        Agent-S Task: content_agent
        """
        self.logger.info(f"Generating content for client {client_id}")
        
        client = await self._get_client(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        content_pieces = []
        
        for gap in content_gaps[:5]:  # Generate content for top 5 gaps
            try:
                # Generate blog post
                blog_post = await self._generate_blog_post(client, gap)
                content_pieces.append(blog_post)
                
                # Generate GMB post
                gmb_post = await self._generate_gmb_post(client, gap)
                content_pieces.append(gmb_post)
                
                # Generate meta description
                meta_desc = await self._generate_meta_description(client, gap)
                content_pieces.append(meta_desc)
                
            except Exception as e:
                self.logger.error(f"Error generating content for gap '{gap}': {e}")
                continue
        
        # Store content pieces
        for piece in content_pieces:
            await self._store_content_piece(piece)
        
        self.logger.info(f"Generated {len(content_pieces)} content pieces")
        return content_pieces
    
    async def _generate_blog_post(self, client: ClientData, topic: str) -> ContentPiece:
        """Generate blog post content"""
        # Simplified content generation (would use AI/LLM in production)
        title = f"{topic} - {client.business_name}"
        content = f"""
        <h1>{title}</h1>
        <p>At {client.business_name}, we specialize in providing exceptional {client.industry} services in {client.location}.</p>
        
        <h2>Why Choose {client.business_name}?</h2>
        <p>Our team of experienced professionals is dedicated to delivering high-quality {client.industry} solutions tailored to your specific needs.</p>
        
        <h2>Our Services</h2>
        <p>We offer comprehensive {client.industry} services including:</p>
        <ul>
            <li>Professional consultation</li>
            <li>Custom solutions</li>
            <li>Ongoing support</li>
        </ul>
        
        <h2>Contact Us</h2>
        <p>Ready to get started? Contact {client.business_name} today for a free consultation.</p>
        """
        
        return ContentPiece(
            id=str(uuid.uuid4()),
            client_id=client.id,
            title=title,
            content=content,
            content_type="blog_post",
            target_keyword=topic,
            seo_score=85.0,
            created_at=datetime.now(),
            platform="website"
        )
    
    async def _generate_gmb_post(self, client: ClientData, topic: str) -> ContentPiece:
        """Generate Google My Business post"""
        content = f"""
        🎉 Exciting news! {client.business_name} is now offering enhanced {client.industry} services in {client.location}.
        
        Our team is committed to providing the best {client.industry} solutions for our community. 
        
        📞 Call us today for a free consultation!
        🌐 Visit our website: {client.website}
        📍 Located in {client.location}
        
        #LocalBusiness #{client.industry.replace(' ', '')} #{client.location.replace(' ', '')}
        """
        
        return ContentPiece(
            id=str(uuid.uuid4()),
            client_id=client.id,
            title=f"GMB Post: {topic}",
            content=content,
            content_type="gmb_post",
            target_keyword=topic,
            seo_score=80.0,
            created_at=datetime.now(),
            platform="gmb"
        )
    
    async def _generate_meta_description(self, client: ClientData, topic: str) -> ContentPiece:
        """Generate meta description"""
        content = f"Professional {client.industry} services in {client.location}. {client.business_name} offers expert solutions with personalized care. Contact us today!"
        
        return ContentPiece(
            id=str(uuid.uuid4()),
            client_id=client.id,
            title=f"Meta Description: {topic}",
            content=content,
            content_type="meta_description",
            target_keyword=topic,
            seo_score=90.0,
            created_at=datetime.now(),
            platform="website"
        )
    
    async def _store_content_piece(self, content: ContentPiece):
        """Store content piece in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO content_pieces 
                (id, client_id, title, content, content_type, target_keyword,
                 seo_score, created_at, published, platform)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content.id,
                content.client_id,
                content.title,
                content.content,
                content.content_type,
                content.target_keyword,
                content.seo_score,
                content.created_at,
                content.published,
                content.platform
            ))
            
            conn.commit()
    
    async def find_backlink_opportunities(self, client_id: str) -> List[BacklinkOpportunity]:
        """
        Find backlink opportunities for client
        
        Agent-S Task: outreach_agent
        """
        self.logger.info(f"Finding backlink opportunities for client {client_id}")
        
        client = await self._get_client(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        opportunities = []
        
        # Find local directory opportunities
        directory_opportunities = await self._find_directory_opportunities(client)
        opportunities.extend(directory_opportunities)
        
        # Find guest post opportunities
        guest_post_opportunities = await self._find_guest_post_opportunities(client)
        opportunities.extend(guest_post_opportunities)
        
        # Find resource page opportunities
        resource_opportunities = await self._find_resource_opportunities(client)
        opportunities.extend(resource_opportunities)
        
        # Store opportunities
        for opportunity in opportunities:
            await self._store_backlink_opportunity(opportunity)
        
        self.logger.info(f"Found {len(opportunities)} backlink opportunities")
        return opportunities
    
    async def _find_directory_opportunities(self, client: ClientData) -> List[BacklinkOpportunity]:
        """Find local directory opportunities"""
        opportunities = []
        
        # Common local directories
        directories = [
            "https://www.yelp.com",
            "https://www.google.com/maps",
            "https://www.yellowpages.com",
            "https://www.local.com",
            "https://www.citysearch.com"
        ]
        
        for directory in directories:
            opportunity = BacklinkOpportunity(
                id=str(uuid.uuid4()),
                client_id=client.id,
                target_url=directory,
                target_domain=urlparse(directory).netloc,
                opportunity_type="directory",
                contact_email="",  # Would need to extract from directory
                outreach_status="pending",
                priority_score=70.0,
                created_at=datetime.now()
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _find_guest_post_opportunities(self, client: ClientData) -> List[BacklinkOpportunity]:
        """Find guest post opportunities"""
        opportunities = []
        
        # Industry-specific blogs (simplified)
        industry_blogs = [
            f"https://{client.industry.replace(' ', '')}blog.com",
            f"https://{client.industry.replace(' ', '')}insights.com",
            f"https://local{client.industry.replace(' ', '')}.com"
        ]
        
        for blog in industry_blogs:
            opportunity = BacklinkOpportunity(
                id=str(uuid.uuid4()),
                client_id=client.id,
                target_url=blog,
                target_domain=urlparse(blog).netloc,
                opportunity_type="guest_post",
                contact_email="",  # Would need to extract
                outreach_status="pending",
                priority_score=85.0,
                created_at=datetime.now()
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _find_resource_opportunities(self, client: ClientData) -> List[BacklinkOpportunity]:
        """Find resource page opportunities"""
        opportunities = []
        
        # Local resource pages
        resource_pages = [
            f"https://{client.location.replace(' ', '').lower()}.gov/resources",
            f"https://chamberofcommerce.com/{client.location.replace(' ', '-').lower()}",
            f"https://localbusinessguide.com/{client.location.replace(' ', '-').lower()}"
        ]
        
        for page in resource_pages:
            opportunity = BacklinkOpportunity(
                id=str(uuid.uuid4()),
                client_id=client.id,
                target_url=page,
                target_domain=urlparse(page).netloc,
                opportunity_type="resource_page",
                contact_email="",  # Would need to extract
                outreach_status="pending",
                priority_score=75.0,
                created_at=datetime.now()
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _store_backlink_opportunity(self, opportunity: BacklinkOpportunity):
        """Store backlink opportunity in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO backlink_opportunities 
                (id, client_id, target_url, target_domain, opportunity_type,
                 contact_email, outreach_status, priority_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opportunity.id,
                opportunity.client_id,
                opportunity.target_url,
                opportunity.target_domain,
                opportunity.opportunity_type,
                opportunity.contact_email,
                opportunity.outreach_status,
                opportunity.priority_score,
                opportunity.created_at
            ))
            
            conn.commit()
    
    async def _store_ranking(self, client_id: str, keyword: str, position: int):
        """Store keyword ranking in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO rankings 
                (id, client_id, keyword, position, search_volume, competition_level, tracked_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                client_id,
                keyword,
                position,
                1000,  # Would get from keyword research tool
                "medium",  # Would analyze competition
                datetime.now()
            ))
            
            conn.commit()
    
    async def _get_client(self, client_id: str) -> Optional[ClientData]:
        """Get client from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            row = cursor.fetchone()
            
            if row:
                return ClientData(
                    id=row[0],
                    business_name=row[1],
                    industry=row[2],
                    location=row[3],
                    website=row[4],
                    gmb_profile=row[5],
                    target_keywords=json.loads(row[6]) if row[6] else [],
                    competitors=json.loads(row[7]) if row[7] else [],
                    subscription_tier=row[8],
                    created_at=datetime.fromisoformat(row[9]),
                    status=row[10]
                )
            
            return None
    
    async def run_automated_workflow(self, client_id: str) -> Dict[str, Any]:
        """
        Run the complete automated SEO workflow for a client
        
        This orchestrates all Agent-S tasks:
        1. audit_agent: Perform SEO audit
        2. content_agent: Generate content
        3. outreach_agent: Find backlink opportunities
        4. monitor_agent: Track performance
        """
        self.logger.info(f"Starting automated SEO workflow for client {client_id}")
        
        workflow_results = {
            "client_id": client_id,
            "started_at": datetime.now(),
            "audit_completed": False,
            "content_generated": 0,
            "backlink_opportunities_found": 0,
            "recommendations_generated": 0,
            "errors": []
        }
        
        try:
            # Step 1: Perform SEO audit
            audit = await self.perform_seo_audit(client_id)
            workflow_results["audit_completed"] = True
            workflow_results["recommendations_generated"] = len(audit.recommendations)
            
            # Step 2: Generate content based on audit
            content_pieces = await self.generate_content(client_id, audit.content_gaps)
            workflow_results["content_generated"] = len(content_pieces)
            
            # Step 3: Find backlink opportunities
            opportunities = await self.find_backlink_opportunities(client_id)
            workflow_results["backlink_opportunities_found"] = len(opportunities)
            
            workflow_results["completed_at"] = datetime.now()
            workflow_results["success"] = True
            
            self.logger.info("Automated SEO workflow completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in automated SEO workflow: {e}")
            workflow_results["errors"].append(str(e))
            workflow_results["success"] = False
        
        return workflow_results
    
    async def get_client_analytics(self, client_id: str) -> Dict[str, Any]:
        """Get analytics for a specific client"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get client info
            client = await self._get_client(client_id)
            if not client:
                return {}
            
            # Get content count
            cursor.execute("SELECT COUNT(*) FROM content_pieces WHERE client_id = ?", (client_id,))
            content_count = cursor.fetchone()[0]
            
            # Get backlink opportunities
            cursor.execute("SELECT COUNT(*) FROM backlink_opportunities WHERE client_id = ?", (client_id,))
            opportunities_count = cursor.fetchone()[0]
            
            # Get current rankings
            cursor.execute("SELECT keyword, position FROM rankings WHERE client_id = ? ORDER BY tracked_date DESC", (client_id,))
            rankings = dict(cursor.fetchall())
            
            # Get latest audit
            cursor.execute("SELECT priority_score FROM seo_audits WHERE client_id = ? ORDER BY audit_date DESC LIMIT 1", (client_id,))
            latest_audit = cursor.fetchone()
            priority_score = latest_audit[0] if latest_audit else 0
            
            return {
                "client_name": client.business_name,
                "industry": client.industry,
                "location": client.location,
                "content_pieces": content_count,
                "backlink_opportunities": opportunities_count,
                "current_rankings": rankings,
                "priority_score": priority_score,
                "subscription_tier": client.subscription_tier,
                "last_updated": datetime.now()
            }

# Example usage and testing
async def main():
    """Example usage of the Local SEO Service"""
    
    # Configuration
    config = {
        "google_api_key": "your_google_api_key",
        "gmb_api_key": "your_gmb_api_key",
        "serp_api_key": "your_serp_api_key"
    }
    
    # Initialize service
    seo_service = LocalSEOService(config)
    
    # Sample client data
    client_data = {
        "business_name": "ABC Dental Clinic",
        "industry": "dental",
        "location": "San Francisco, CA",
        "website": "https://abcdental.com",
        "gmb_profile": "https://g.page/abcdental",
        "target_keywords": ["dental clinic san francisco", "dentist near me", "teeth cleaning"],
        "competitors": ["https://xyz-dental.com", "https://premium-dental.com"],
        "subscription_tier": "premium"
    }
    
    # Onboard client
    client = await seo_service.onboard_client(client_data)
    
    # Run automated workflow
    results = await seo_service.run_automated_workflow(client.id)
    
    print("Workflow Results:")
    print(json.dumps(results, indent=2, default=str))
    
    # Get client analytics
    analytics = await seo_service.get_client_analytics(client.id)
    
    print("\nClient Analytics:")
    print(json.dumps(analytics, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
