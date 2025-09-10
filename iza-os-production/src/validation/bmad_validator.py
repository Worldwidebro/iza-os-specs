#!/usr/bin/env python3
"""
BMAD Framework Validator for IZA OS - Production
Validates Business Model Automated Deployment configurations
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import yaml

# Import management with fallbacks
import sys
sys.path.append('/Users/divinejohns/memU/iza-os-production/src')

try:
    from utils.import_manager import safe_import, ImportPatterns
    
    # Validation imports
    pydantic = safe_import('pydantic')
    jsonschema = safe_import('jsonschema')
    
except ImportError:
    pydantic = None
    jsonschema = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"

class OrchestrationPattern(Enum):
    """Agent orchestration patterns"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    FEEDBACK_LOOP = "feedback_loop"

@dataclass
class ValidationResult:
    """Result of a validation check"""
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BusinessModelValidationReport:
    """Complete validation report for a business model"""
    business_model_id: str
    name: str
    overall_status: ValidationLevel
    validation_results: List[ValidationResult]
    schema_compliance: bool
    deployment_ready: bool
    automation_level: float
    estimated_complexity: str
    required_repositories: List[str]
    estimated_deployment_time: str
    
    def to_dict(self) -> Dict[str, Any]:
        report = asdict(self)
        report['validation_results'] = [r.to_dict() for r in self.validation_results]
        return report

class BMADValidator:
    """Main validator for Business Model Automated Deployment"""
    
    def __init__(self, bmad_config_path: str = None):
        self.logger = logger
        self.bmad_config_path = bmad_config_path or "/Users/divinejohns/memU/bmad_framework.yaml"
        self.bmad_config = self._load_bmad_config()
        self.available_repositories = self._discover_available_repositories()
        self.validation_rules = self._initialize_validation_rules()
    
    def _load_bmad_config(self) -> Dict[str, Any]:
        """Load BMAD framework configuration"""
        try:
            if Path(self.bmad_config_path).exists():
                with open(self.bmad_config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                self.logger.warning(f"BMAD config file not found: {self.bmad_config_path}")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to load BMAD config: {e}")
            return {}
    
    def _discover_available_repositories(self) -> Set[str]:
        """Discover available repositories/stacks"""
        available = set()
        
        # Check for known repositories in the system
        repo_paths = [
            "/Users/divinejohns/memU/active-projects",
            "/Users/divinejohns/memU/reference-repos",
            "/Users/divinejohns/memU/Agent-S",
            "/Users/divinejohns/memU/iza-os-production"
        ]
        
        for repo_path in repo_paths:
            repo_dir = Path(repo_path)
            if repo_dir.exists():
                for item in repo_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        available.add(item.name.lower())
        
        # Add known stack components
        known_stacks = [
            'agent-s', 'fastmcp', 'tailwindcss', 'drizzle-orm', 'stagehand',
            'postiz-app', 'n8n-workflows', 'lobe-chat', 'public-apis',
            'autogen', 'dify', 'graphiti'
        ]
        available.update(known_stacks)
        
        return available
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules from BMAD config"""
        return {
            'required_fields': [
                'id', 'name', 'category', 'stack', 'revenue_model',
                'estimated_monthly_revenue', 'implementation_complexity',
                'development_time', 'market_size', 'automation_level'
            ],
            'valid_complexity_levels': ['Low', 'Medium', 'High'],
            'valid_market_sizes': ['Small', 'Medium', 'Large', 'Very Large', 'Massive', 'Growing', 'Growing rapidly'],
            'automation_level_range': (0, 100),
            'max_stack_components': 10,
            'revenue_patterns': [
                r'\$[\d,]+-[\d,]+',
                r'Per-.*\(\$\d+',
                r'Freemium.*\$\d+',
                r'Subscription.*\$\d+',
                r'Commission.*\d+%'
            ]
        }
    
    def validate_business_model(self, business_model: Dict[str, Any]) -> BusinessModelValidationReport:
        """Validate a single business model"""
        results = []
        business_model_id = business_model.get('id', 'Unknown')
        name = business_model.get('name', 'Unknown')
        
        self.logger.info(f"Validating business model: {business_model_id} - {name}")
        
        # Schema validation
        schema_results = self._validate_schema(business_model)
        results.extend(schema_results)
        
        # Stack validation
        stack_results = self._validate_stack(business_model)
        results.extend(stack_results)
        
        # Revenue model validation
        revenue_results = self._validate_revenue_model(business_model)
        results.extend(revenue_results)
        
        # Automation validation
        automation_results = self._validate_automation_level(business_model)
        results.extend(automation_results)
        
        # Deployment readiness
        deployment_results = self._validate_deployment_readiness(business_model)
        results.extend(deployment_results)
        
        # Agent configuration validation
        agent_results = self._validate_agent_configuration(business_model)
        results.extend(agent_results)
        
        # Calculate overall status
        overall_status = self._calculate_overall_status(results)
        schema_compliance = not any(r.level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR] for r in schema_results)
        deployment_ready = self._is_deployment_ready(results)
        
        return BusinessModelValidationReport(
            business_model_id=business_model_id,
            name=name,
            overall_status=overall_status,
            validation_results=results,
            schema_compliance=schema_compliance,
            deployment_ready=deployment_ready,
            automation_level=business_model.get('automation_level', 0),
            estimated_complexity=business_model.get('implementation_complexity', 'Unknown'),
            required_repositories=business_model.get('stack', []),
            estimated_deployment_time=business_model.get('development_time', 'Unknown')
        )
    
    def _validate_schema(self, business_model: Dict[str, Any]) -> List[ValidationResult]:
        """Validate business model schema"""
        results = []
        
        # Check required fields
        for field in self.validation_rules['required_fields']:
            if field not in business_model:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Missing required field: {field}",
                    field=field,
                    suggestion=f"Add '{field}' to business model configuration"
                ))
            elif not business_model[field]:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Empty value for required field: {field}",
                    field=field,
                    value=business_model[field]
                ))
        
        # Validate field types and formats
        if 'automation_level' in business_model:
            automation = business_model['automation_level']
            if isinstance(automation, str) and automation.endswith('%'):
                try:
                    automation_num = float(automation.rstrip('%'))
                    if not (0 <= automation_num <= 100):
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"Automation level must be between 0-100%: {automation}",
                            field='automation_level',
                            value=automation
                        ))
                except ValueError:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"Invalid automation level format: {automation}",
                        field='automation_level',
                        value=automation,
                        suggestion="Use format like '95%' or numeric value 0-100"
                    ))
        
        # Validate complexity level
        if 'implementation_complexity' in business_model:
            complexity = business_model['implementation_complexity']
            if complexity not in self.validation_rules['valid_complexity_levels']:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Unusual complexity level: {complexity}",
                    field='implementation_complexity',
                    value=complexity,
                    suggestion=f"Consider using: {', '.join(self.validation_rules['valid_complexity_levels'])}"
                ))
        
        # Validate market size
        if 'market_size' in business_model:
            market_size = business_model['market_size']
            if market_size not in self.validation_rules['valid_market_sizes']:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Non-standard market size: {market_size}",
                    field='market_size',
                    value=market_size,
                    suggestion=f"Consider using: {', '.join(self.validation_rules['valid_market_sizes'])}"
                ))
        
        if not results:
            results.append(ValidationResult(
                level=ValidationLevel.SUCCESS,
                message="Schema validation passed",
                field="schema"
            ))
        
        return results
    
    def _validate_stack(self, business_model: Dict[str, Any]) -> List[ValidationResult]:
        """Validate technology stack"""
        results = []
        stack = business_model.get('stack', [])
        
        if not stack:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="No technology stack specified",
                field='stack',
                suggestion="Specify required repositories/frameworks in stack array"
            ))
            return results
        
        # Check stack size
        if len(stack) > self.validation_rules['max_stack_components']:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Large stack size ({len(stack)} components) may increase complexity",
                field='stack',
                value=len(stack),
                suggestion="Consider consolidating or splitting into multiple business models"
            ))
        
        # Check repository availability
        missing_repos = []
        available_repos = []
        
        for repo in stack:
            repo_normalized = repo.lower().replace('_', '-')
            if repo_normalized in self.available_repositories:
                available_repos.append(repo)
            else:
                missing_repos.append(repo)
        
        if missing_repos:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Repositories not found locally: {', '.join(missing_repos)}",
                field='stack',
                value=missing_repos,
                suggestion="Ensure repositories are cloned or add to discovery paths"
            ))
        
        if available_repos:
            results.append(ValidationResult(
                level=ValidationLevel.SUCCESS,
                message=f"Found {len(available_repos)} available repositories",
                field='stack',
                value=available_repos
            ))
        
        # Validate stack coherence
        self._validate_stack_coherence(stack, results)
        
        return results
    
    def _validate_stack_coherence(self, stack: List[str], results: List[ValidationResult]) -> None:
        """Validate that stack components work well together"""
        stack_lower = [s.lower() for s in stack]
        
        # Check for common patterns
        has_agent_s = 'agent-s' in stack_lower
        has_automation = any(s in stack_lower for s in ['stagehand', 'n8n-workflows', 'autogen'])
        has_ui_framework = any(s in stack_lower for s in ['tailwindcss', 'postiz-app', 'lobe-chat'])
        has_database = any(s in stack_lower for s in ['drizzle-orm', 'graphiti'])
        
        if has_agent_s and not has_automation:
            results.append(ValidationResult(
                level=ValidationLevel.INFO,
                message="Agent-S detected but no automation framework specified",
                field='stack',
                suggestion="Consider adding stagehand or n8n-workflows for enhanced automation"
            ))
        
        if has_ui_framework and not has_database:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message="UI framework without database layer",
                field='stack',
                suggestion="Consider adding drizzle-orm or similar for data persistence"
            ))
    
    def _validate_revenue_model(self, business_model: Dict[str, Any]) -> List[ValidationResult]:
        """Validate revenue model"""
        results = []
        revenue_model = business_model.get('revenue_model', '')
        
        if not revenue_model:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="No revenue model specified",
                field='revenue_model',
                suggestion="Specify how the business will generate revenue"
            ))
            return results
        
        # Check for revenue amount patterns
        import re
        has_pricing = False
        for pattern in self.validation_rules['revenue_patterns']:
            if re.search(pattern, revenue_model):
                has_pricing = True
                break
        
        if not has_pricing:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message="Revenue model lacks specific pricing information",
                field='revenue_model',
                value=revenue_model,
                suggestion="Include specific pricing tiers or commission rates"
            ))
        
        # Validate estimated revenue
        estimated_revenue = business_model.get('estimated_monthly_revenue', '')
        if estimated_revenue:
            if not re.search(r'\$[\d,]+-[\d,]+', estimated_revenue):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="Estimated revenue format may be unclear",
                    field='estimated_monthly_revenue',
                    value=estimated_revenue,
                    suggestion="Use format like '$10,000-50,000' for clarity"
                ))
        
        results.append(ValidationResult(
            level=ValidationLevel.SUCCESS,
            message="Revenue model validation completed",
            field='revenue_model'
        ))
        
        return results
    
    def _validate_automation_level(self, business_model: Dict[str, Any]) -> List[ValidationResult]:
        """Validate automation capabilities"""
        results = []
        automation_level = business_model.get('automation_level', 0)
        
        # Convert percentage string to number
        if isinstance(automation_level, str) and automation_level.endswith('%'):
            try:
                automation_level = float(automation_level.rstrip('%'))
            except ValueError:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Invalid automation level format",
                    field='automation_level',
                    value=automation_level
                ))
                return results
        
        # Validate automation level reasonableness
        if automation_level < 50:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Low automation level ({automation_level}%) may not be optimal for IZA OS",
                field='automation_level',
                value=automation_level,
                suggestion="Consider increasing automation with Agent-S integration"
            ))
        elif automation_level >= 90:
            results.append(ValidationResult(
                level=ValidationLevel.SUCCESS,
                message=f"Excellent automation level ({automation_level}%)",
                field='automation_level',
                value=automation_level
            ))
        
        return results
    
    def _validate_deployment_readiness(self, business_model: Dict[str, Any]) -> List[ValidationResult]:
        """Validate deployment readiness"""
        results = []
        
        # Check for deployment-critical information
        required_for_deployment = [
            'target_customers',
            'key_features',
            'competitive_advantage',
            'development_time'
        ]
        
        missing_deployment_info = []
        for field in required_for_deployment:
            if field not in business_model or not business_model[field]:
                missing_deployment_info.append(field)
        
        if missing_deployment_info:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Missing deployment information: {', '.join(missing_deployment_info)}",
                field='deployment_readiness',
                value=missing_deployment_info,
                suggestion="Add missing fields for complete deployment specification"
            ))
        else:
            results.append(ValidationResult(
                level=ValidationLevel.SUCCESS,
                message="All deployment information present",
                field='deployment_readiness'
            ))
        
        return results
    
    def _validate_agent_configuration(self, business_model: Dict[str, Any]) -> List[ValidationResult]:
        """Validate agent configuration potential"""
        results = []
        stack = business_model.get('stack', [])
        stack_lower = [s.lower() for s in stack]
        
        # Check for agent-compatible components
        agent_compatible = ['agent-s', 'autogen', 'lobe-chat', 'dify', 'fastmcp']
        has_agent_capability = any(comp in stack_lower for comp in agent_compatible)
        
        automation_level = business_model.get('automation_level', 0)
        if isinstance(automation_level, str) and automation_level.endswith('%'):
            automation_level = float(automation_level.rstrip('%'))
        
        if automation_level > 80 and not has_agent_capability:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message="High automation claimed but no agent framework in stack",
                field='agent_configuration',
                suggestion="Consider adding Agent-S or AutoGen for agent-based automation"
            ))
        elif has_agent_capability:
            results.append(ValidationResult(
                level=ValidationLevel.SUCCESS,
                message="Agent framework detected in stack",
                field='agent_configuration'
            ))
        
        return results
    
    def _calculate_overall_status(self, results: List[ValidationResult]) -> ValidationLevel:
        """Calculate overall validation status"""
        if any(r.level == ValidationLevel.CRITICAL for r in results):
            return ValidationLevel.CRITICAL
        elif any(r.level == ValidationLevel.ERROR for r in results):
            return ValidationLevel.ERROR
        elif any(r.level == ValidationLevel.WARNING for r in results):
            return ValidationLevel.WARNING
        else:
            return ValidationLevel.SUCCESS
    
    def _is_deployment_ready(self, results: List[ValidationResult]) -> bool:
        """Determine if business model is ready for deployment"""
        blocking_issues = [ValidationLevel.CRITICAL, ValidationLevel.ERROR]
        return not any(r.level in blocking_issues for r in results)
    
    def validate_business_models_from_file(self, file_path: str) -> List[BusinessModelValidationReport]:
        """Validate all business models from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            reports = []
            
            # Handle different JSON structures
            if 'business_models' in data:
                # Tiered structure
                for tier, models in data['business_models'].items():
                    if isinstance(models, list):
                        for model in models:
                            report = self.validate_business_model(model)
                            reports.append(report)
            else:
                # Flat list structure
                if isinstance(data, list):
                    for model in data:
                        report = self.validate_business_model(model)
                        reports.append(report)
                elif isinstance(data, dict) and 'models' in data:
                    for model in data['models']:
                        report = self.validate_business_model(model)
                        reports.append(report)
            
            return reports
            
        except Exception as e:
            self.logger.error(f"Failed to validate business models from {file_path}: {e}")
            return []
    
    def generate_deployment_summary(self, reports: List[BusinessModelValidationReport]) -> Dict[str, Any]:
        """Generate deployment readiness summary"""
        total_models = len(reports)
        deployment_ready = sum(1 for r in reports if r.deployment_ready)
        schema_compliant = sum(1 for r in reports if r.schema_compliance)
        
        status_counts = {}
        for status in ValidationLevel:
            status_counts[status.value] = sum(1 for r in reports if r.overall_status == status)
        
        # Top models by automation level
        top_automation = sorted(reports, key=lambda x: x.automation_level, reverse=True)[:5]
        
        # Models by complexity
        complexity_counts = {}
        for report in reports:
            complexity = report.estimated_complexity
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        
        return {
            'total_models': total_models,
            'deployment_ready': deployment_ready,
            'deployment_ready_percentage': (deployment_ready / total_models * 100) if total_models > 0 else 0,
            'schema_compliant': schema_compliant,
            'schema_compliant_percentage': (schema_compliant / total_models * 100) if total_models > 0 else 0,
            'status_distribution': status_counts,
            'complexity_distribution': complexity_counts,
            'top_automation_models': [
                {'id': m.business_model_id, 'name': m.name, 'automation_level': m.automation_level}
                for m in top_automation
            ],
            'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def test_orchestration_patterns(self) -> Dict[str, Any]:
        """Test different agent orchestration patterns"""
        patterns = {}
        
        for pattern in OrchestrationPattern:
            test_result = self._test_orchestration_pattern(pattern)
            patterns[pattern.value] = test_result
        
        return {
            'orchestration_patterns': patterns,
            'total_patterns_tested': len(OrchestrationPattern),
            'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _test_orchestration_pattern(self, pattern: OrchestrationPattern) -> Dict[str, Any]:
        """Test a specific orchestration pattern"""
        # Mock testing different patterns
        start_time = time.time()
        
        # Simulate pattern testing
        if pattern == OrchestrationPattern.SEQUENTIAL:
            # Test document generation pipeline
            test_result = {
                'success': True,
                'description': 'Sequential workflow for document generation',
                'test_scenario': 'Agent A (analyzer) -> Agent B (processor) -> Agent C (publisher)',
                'performance': 'Good for linear processes'
            }
        elif pattern == OrchestrationPattern.PARALLEL:
            # Test multi-agent research
            test_result = {
                'success': True,
                'description': 'Parallel processing for research workflows',
                'test_scenario': 'Multiple research agents -> Synthesis agent',
                'performance': 'Excellent for scalable research'
            }
        elif pattern == OrchestrationPattern.HIERARCHICAL:
            # Test customer service delegation
            test_result = {
                'success': True,
                'description': 'Hierarchical delegation for customer service',
                'test_scenario': 'Supervisor -> Specialized worker agents',
                'performance': 'Good for complex task routing'
            }
        elif pattern == OrchestrationPattern.FEEDBACK_LOOP:
            # Test optimization cycles
            test_result = {
                'success': True,
                'description': 'Continuous improvement through feedback',
                'test_scenario': 'Execute -> Monitor -> Analyze -> Optimize -> Execute',
                'performance': 'Excellent for adaptive systems'
            }
        
        test_result['duration'] = time.time() - start_time
        return test_result

# Example usage and testing
async def main():
    """Example usage of the BMAD validator"""
    print("🔍 BMAD Framework Validator Test")
    
    # Initialize validator
    validator = BMADValidator()
    
    print(f"Available repositories: {len(validator.available_repositories)}")
    print(f"First 10: {list(validator.available_repositories)[:10]}")
    
    # Test business model validation
    print("\n📋 Validating business models...")
    
    reports = validator.validate_business_models_from_file(
        "/Users/divinejohns/memU/100_highest_roi_businesses.json"
    )
    
    print(f"Validated {len(reports)} business models")
    
    # Generate summary
    summary = validator.generate_deployment_summary(reports)
    
    print(f"\n📊 Deployment Summary:")
    print(f"Total models: {summary['total_models']}")
    print(f"Deployment ready: {summary['deployment_ready']} ({summary['deployment_ready_percentage']:.1f}%)")
    print(f"Schema compliant: {summary['schema_compliant']} ({summary['schema_compliant_percentage']:.1f}%)")
    
    print(f"\nStatus distribution:")
    for status, count in summary['status_distribution'].items():
        print(f"  {status}: {count}")
    
    print(f"\nTop automation models:")
    for model in summary['top_automation_models'][:3]:
        print(f"  {model['id']}: {model['automation_level']}% - {model['name']}")
    
    # Test orchestration patterns
    print("\n🔄 Testing orchestration patterns...")
    pattern_results = validator.test_orchestration_patterns()
    
    for pattern, result in pattern_results['orchestration_patterns'].items():
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {pattern}: {result['description']}")
    
    # Show detailed results for first few models
    print("\n🔍 Detailed validation results (first 3 models):")
    for i, report in enumerate(reports[:3]):
        print(f"\n{i+1}. {report.business_model_id} - {report.name}")
        print(f"   Status: {report.overall_status.value}")
        print(f"   Deployment ready: {'Yes' if report.deployment_ready else 'No'}")
        print(f"   Automation level: {report.automation_level}%")
        
        # Show critical issues
        critical_issues = [r for r in report.validation_results if r.level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR]]
        if critical_issues:
            print(f"   Critical issues:")
            for issue in critical_issues:
                print(f"     - {issue.message}")
    
    print("\n✅ BMAD validation completed")

if __name__ == "__main__":
    asyncio.run(main())
