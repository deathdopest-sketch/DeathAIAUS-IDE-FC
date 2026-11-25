#!/usr/bin/env python3
"""
Audit Report Viewer
Displays audit results in a readable format
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def load_latest_report(project_root: Path = None) -> Dict:
    """Load the most recent audit report"""
    if project_root is None:
        project_root = Path.cwd()
    
    audit_dir = project_root / 'audit'
    if not audit_dir.exists():
        print("No audit directory found. Run audit first.")
        sys.exit(1)
    
    reports = list(audit_dir.glob('audit_report_*.json'))
    if not reports:
        print("No audit reports found. Run audit first.")
        sys.exit(1)
    
    # Get most recent
    latest = max(reports, key=lambda p: p.stat().st_mtime)
    
    with open(latest, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_summary(report: Dict):
    """Print audit summary"""
    summary = report['summary']
    
    print("=" * 60)
    print("DEATHAIAUS IDE - E2E AUDIT SUMMARY")
    print("=" * 60)
    print(f"\nTimestamp: {summary['timestamp']}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} [OK]")
    print(f"Failed: {summary['failed']} [FAIL]")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    if summary['success_rate'] >= 95:
        print("\n[EXCELLENT] IDE is production-ready!")
    elif summary['success_rate'] >= 85:
        print("\n[GOOD] Minor issues to address")
    elif summary['success_rate'] >= 70:
        print("\n[FAIR] Several issues need attention")
    else:
        print("\n[POOR] Significant issues found")


def print_phase_results(report: Dict):
    """Print results by phase"""
    print("\n" + "=" * 60)
    print("PHASE RESULTS")
    print("=" * 60)
    
    phase_results = report['phase_results']
    for phase in sorted(phase_results.keys()):
        results = phase_results[phase]
        total = results['total']
        passed = results['passed']
        failed = results['failed']
        rate = (passed / total * 100) if total > 0 else 0
        
        status = "[OK]" if rate >= 95 else "[WARN]" if rate >= 70 else "[FAIL]"
        print(f"\n{status} {phase}: {passed}/{total} passed ({rate:.1f}%)")


def print_issues(report: Dict):
    """Print all issues found"""
    issues = report['issues']
    
    if not issues:
        print("\n" + "=" * 60)
        print("NO ISSUES FOUND! [SUCCESS]")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    print(f"ISSUES FOUND: {len(issues)}")
    print("=" * 60)
    
    # Group by phase
    by_phase = {}
    for issue in issues:
        phase = issue['phase']
        if phase not in by_phase:
            by_phase[phase] = []
        by_phase[phase].append(issue)
    
    for phase in sorted(by_phase.keys()):
        print(f"\n{phase}:")
        for issue in by_phase[phase]:
            print(f"  [FAIL] {issue['test']}")
            print(f"     {issue['message']}")
            if issue.get('details'):
                print(f"     Details: {issue['details']}")


def print_recommendations(report: Dict):
    """Print recommendations based on issues"""
    issues = report['issues']
    
    if not issues:
        return
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = []
    
    for issue in issues:
        test = issue['test'].lower()
        message = issue['message'].lower()
        
        if 'pywebview' in message or 'webview' in test:
            recommendations.append("Install pywebview: pip install pywebview")
        elif 'syntax error' in message:
            recommendations.append(f"Fix syntax error in {issue.get('details', {}).get('file', 'file')}")
        elif 'missing' in message and 'component' in test:
            recommendations.append(f"Verify {issue['test']} is properly integrated")
        elif 'dependency' in test:
            recommendations.append("Install missing dependencies from requirements.txt")
    
    # Remove duplicates
    recommendations = list(set(recommendations))
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("Review issues above for specific fixes needed.")


def main():
    """Main entry point"""
    try:
        report = load_latest_report()
        
        print_summary(report)
        print_phase_results(report)
        print_issues(report)
        print_recommendations(report)
        
        print("\n" + "=" * 60)
        print("For detailed results, see the JSON report file.")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

