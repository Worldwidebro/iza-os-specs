# IZA OS Business Models Package
"""
Business Models Package for IZA OS Production System

This package contains all business model implementations that integrate
with the actual GitHub repositories from the IZA OS ecosystem.
"""

__version__ = "2.0.0"
__author__ = "IZA OS Team"

# Import all business models
from .templates.bm001_resume_builder import ResumeBuilder, ResumeBuilderConfig
from .templates.bm002_etsy_print_on_demand import PrintOnDemandStore, PrintOnDemandConfig
from .templates.bm003_local_seo_service import LocalSEOService, LocalSEOConfig
from .templates.bm004_fitness_meal_coach import FitnessMealCoach, FitnessCoachConfig
from .templates.bm005_youtube_channel_factory import YouTubeChannelFactory, YouTubeFactoryConfig

__all__ = [
    "ResumeBuilder",
    "ResumeBuilderConfig", 
    "PrintOnDemandStore",
    "PrintOnDemandConfig",
    "LocalSEOService",
    "LocalSEOConfig",
    "FitnessMealCoach",
    "FitnessCoachConfig",
    "YouTubeChannelFactory",
    "YouTubeFactoryConfig"
]
