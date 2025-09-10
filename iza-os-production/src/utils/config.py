"""
IZA OS Configuration Management
Handles loading and managing configuration from various sources
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class IZAConfig:
    """IZA OS Configuration structure"""
    
    # Server configuration
    server: Dict[str, Any]
    
    # Database configuration
    database: Dict[str, Any]
    
    # AI service configurations
    ai_services: Dict[str, Any]
    
    # Agent configuration
    agents: Dict[str, Any]
    
    # Memory system configuration
    memory: Dict[str, Any]
    
    # Venture factory configuration
    ventures: Dict[str, Any]
    
    # Problem discovery configuration
    discovery: Dict[str, Any]
    
    # Security configuration
    security: Dict[str, Any]
    
    # Development/production flags
    development: bool = False
    debug: bool = False


def load_config() -> Dict[str, Any]:
    """
    Load IZA OS configuration from multiple sources:
    1. Environment variables
    2. .env file
    3. config files (YAML/JSON)
    4. Defaults
    """
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Base configuration with defaults
    config = {
        "server": {
            "host": os.getenv("HOST", "0.0.0.0"),
            "port": int(os.getenv("PORT", 3000)),
            "workers": int(os.getenv("WORKERS", 1)),
            "reload": os.getenv("NODE_ENV") == "development"
        },
        
        "database": {
            "url": os.getenv("DATABASE_URL", "postgresql://localhost/iza_os_dev"),
            "pool_size": int(os.getenv("DB_POOL_SIZE", 10)),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 20)),
            "echo": os.getenv("DB_ECHO", "false").lower() == "true"
        },
        
        "redis": {
            "url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "password": os.getenv("REDIS_PASSWORD"),
            "db": int(os.getenv("REDIS_DB", 0))
        },
        
        "ai_services": {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", 0.7)),
                "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", 2000))
            },
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            }
        },
        
        "agents": {
            "max_concurrent": int(os.getenv("MAX_CONCURRENT_AGENTS", 10)),
            "task_timeout": int(os.getenv("AGENT_TASK_TIMEOUT", 300)),
            "retry_attempts": int(os.getenv("AGENT_RETRY_ATTEMPTS", 3)),
            "types": {
                "venture_creator": {
                    "enabled": True,
                    "max_instances": 3
                },
                "market_analyst": {
                    "enabled": True,
                    "max_instances": 2
                },
                "repository_manager": {
                    "enabled": True,
                    "max_instances": 1
                },
                "system_optimizer": {
                    "enabled": True,
                    "max_instances": 1
                }
            }
        },
        
        "memory": {
            "storage_type": os.getenv("MEMORY_STORAGE_TYPE", "postgresql"),
            "max_entries": int(os.getenv("MEMORY_MAX_ENTRIES", 10000)),
            "retention_days": int(os.getenv("MEMORY_RETENTION_DAYS", 365)),
            "backup_enabled": os.getenv("MEMORY_BACKUP_ENABLED", "true").lower() == "true",
            "backup_interval": int(os.getenv("MEMORY_BACKUP_INTERVAL", 24))  # hours
        },
        
        "ventures": {
            "max_concurrent": int(os.getenv("MAX_CONCURRENT_VENTURES", 478)),
            "templates_path": os.getenv("VENTURE_TEMPLATES_PATH", "src/ventures/templates"),
            "auto_deploy": os.getenv("VENTURE_AUTO_DEPLOY", "false").lower() == "true",
            "default_template": os.getenv("VENTURE_DEFAULT_TEMPLATE", "saas")
        },
        
        "discovery": {
            "enabled_sources": {
                "reddit": os.getenv("REDDIT_ENABLED", "true").lower() == "true",
                "github": os.getenv("GITHUB_ENABLED", "true").lower() == "true",
                "twitter": os.getenv("TWITTER_ENABLED", "true").lower() == "true",
                "producthunt": os.getenv("PRODUCTHUNT_ENABLED", "true").lower() == "true"
            },
            "scan_interval": int(os.getenv("DISCOVERY_SCAN_INTERVAL", 60)),  # minutes
            "pain_threshold": float(os.getenv("DISCOVERY_PAIN_THRESHOLD", 0.7)),
            "market_size_min": int(os.getenv("DISCOVERY_MARKET_SIZE_MIN", 1000))
        },
        
        "apis": {
            "reddit": {
                "client_id": os.getenv("REDDIT_CLIENT_ID"),
                "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
                "user_agent": os.getenv("REDDIT_USER_AGENT", "IZA-OS/1.0")
            },
            "github": {
                "token": os.getenv("GITHUB_TOKEN")
            },
            "twitter": {
                "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
                "api_key": os.getenv("TWITTER_API_KEY"),
                "api_secret": os.getenv("TWITTER_API_SECRET")
            }
        },
        
        "security": {
            "secret_key": os.getenv("SECRET_KEY", "your-secret-key-change-this"),
            "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
            "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)),
            "allowed_hosts": os.getenv("ALLOWED_HOSTS", "*").split(","),
            "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
            "rate_limit": {
                "enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
                "requests_per_minute": int(os.getenv("RATE_LIMIT_RPM", 100))
            }
        },
        
        "logging": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": os.getenv("LOG_FORMAT", "json"),
            "file_enabled": os.getenv("LOG_FILE_ENABLED", "true").lower() == "true",
            "file_path": os.getenv("LOG_FILE_PATH", "logs/iza-os.log"),
            "rotation": os.getenv("LOG_ROTATION", "daily"),
            "retention": int(os.getenv("LOG_RETENTION_DAYS", 30))
        },
        
        "monitoring": {
            "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            "sentry_dsn": os.getenv("SENTRY_DSN"),
            "prometheus_enabled": os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true",
            "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", 60))
        },
        
        "mobile": {
            "pwa_enabled": os.getenv("PWA_ENABLED", "true").lower() == "true",
            "offline_mode": os.getenv("OFFLINE_MODE", "true").lower() == "true",
            "cursor_integration": os.getenv("CURSOR_INTEGRATION", "true").lower() == "true"
        },
        
        # Environment flags
        "development": os.getenv("NODE_ENV") == "development",
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "testing": os.getenv("TESTING", "false").lower() == "true"
    }
    
    # Load additional config from files if they exist
    config_files = [
        "config/default.yaml",
        "config/default.json",
        f"config/{os.getenv('NODE_ENV', 'development')}.yaml",
        f"config/{os.getenv('NODE_ENV', 'development')}.json"
    ]
    
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
                        file_config = yaml.safe_load(f)
                    else:
                        file_config = json.load(f)
                
                # Deep merge file config with existing config
                config = deep_merge(config, file_config)
                
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
    
    return config


def deep_merge(base_dict: Dict[str, Any], override_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with override_dict values taking precedence
    """
    result = base_dict.copy()
    
    for key, value in override_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get a nested configuration value using dot notation
    Example: get_config_value(config, "database.pool_size", 10)
    """
    keys = path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate critical configuration values
    """
    required_fields = [
        "ai_services.openai.api_key",
        "database.url",
        "security.secret_key"
    ]
    
    missing_fields = []
    
    for field in required_fields:
        value = get_config_value(config, field)
        if not value or (isinstance(value, str) and value.startswith("your-")):
            missing_fields.append(field)
    
    if missing_fields:
        print("❌ Missing required configuration:")
        for field in missing_fields:
            print(f"  - {field}")
        print("\nPlease update your .env file with the required values")
        return False
    
    return True


def create_default_config_file(file_path: str = "config/default.yaml"):
    """
    Create a default configuration file template
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    default_config = {
        "server": {
            "host": "0.0.0.0",
            "port": 3000,
            "workers": 1
        },
        "agents": {
            "max_concurrent": 10,
            "task_timeout": 300
        },
        "memory": {
            "max_entries": 10000,
            "retention_days": 365
        },
        "ventures": {
            "max_concurrent": 478,
            "auto_deploy": False
        }
    }
    
    with open(file_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, indent=2)
    
    print(f"✅ Default configuration file created: {file_path}")


if __name__ == "__main__":
    # For testing configuration loading
    config = load_config()
    
    if validate_config(config):
        print("✅ Configuration loaded and validated successfully")
        print(f"Server will run on {config['server']['host']}:{config['server']['port']}")
    else:
        print("❌ Configuration validation failed")
        create_default_config_file()
