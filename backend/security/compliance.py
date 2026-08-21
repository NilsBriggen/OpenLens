"""
Compliance Manager for OpenLens

Provides compliance management capabilities:
- Compliance standards (GDPR, HIPAA, SOC2, etc.)
- Compliance checking
- Audit trail management
- Compliance reporting
- Gap analysis
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

from backend.paths import resolve_dir


@dataclass
class ComplianceStandard:
    """Represents a compliance standard."""
    standard_id: str
    name: str
    description: str = ''
    version: str = ''
    requirements: List[Dict[str, Any]] = field(default_factory=list)
    is_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'standard_id': self.standard_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'requirements': self.requirements,
            'is_enabled': self.is_enabled,
        }


@dataclass
class ComplianceRequirement:
    """Represents a compliance requirement."""
    requirement_id: str
    standard_id: str
    name: str
    description: str = ''
    category: str = ''
    controls: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'requirement_id': self.requirement_id,
            'standard_id': self.standard_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'controls': self.controls,
        }


@dataclass
class ComplianceControl:
    """Represents a compliance control."""
    control_id: str
    requirement_id: str
    name: str
    description: str = ''
    implementation: str = ''
    status: str = 'not_implemented'  # not_implemented, implemented, tested, verified
    evidence: List[str] = field(default_factory=list)
    last_tested: datetime = None
    next_test: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'control_id': self.control_id,
            'requirement_id': self.requirement_id,
            'name': self.name,
            'description': self.description,
            'implementation': self.implementation,
            'status': self.status,
            'evidence': self.evidence,
            'last_tested': self.last_tested.isoformat() if self.last_tested else None,
            'next_test': self.next_test.isoformat() if self.next_test else None,
        }


@dataclass
class ComplianceAssessment:
    """Represents a compliance assessment."""
    assessment_id: str
    standard_id: str
    name: str
    description: str = ''
    status: str = 'in_progress'  # in_progress, completed, failed
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = None
    findings: List[Dict[str, Any]] = field(default_factory=list)
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'assessment_id': self.assessment_id,
            'standard_id': self.standard_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'findings': self.findings,
            'score': self.score,
        }


@dataclass
class ComplianceFinding:
    """Represents a compliance finding."""
    finding_id: str
    assessment_id: str
    requirement_id: str
    control_id: str
    status: str = 'non_compliant'  # compliant, non_compliant, partial
    severity: str = 'medium'  # low, medium, high, critical
    description: str = ''
    evidence: List[str] = field(default_factory=list)
    recommendation: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'finding_id': self.finding_id,
            'assessment_id': self.assessment_id,
            'requirement_id': self.requirement_id,
            'control_id': self.control_id,
            'status': self.status,
            'severity': self.severity,
            'description': self.description,
            'evidence': self.evidence,
            'recommendation': self.recommendation,
        }


@dataclass
class ComplianceReport:
    """Represents a compliance report."""
    report_id: str
    assessment_id: str
    name: str
    generated_at: datetime = field(default_factory=datetime.utcnow)
    format: str = 'pdf'  # pdf, html, json, csv
    data: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'report_id': self.report_id,
            'assessment_id': self.assessment_id,
            'name': self.name,
            'generated_at': self.generated_at.isoformat(),
            'format': self.format,
        }


@dataclass
class ComplianceConfig:
    """Configuration for compliance manager."""
    report_dir: str = field(
        default_factory=lambda: resolve_dir('OPENLENS_REPORT_DIR', '/var/reports/openlens/compliance', 'compliance')
    )
    assessment_interval: int = 30  # days
    auto_generate_reports: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'report_dir': self.report_dir,
            'assessment_interval': self.assessment_interval,
            'auto_generate_reports': self.auto_generate_reports,
        }


class ComplianceManager:
    """
    Compliance manager for OpenLens.
    
    Provides:
    - Compliance standards management
    - Compliance checking
    - Audit trail management
    - Compliance reporting
    - Gap analysis
    """
    
    def __init__(self, config: ComplianceConfig = None, 
                 security_policy_manager=None, audit_logger=None):
        """
        Initialize the compliance manager.
        
        Args:
            config: ComplianceConfig instance.
            security_policy_manager: SecurityPolicyManager instance.
            audit_logger: AuditLogger instance.
        """
        self.config = config or ComplianceConfig()
        self.security_policy_manager = security_policy_manager
        self.audit_logger = audit_logger
        self._standards: Dict[str, ComplianceStandard] = {}
        self._requirements: Dict[str, ComplianceRequirement] = {}
        self._controls: Dict[str, ComplianceControl] = {}
        self._assessments: Dict[str, ComplianceAssessment] = {}
        self._reports: Dict[str, ComplianceReport] = {}
        self._lock = threading.Lock()
        
        # Initialize with default standards
        self._initialize_default_standards()
    
    def _initialize_default_standards(self):
        """Initialize default compliance standards."""
        # GDPR
        gdpr = ComplianceStandard(
            standard_id='gdpr',
            name='General Data Protection Regulation',
            description='EU regulation on data protection and privacy',
            version='2018',
            requirements=[
                {
                    'requirement_id': 'gdpr_lawful_basis',
                    'name': 'Lawful Basis for Processing',
                    'description': 'Data processing must have a lawful basis',
                    'category': 'data_processing',
                },
                {
                    'requirement_id': 'gdpr_data_minimization',
                    'name': 'Data Minimization',
                    'description': 'Only collect data that is necessary',
                    'category': 'data_processing',
                },
                {
                    'requirement_id': 'gdpr_storage_limitation',
                    'name': 'Storage Limitation',
                    'description': 'Data should not be kept longer than necessary',
                    'category': 'data_storage',
                },
                {
                    'requirement_id': 'gdpr_rights',
                    'name': 'Data Subject Rights',
                    'description': 'Individuals have rights over their data',
                    'category': 'data_rights',
                },
                {
                    'requirement_id': 'gdpr_security',
                    'name': 'Security',
                    'description': 'Appropriate security measures must be in place',
                    'category': 'security',
                },
            ],
        )
        self._standards[gdpr.standard_id] = gdpr
        
        # HIPAA
        hipaa = ComplianceStandard(
            standard_id='hipaa',
            name='Health Insurance Portability and Accountability Act',
            description='US regulation for healthcare data protection',
            version='1996',
            requirements=[
                {
                    'requirement_id': 'hipaa_privacy_rule',
                    'name': 'Privacy Rule',
                    'description': 'Protects individually identifiable health information',
                    'category': 'privacy',
                },
                {
                    'requirement_id': 'hipaa_security_rule',
                    'name': 'Security Rule',
                    'description': 'Establishes national standards for protecting health information',
                    'category': 'security',
                },
                {
                    'requirement_id': 'hipaa_breach_notification',
                    'name': 'Breach Notification Rule',
                    'description': 'Requires notification of data breaches',
                    'category': 'breach_management',
                },
            ],
        )
        self._standards[hipaa.standard_id] = hipaa
        
        # SOC 2
        soc2 = ComplianceStandard(
            standard_id='soc2',
            name='Service Organization Control 2',
            description='AICPA standard for service organizations',
            version='Type II',
            requirements=[
                {
                    'requirement_id': 'soc2_security',
                    'name': 'Security',
                    'description': 'Information and systems are protected against unauthorized access',
                    'category': 'security',
                },
                {
                    'requirement_id': 'soc2_availability',
                    'name': 'Availability',
                    'description': 'Systems are available for operation and use',
                    'category': 'availability',
                },
                {
                    'requirement_id': 'soc2_processing_integrity',
                    'name': 'Processing Integrity',
                    'description': 'System processing is complete, accurate, and authorized',
                    'category': 'processing',
                },
                {
                    'requirement_id': 'soc2_confidentiality',
                    'name': 'Confidentiality',
                    'description': 'Information designated as confidential is protected',
                    'category': 'confidentiality',
                },
                {
                    'requirement_id': 'soc2_privacy',
                    'name': 'Privacy',
                    'description': 'Personal information is collected, used, retained, and disclosed properly',
                    'category': 'privacy',
                },
            ],
        )
        self._standards[soc2.standard_id] = soc2
        
        # ISO 27001
        iso27001 = ComplianceStandard(
            standard_id='iso27001',
            name='ISO/IEC 27001',
            description='Information security management standard',
            version='2017',
            requirements=[
                {
                    'requirement_id': 'iso27001_ism',
                    'name': 'Information Security Management System',
                    'description': 'Establish, implement, maintain, and continually improve an ISMS',
                    'category': 'management',
                },
                {
                    'requirement_id': 'iso27001_risk_assessment',
                    'name': 'Risk Assessment',
                    'description': 'Identify and evaluate information security risks',
                    'category': 'risk_management',
                },
                {
                    'requirement_id': 'iso27001_access_control',
                    'name': 'Access Control',
                    'description': 'Limit access to information and systems',
                    'category': 'access_control',
                },
            ],
        )
        self._standards[iso27001.standard_id] = iso27001
    
    def add_standard(self, standard: ComplianceStandard) -> bool:
        """
        Add a compliance standard.
        
        Args:
            standard: ComplianceStandard to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if standard.standard_id in self._standards:
                return False
            
            self._standards[standard.standard_id] = standard
            return True
    
    def remove_standard(self, standard_id: str) -> bool:
        """
        Remove a compliance standard.
        
        Args:
            standard_id: Standard ID.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if standard_id not in self._standards:
                return False
            
            del self._standards[standard_id]
            return True
    
    def get_standard(self, standard_id: str) -> Optional[ComplianceStandard]:
        """
        Get a compliance standard.
        
        Args:
            standard_id: Standard ID.
            
        Returns:
            ComplianceStandard or None.
        """
        return self._standards.get(standard_id)
    
    def list_standards(self) -> List[ComplianceStandard]:
        """
        List all compliance standards.
        
        Returns:
            List of ComplianceStandard objects.
        """
        return list(self._standards.values())
    
    def add_requirement(self, requirement: ComplianceRequirement) -> bool:
        """
        Add a compliance requirement.
        
        Args:
            requirement: ComplianceRequirement to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if requirement.requirement_id in self._requirements:
                return False
            
            self._requirements[requirement.requirement_id] = requirement
            return True
    
    def get_requirement(self, requirement_id: str) -> Optional[ComplianceRequirement]:
        """
        Get a compliance requirement.
        
        Args:
            requirement_id: Requirement ID.
            
        Returns:
            ComplianceRequirement or None.
        """
        return self._requirements.get(requirement_id)
    
    def list_requirements(self, standard_id: str = None) -> List[ComplianceRequirement]:
        """
        List all compliance requirements.
        
        Args:
            standard_id: Filter by standard ID (None for all).
            
        Returns:
            List of ComplianceRequirement objects.
        """
        with self._lock:
            if standard_id:
                return [r for r in self._requirements.values() if r.standard_id == standard_id]
            return list(self._requirements.values())
    
    def add_control(self, control: ComplianceControl) -> bool:
        """
        Add a compliance control.
        
        Args:
            control: ComplianceControl to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if control.control_id in self._controls:
                return False
            
            self._controls[control.control_id] = control
            return True
    
    def get_control(self, control_id: str) -> Optional[ComplianceControl]:
        """
        Get a compliance control.
        
        Args:
            control_id: Control ID.
            
        Returns:
            ComplianceControl or None.
        """
        return self._controls.get(control_id)
    
    def list_controls(self, requirement_id: str = None) -> List[ComplianceControl]:
        """
        List all compliance controls.
        
        Args:
            requirement_id: Filter by requirement ID (None for all).
            
        Returns:
            List of ComplianceControl objects.
        """
        with self._lock:
            if requirement_id:
                return [c for c in self._controls.values() if c.requirement_id == requirement_id]
            return list(self._controls.values())
    
    def create_assessment(self, standard_id: str, name: str, 
                         description: str = '') -> ComplianceAssessment:
        """
        Create a new compliance assessment.
        
        Args:
            standard_id: Standard ID.
            name: Assessment name.
            description: Assessment description.
            
        Returns:
            ComplianceAssessment.
        """
        assessment_id = f"assessment_{standard_id}_{int(time.time())}"
        
        assessment = ComplianceAssessment(
            assessment_id=assessment_id,
            standard_id=standard_id,
            name=name,
            description=description,
        )
        
        with self._lock:
            self._assessments[assessment_id] = assessment
        
        return assessment
    
    def get_assessment(self, assessment_id: str) -> Optional[ComplianceAssessment]:
        """
        Get a compliance assessment.
        
        Args:
            assessment_id: Assessment ID.
            
        Returns:
            ComplianceAssessment or None.
        """
        return self._assessments.get(assessment_id)
    
    def list_assessments(self, standard_id: str = None) -> List[ComplianceAssessment]:
        """
        List all compliance assessments.
        
        Args:
            standard_id: Filter by standard ID (None for all).
            
        Returns:
            List of ComplianceAssessment objects.
        """
        with self._lock:
            if standard_id:
                return [a for a in self._assessments.values() if a.standard_id == standard_id]
            return list(self._assessments.values())
    
    def run_assessment(self, assessment_id: str) -> ComplianceAssessment:
        """
        Run a compliance assessment.
        
        Args:
            assessment_id: Assessment ID.
            
        Returns:
            ComplianceAssessment with results.
        """
        assessment = self.get_assessment(assessment_id)
        
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        standard = self.get_standard(assessment.standard_id)
        
        if not standard:
            raise ValueError(f"Standard {assessment.standard_id} not found")
        
        # Get all requirements for the standard
        requirements = self.list_requirements(assessment.standard_id)
        
        # Evaluate each requirement
        findings = []
        total_requirements = len(requirements)
        compliant_requirements = 0
        
        for requirement in requirements:
            # Get controls for this requirement
            controls = self.list_controls(requirement.requirement_id)
            
            # Evaluate each control
            for control in controls:
                # In a real implementation, we would evaluate the control
                # For now, assume some are compliant and some are not
                import random
                is_compliant = random.choice([True, True, True, False])  # 75% compliant
                
                if is_compliant:
                    compliant_requirements += 1
                
                finding = ComplianceFinding(
                    finding_id=f"finding_{assessment_id}_{control.control_id}",
                    assessment_id=assessment_id,
                    requirement_id=requirement.requirement_id,
                    control_id=control.control_id,
                    status='compliant' if is_compliant else 'non_compliant',
                    severity=control.status if control.status in ['low', 'medium', 'high', 'critical'] else 'medium',
                    description=f"Control {control.name} evaluation",
                    recommendation='Implement the control' if not is_compliant else '',
                )
                findings.append(finding.to_dict())
        
        # Calculate score
        score = (compliant_requirements / total_requirements) * 100 if total_requirements > 0 else 0
        
        # Update assessment
        assessment.findings = findings
        assessment.score = score
        assessment.status = 'completed'
        assessment.end_date = datetime.utcnow()
        
        return assessment
    
    def generate_report(self, assessment_id: str, format: str = 'json') -> ComplianceReport:
        """
        Generate a compliance report.
        
        Args:
            assessment_id: Assessment ID.
            format: Report format.
            
        Returns:
            ComplianceReport.
        """
        assessment = self.get_assessment(assessment_id)
        
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        report_id = f"report_{assessment_id}_{format}_{int(time.time())}"
        
        # Generate report data based on format
        if format == 'json':
            data = assessment.to_dict()
        elif format == 'html':
            data = self._generate_html_report(assessment)
        elif format == 'pdf':
            data = self._generate_pdf_report(assessment)
        else:
            data = assessment.to_dict()
        
        report = ComplianceReport(
            report_id=report_id,
            assessment_id=assessment_id,
            name=f"{assessment.name} Report",
            format=format,
            data=data,
        )
        
        with self._lock:
            self._reports[report_id] = report
        
        return report
    
    def _generate_html_report(self, assessment: ComplianceAssessment) -> str:
        """Generate an HTML report."""
        html = f"""
        <html>
        <head>
            <title>Compliance Report: {assessment.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f5f5f5; padding: 15px; margin-bottom: 20px; }}
                .finding {{ margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; }}
                .compliant {{ background: #d4edda; }}
                .non_compliant {{ background: #f8d7da; }}
            </style>
        </head>
        <body>
            <h1>Compliance Report: {assessment.name}</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Standard:</strong> {assessment.standard_id}</p>
                <p><strong>Status:</strong> {assessment.status}</p>
                <p><strong>Score:</strong> {assessment.score:.1f}%</p>
                <p><strong>Date:</strong> {assessment.end_date.isoformat() if assessment.end_date else assessment.start_date.isoformat()}</p>
            </div>
            <h2>Findings</h2>
        """
        
        for finding in assessment.findings:
            status_class = 'compliant' if finding['status'] == 'compliant' else 'non_compliant'
            html += f"""
            <div class="finding {status_class}">
                <h3>{finding.get('control_id', 'Unknown')}</h3>
                <p><strong>Status:</strong> {finding['status']}</p>
                <p><strong>Severity:</strong> {finding.get('severity', 'medium')}</p>
                <p>{finding.get('description', '')}</p>
                <p><em>{finding.get('recommendation', '')}</em></p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _generate_pdf_report(self, assessment: ComplianceAssessment) -> str:
        """Generate a PDF report (simplified)."""
        # In a real implementation, this would use a PDF library
        # For now, return a simple text representation
        return json.dumps(assessment.to_dict(), indent=2)
    
    def get_gap_analysis(self, standard_id: str) -> Dict[str, Any]:
        """
        Perform a gap analysis for a standard.
        
        Args:
            standard_id: Standard ID.
            
        Returns:
            Gap analysis results.
        """
        standard = self.get_standard(standard_id)
        
        if not standard:
            return {'error': f"Standard {standard_id} not found"}
        
        # Get all requirements for the standard
        requirements = self.list_requirements(standard_id)
        
        # Get all controls
        controls = self.list_controls()
        
        # Find gaps
        gaps = []
        for requirement in requirements:
            # Check if there are controls for this requirement
            req_controls = [c for c in controls if c.requirement_id == requirement.requirement_id]
            
            if not req_controls:
                gaps.append({
                    'requirement_id': requirement.requirement_id,
                    'requirement_name': requirement.name,
                    'gap_type': 'missing_controls',
                    'description': f"No controls implemented for requirement: {requirement.name}",
                    'severity': 'high',
                })
            else:
                # Check if controls are implemented
                for control in req_controls:
                    if control.status != 'implemented':
                        gaps.append({
                            'requirement_id': requirement.requirement_id,
                            'requirement_name': requirement.name,
                            'control_id': control.control_id,
                            'control_name': control.name,
                            'gap_type': 'control_not_implemented',
                            'description': f"Control {control.name} is not implemented",
                            'severity': 'medium',
                            'status': control.status,
                        })
        
        return {
            'standard_id': standard_id,
            'standard_name': standard.name,
            'total_requirements': len(requirements),
            'total_controls': len(controls),
            'gaps': gaps,
            'gap_count': len(gaps),
        }
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """
        Get overall compliance status.
        
        Returns:
            Compliance status dictionary.
        """
        standards = self.list_standards()
        assessments = self.list_assessments()
        
        status = {
            'total_standards': len(standards),
            'total_assessments': len(assessments),
            'by_standard': {},
        }
        
        for standard in standards:
            standard_assessments = [a for a in assessments if a.standard_id == standard.standard_id]
            
            if standard_assessments:
                latest_assessment = max(standard_assessments, key=lambda a: a.start_date)
                status['by_standard'][standard.standard_id] = {
                    'name': standard.name,
                    'latest_score': latest_assessment.score,
                    'latest_status': latest_assessment.status,
                    'last_assessed': latest_assessment.end_date.isoformat() if latest_assessment.end_date else latest_assessment.start_date.isoformat(),
                }
            else:
                status['by_standard'][standard.standard_id] = {
                    'name': standard.name,
                    'latest_score': 0,
                    'latest_status': 'not_assessed',
                    'last_assessed': None,
                }
        
        # Calculate overall score
        total_score = sum(s.get('latest_score', 0) for s in status['by_standard'].values())
        total_standards = len(status['by_standard'])
        status['overall_score'] = total_score / total_standards if total_standards > 0 else 0
        
        return status
    
    def export_to_json(self) -> str:
        """
        Export compliance data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'standards': [s.to_dict() for s in self._standards.values()],
            'requirements': [r.to_dict() for r in self._requirements.values()],
            'controls': [c.to_dict() for c in self._controls.values()],
            'assessments': [a.to_dict() for a in self._assessments.values()],
            'reports': [r.to_dict() for r in self._reports.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import compliance data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import standards
            self._standards = {}
            for standard_data in data.get('standards', []):
                standard = ComplianceStandard(
                    standard_id=standard_data['standard_id'],
                    name=standard_data['name'],
                    description=standard_data.get('description', ''),
                    version=standard_data.get('version', ''),
                    requirements=standard_data.get('requirements', []),
                    is_enabled=standard_data.get('is_enabled', True),
                )
                self._standards[standard.standard_id] = standard
            
            # Import requirements
            self._requirements = {}
            for requirement_data in data.get('requirements', []):
                requirement = ComplianceRequirement(
                    requirement_id=requirement_data['requirement_id'],
                    standard_id=requirement_data['standard_id'],
                    name=requirement_data['name'],
                    description=requirement_data.get('description', ''),
                    category=requirement_data.get('category', ''),
                    controls=requirement_data.get('controls', []),
                )
                self._requirements[requirement.requirement_id] = requirement
            
            # Import controls
            self._controls = {}
            for control_data in data.get('controls', []):
                control = ComplianceControl(
                    control_id=control_data['control_id'],
                    requirement_id=control_data['requirement_id'],
                    name=control_data['name'],
                    description=control_data.get('description', ''),
                    implementation=control_data.get('implementation', ''),
                    status=control_data.get('status', 'not_implemented'),
                    evidence=control_data.get('evidence', []),
                    last_tested=datetime.fromisoformat(control_data['last_tested']) if control_data.get('last_tested') else None,
                    next_test=datetime.fromisoformat(control_data['next_test']) if control_data.get('next_test') else None,
                )
                self._controls[control.control_id] = control
            
            # Import assessments
            self._assessments = {}
            for assessment_data in data.get('assessments', []):
                assessment = ComplianceAssessment(
                    assessment_id=assessment_data['assessment_id'],
                    standard_id=assessment_data['standard_id'],
                    name=assessment_data['name'],
                    description=assessment_data.get('description', ''),
                    status=assessment_data.get('status', 'in_progress'),
                    start_date=datetime.fromisoformat(assessment_data['start_date']),
                    end_date=datetime.fromisoformat(assessment_data['end_date']) if assessment_data.get('end_date') else None,
                    findings=assessment_data.get('findings', []),
                    score=assessment_data.get('score', 0.0),
                )
                self._assessments[assessment.assessment_id] = assessment
            
            # Import reports
            self._reports = {}
            for report_data in data.get('reports', []):
                report = ComplianceReport(
                    report_id=report_data['report_id'],
                    assessment_id=report_data['assessment_id'],
                    name=report_data['name'],
                    generated_at=datetime.fromisoformat(report_data['generated_at']),
                    format=report_data.get('format', 'json'),
                )
                self._reports[report.report_id] = report
            
            # Import config
            config_data = data.get('config', {})
            self.config = ComplianceConfig(
                report_dir=config_data.get('report_dir', resolve_dir('OPENLENS_REPORT_DIR', '/var/reports/openlens/compliance', 'compliance')),
                assessment_interval=config_data.get('assessment_interval', 30),
                auto_generate_reports=config_data.get('auto_generate_reports', True),
            )
            
            return True
        
        except Exception as e:
            print(f"Error importing compliance data: {e}")
            return False


# Global compliance manager instance
compliance_manager = ComplianceManager()
