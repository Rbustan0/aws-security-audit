# AWS Security Audit — Prowler Cloud Security Assessment

## Overview
Hands-on cloud security project using Prowler, an open-source AWS security scanner, to audit an AWS account against CIS Benchmarks and AWS Foundational Security Best Practices. Findings were triaged by severity, critical issues remediated, and results documented with before/after evidence.

**Tools used:** Prowler v3, AWS CLI, IAM  
**Scope:** AWS free-tier account, us-east-1 region  
**Framework:** CIS AWS Foundations Benchmark

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

## What I Learned
- How to create least-privilege IAM users for security tooling
- How to interpret CIS Benchmark findings and prioritize by severity
- Why CloudTrail is the foundation of AWS incident response
- How default AWS configurations leave accounts exposed out of the box
- The difference between findings that need immediate remediation vs. accepted risk documentation

---

## Setup & Reproduction
1. Create a read-only IAM user with `SecurityAudit` and `ViewOnlyAccess` policies
2. Configure AWS CLI profile: `aws configure --profile prowler`
3. Run Prowler: `prowler aws --profile prowler -M html json -o ./prowler-output -f us-east-1`
4. Review HTML report in `./prowler-output/`

> ⚠️ Never commit AWS credentials, account IDs, or access keys to this repository.

---

## Scan Reports
- 📊 [Before Remediation Report](./report-before.html)
- 📊 [After Remediation Report](./report-after.html)
