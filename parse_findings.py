import json
import os
import sys

def load_findings(filepath):
    """Load Prowler findings from a JSON file."""
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    return data

def summarize_findings(findings):
    """Print a summary of findings by severity."""
    severity_counts = {}
    
    for finding in findings:
        severity = finding.get("Severity", "UNKNOWN")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print("=== Prowler Findings Summary ===")
    for severity, count in sorted(severity_counts.items()):
        print(f"  {severity}: {count}")
    
    return severity_counts

def get_failed_checks(findings):
    """Return only failed checks."""
    failed = [f for f in findings if f.get("Status") == "FAIL"]
    return failed

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_findings.py <findings.json>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    findings = load_findings(filepath)
    summarize_findings(findings)
    
    failed = get_failed_checks(findings)
    print(f"\nTotal failed checks: {len(failed)}")
