# AWS Security Audit — Prowler Cloud Security Assessment & DevSecOps Pipeline

## Overview
Two-part hands-on security project. First, I used Prowler to audit an AWS account against CIS Benchmarks, triaging and remediating critical findings. Then I extended the project by building an automated CI/CD security pipeline using GitHub Actions — integrating Bandit for Python static analysis and Trivy for dependency vulnerability scanning, reducing findings from 22 CVEs to 7 through targeted dependency patching.

**Tools used:** Prowler v3, AWS CLI, IAM, Bandit, Trivy, GitHub Actions  
**Scope:** AWS free-tier account, us-east-1 region  
**Framework:** CIS AWS Foundations Benchmark

---

## Repository Structure

| File | Purpose |
|---|---|
| `parse_findings.py` | Python script for parsing Prowler JSON output — scanned by Bandit |
| `requirements.txt` | Python dependencies — scanned by Trivy for CVEs |
| `.github/workflows/security-scan.yml` | GitHub Actions pipeline definition |
| `prowler-output/` | Raw Prowler scan reports (before and after remediation) |

---

## Scan Results Summary

| | Before | After |
|---|---|---|
| Total Checks | 301 | 301 |
| Failed | 63 | 58 |
| Passed | 37 | 46 |

---

## Key Findings & Remediation

| # | Finding | Severity | Status | Risk |
|---|---|---|---|---|
| 1 | Root account MFA not enabled | 🔴 Critical | ✅ Fixed | Full account takeover with stolen password |
| 2 | CloudTrail multi-region logging disabled | 🟠 High | ✅ Fixed | Zero audit trail — attacker activity undetectable |
| 3 | IAM password policy too weak | 🟡 Medium | ✅ Fixed | IAM users vulnerable to brute force |
| 4 | S3 account-level public access blocks disabled | 🟠 High | 📋 Documented | Accidental bucket exposure risk |
| 5 | Default security group allows unrestricted traffic | 🟠 High | 📋 Documented | New EC2 instances exposed by default |
| 6 | VPC Flow Logs not enabled | 🟡 Medium | 📋 Documented | No network traffic visibility |
| 7 | IAM Access Analyzer not enabled | 🔵 Low | 📋 Documented | External resource sharing undetected |

---

## Remediation Details

### Finding 1 — Root Account MFA (Critical) ✅
**What it means:** The AWS root account had no multi-factor authentication. Root has unrestricted access to everything in the account — billing, IAM, all services. A single stolen password would mean full account compromise.  
**Fix:** Enabled software MFA via authenticator app on root account. Hardware MFA (YubiKey) noted as enterprise best practice but out of scope for personal account.  
**Result:** `iam_root_mfa_enabled` resolved. `iam_root_hardware_mfa_enabled` remains as expected for non-enterprise setup.

### Finding 2 — CloudTrail Multi-Region Logging (High) ✅
**What it means:** No CloudTrail trail was configured, meaning zero API activity was being logged across any AWS region. An attacker could spin up resources, exfiltrate data, or move laterally with no audit trail.  
**Fix:** Created a multi-region CloudTrail trail writing to a dedicated S3 bucket, capturing all management events across all regions.  
**Result:** `cloudtrail_multi_region_enabled` resolved. Additional CloudTrail findings now visible because Prowler can inspect the trail configuration — expected behavior.

### Finding 3 — IAM Password Policy (Medium) ✅
**What it means:** Default AWS password policy allows weak passwords — no minimum length, no complexity requirements, no expiration.  
**Fix:** Enforced 14-character minimum, uppercase, lowercase, numbers, symbols, 90-day expiration, 24-password reuse prevention.  
**Result:** 7 password policy findings resolved in a single fix.

---

## Remaining Findings (Documented, Not Remediated)

| Finding | Reason Not Fixed |
|---|---|
| S3 public access blocks | No S3 buckets in account — low practical risk, would enable as standard practice in production |
| Default security group | No EC2 instances deployed — would restrict on first deployment |
| VPC Flow Logs | Requires active VPC traffic to be meaningful — noted for production setup |
| IAM Access Analyzer | Free to enable — would activate in any production account |

---

## CI/CD Security Pipeline — Automated Vulnerability Scanning

### Overview
After completing the Prowler audit, I extended this project by building an automated security scanning pipeline using GitHub Actions. Every push to this repository triggers two security tools that scan the codebase and dependencies for vulnerabilities — no manual intervention required.

**Tools used:** Bandit, Trivy, GitHub Actions  
**Scan triggers:** Every push to `main` or `add-devsecops-pipeline`, every pull request to `main`  
**Pipeline file:** `.github/workflows/security-scan.yml`

---

### How the Pipeline Works

Every push to GitHub triggers GitHub Actions, which spins up a fresh Linux runner, runs Bandit against the Python source code, then runs Trivy against requirements.txt, and saves both reports as downloadable artifacts.

---

### Tool 1: Bandit (Static Analysis)
Bandit reads Python source code without executing it, flagging known dangerous patterns — hardcoded secrets, weak cryptography, SQL injection risks, insecure shell usage.

**Result:** No issues found in `parse_findings.py` — code is clean.

---

### Tool 2: Trivy (Dependency Scanning)
Trivy checks every library in `requirements.txt` against its CVE database, reporting known vulnerabilities by severity with direct links to advisories and fixed versions.

**Initial scan — 22 vulnerabilities found:**

| Library | Version | Severity | CVE | Issue |
|---|---|---|---|---|
| urllib3 | 1.26.13 | 🔴 HIGH | CVE-2023-43804 | Cookie headers leaked during cross-origin redirects |
| cryptography | 38.0.0 | 🔴 HIGH | CVE-2023-0286 | OpenSSL type confusion in X.509 handling |
| cryptography | 38.0.0 | 🔴 HIGH | CVE-2023-50782 | Bleichenbacher timing oracle attack against RSA |
| requests | 2.28.0 | 🟡 MEDIUM | CVE-2023-32681 | Proxy-Authorization header leaked on redirect |
| paramiko | 2.11.0 | 🟡 MEDIUM | CVE-2023-48795 | Terrapin — SSH prefix truncation attack |

**Remediation — patched 3 libraries:**

| Library | Before | After | Result |
|---|---|---|---|
| requests | 2.28.0 | 2.32.4 | ✅ 4 CVEs resolved |
| urllib3 | 1.26.13 | 2.6.0 | ✅ 5 CVEs resolved |
| cryptography | 38.0.0 | 42.0.4 | ✅ 4 CVEs resolved |
| paramiko | 2.11.0 | 2.11.0 | ⚠️ Accepted risk — see below |

**Post-remediation scan — 7 vulnerabilities remaining**

---

### Accepted Risk: paramiko

`paramiko 2.11.0` contains CVE-2023-48795 (Terrapin attack, MEDIUM severity). The fix requires upgrading to `3.x`, which is a breaking major version change. In a real project this would require regression testing before deployment. Documented here as accepted risk pending compatibility verification — this is standard practice in production security workflows.

---

## Setup & Reproduction

### Part 1 — Prowler Cloud Audit
1. Create a read-only IAM user with `SecurityAudit` and `ViewOnlyAccess` policies
2. Configure AWS CLI profile: `aws configure --profile prowler`
3. Run Prowler: `prowler aws --profile prowler -M html json -o ./prowler-output -f us-east-1`
4. Review HTML report in `./prowler-output/`

> ⚠️ Never commit AWS credentials, account IDs, or access keys to this repository.

### Part 2 — CI/CD Security Pipeline

**The pipeline runs automatically on every push — no setup needed to see it work. Just push code and check the Actions tab.**

To run the tools locally before pushing:

**Bandit (Python static analysis):**
```bash
pip install bandit
bandit -r . -f json -o bandit-report.json
```

**Trivy (dependency scanning):**
```bash
brew install trivy
trivy fs . --severity CRITICAL,HIGH,MEDIUM
```

**To view pipeline results on GitHub:**
1. Go to the Actions tab on this repository
2. Click the most recent Security Scan run
3. Click the `security-scan` job
4. Expand `Run Bandit` or `Run Trivy filesystem scan` to see findings
5. Scroll to the bottom of the run page to download `bandit-report` or `trivy-report` artifacts

---

## Scan Reports
- 📊 [Before Remediation Report](./report-before.html)
- 📊 [After Remediation Report](./report-after.html)

---

## What This Project Demonstrates
- Writing GitHub Actions YAML for automated security workflows
- Integrating Bandit and Trivy into a CI/CD pipeline
- Reading and triaging CVE findings by severity
- Making documented remediation decisions vs. accepted risk calls
- Reducing attack surface from 22 → 7 findings through dependency patching

--- 

## What I Learned
- How to create least-privilege IAM users for security tooling
- How to interpret CIS Benchmark findings and prioritize by severity
- Why CloudTrail is the foundation of AWS incident response
- How default AWS configurations leave accounts exposed out of the box
- The difference between findings that need immediate remediation vs. accepted risk documentation
- How to write a GitHub Actions workflow that runs security tools automatically on every push
- What CVEs are and how to read Trivy output to understand severity, affected version, and fix version
- Why dependency scanning matters — unpatched libraries are one of the most common real-world attack vectors
- That patching dependencies isn't a one-time fix — new CVEs drop against newly patched versions constantly
- The difference between static analysis (Bandit reads your code) and dependency scanning (Trivy checks your libraries)
- How to make and document an accepted risk decision when a fix carries breaking change risk