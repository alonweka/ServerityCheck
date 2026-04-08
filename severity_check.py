#!/usr/bin/env python3
"""
Severity Check Script for WEKAPP Jira Tickets.

Analyzes Jira tickets from a JQL query against the SeverityCheck.md criteria
using Claude AI to propose priority changes.

Modes:
  dry     - List all tickets with current and proposed priority (no changes)
  actual  - Add comments and labels to tickets with proposed changes
  review  - Review closed tickets, compare outcomes, and learn

Usage:
  python severity_check.py --mode dry --jql "project = WEKAPP AND ..."
  python severity_check.py --mode actual --jql "project = WEKAPP AND ..."
  python severity_check.py --mode review

Requires:
  - config.yaml with Jira credentials and Claude provider settings
  - For direct API: ANTHROPIC_API_KEY environment variable
  - For Bedrock: AWS credentials (via env vars, ~/.aws/credentials, or IAM role)
  - For Vertex AI: Google Cloud credentials (via gcloud auth or service account)
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import yaml
from jira import JIRA
from tabulate import tabulate

# ---------------------------------------------------------------------------
# Progress logging
# ---------------------------------------------------------------------------

_start_time = time.monotonic()


def log(msg: str, level: str = "INFO"):
    """Print a timestamped log message to stderr so progress is always visible."""
    elapsed = time.monotonic() - _start_time
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{elapsed:7.1f}s] [{level:5s}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Graceful shutdown on Ctrl+C
# ---------------------------------------------------------------------------

_shutdown_requested = False


def _handle_sigint(signum, frame):
    global _shutdown_requested
    if _shutdown_requested:
        # Second Ctrl+C — force exit
        log("Force quit.", "WARN")
        sys.exit(1)
    _shutdown_requested = True
    log("Ctrl+C received — finishing current ticket then stopping. Press Ctrl+C again to force quit.", "WARN")


signal.signal(signal.SIGINT, _handle_sigint)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config(config_path: str = "config.yaml") -> dict:
    path = Path(config_path)
    if not path.exists():
        log(f"Config file '{config_path}' not found.", "ERROR")
        log("Copy config.yaml.example to config.yaml and fill in your credentials.", "ERROR")
        sys.exit(1)
    log(f"Loaded config from {config_path}")
    with open(path) as f:
        return yaml.safe_load(f)


def get_anthropic_client(config: dict) -> anthropic.Anthropic:
    """Create a Claude client based on the configured provider.

    Supported providers (set in config.yaml under claude.provider):
      - "direct"  : Uses ANTHROPIC_API_KEY env var (default)
      - "bedrock" : Uses AWS credentials (boto3 credential chain)
      - "vertex"  : Uses Google Cloud credentials (ADC or service account)
    """
    claude_cfg = config.get("claude", {})
    provider = claude_cfg.get("provider", "direct")

    if provider == "bedrock":
        region = claude_cfg.get("aws_region", "us-east-1")
        log(f"Connecting to Claude via AWS Bedrock (region: {region})")
        return anthropic.AnthropicBedrock(aws_region=region)

    elif provider == "vertex":
        project_id = claude_cfg.get("gcp_project_id")
        region = claude_cfg.get("gcp_region", "us-east5")
        if not project_id:
            log("claude.gcp_project_id is required in config.yaml for Vertex AI provider.", "ERROR")
            sys.exit(1)
        log(f"Connecting to Claude via Vertex AI (project: {project_id}, region: {region})")
        return anthropic.AnthropicVertex(project_id=project_id, region=region)

    else:  # direct
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            log("ANTHROPIC_API_KEY environment variable is not set.", "ERROR")
            sys.exit(1)
        log("Connecting to Claude via direct API")
        return anthropic.Anthropic(api_key=api_key)


def get_jira_client(config: dict) -> JIRA:
    jira_cfg = config["jira"]
    log(f"Connecting to Jira at {jira_cfg['url']} as {jira_cfg['email']}")
    client = JIRA(
        server=jira_cfg["url"],
        basic_auth=(jira_cfg["email"], jira_cfg["api_token"]),
    )
    log("Jira connection established")
    return client


# ---------------------------------------------------------------------------
# Severity reference
# ---------------------------------------------------------------------------

def load_severity_reference(config: dict) -> str:
    severity_file = config.get("settings", {}).get("severity_file", "SeverityCheck.md")
    path = Path(severity_file)
    if not path.exists():
        log(f"Severity reference file '{severity_file}' not found.", "ERROR")
        sys.exit(1)
    with open(path) as f:
        content = f.read()
    log(f"Loaded severity reference from {severity_file} ({len(content)} chars)")
    return content


# ---------------------------------------------------------------------------
# Jira helpers
# ---------------------------------------------------------------------------

FIELDS_TO_FETCH = [
    "summary",
    "description",
    "components",
    "labels",
    "status",
    "priority",
    "issuetype",
    "fixVersions",
    "reporter",
    "assignee",
    "comment",
]


def fetch_tickets(jira: JIRA, jql: str) -> list[dict]:
    """Fetch all tickets matching the JQL and extract relevant fields."""
    log(f"Fetching tickets from Jira...")
    log(f"  JQL: {jql}")
    tickets = []
    start = 0
    page_size = 50
    page_num = 0

    while True:
        page_num += 1
        page_start = time.monotonic()
        log(f"  Fetching page {page_num} (offset {start})...")
        issues = jira.search_issues(
            jql,
            startAt=start,
            maxResults=page_size,
            fields=",".join(FIELDS_TO_FETCH),
        )
        if not issues:
            break

        for issue in issues:
            f = issue.fields
            comments_text = ""
            if f.comment and f.comment.comments:
                # Get last 10 comments for context
                recent_comments = f.comment.comments[-10:]
                comments_text = "\n---\n".join(
                    f"[{c.author.displayName} @ {c.created}]: {c.body}"
                    for c in recent_comments
                )

            tickets.append({
                "key": issue.key,
                "summary": f.summary or "",
                "description": (f.description or "")[:3000],  # Truncate long descriptions
                "components": [c.name for c in (f.components or [])],
                "labels": list(f.labels or []),
                "status": str(f.status),
                "priority": str(f.priority),
                "issue_type": str(f.issuetype),
                "fix_versions": [v.name for v in (f.fixVersions or [])],
                "reporter": f.reporter.displayName if f.reporter else "Unknown",
                "assignee": f.assignee.displayName if f.assignee else "Unassigned",
                "comments": comments_text,
            })

        page_elapsed = time.monotonic() - page_start
        log(f"  Page {page_num}: got {len(issues)} tickets ({page_elapsed:.1f}s) — {len(tickets)} total so far")

        start += len(issues)
        if len(issues) < page_size:
            break

    log(f"Fetched {len(tickets)} tickets total")
    return tickets


def add_comment_to_ticket(jira: JIRA, ticket_key: str, comment: str):
    log(f"  Adding comment to {ticket_key}...")
    jira.add_comment(ticket_key, comment)
    log(f"  Comment added to {ticket_key}")


def add_label_to_ticket(jira: JIRA, ticket_key: str, label: str):
    log(f"  Adding label '{label}' to {ticket_key}...")
    issue = jira.issue(ticket_key)
    current_labels = list(issue.fields.labels or [])
    if label not in current_labels:
        current_labels.append(label)
        issue.update(fields={"labels": current_labels})
        log(f"  Label '{label}' added to {ticket_key}")
    else:
        log(f"  Label '{label}' already exists on {ticket_key}, skipping")


# ---------------------------------------------------------------------------
# Claude analysis
# ---------------------------------------------------------------------------

ANALYSIS_SYSTEM_PROMPT = """You are a severity/priority analyst for WEKAPP Jira tickets at Weka.io.

You will be given:
1. A severity criteria reference document
2. A Jira ticket with its fields and comments

Your job is to analyze the ticket and determine if the current Priority is correct based on the severity criteria.

Respond in this exact JSON format (no markdown, no code fences):
{
  "current_priority": "<current priority>",
  "proposed_priority": "<your proposed priority: Critical, Major, Minor, or Blocker>",
  "change_needed": true/false,
  "confidence": "high/medium/low",
  "rationale": "<2-3 sentence explanation referencing specific criteria from the document>"
}
"""


def analyze_ticket(
    client: anthropic.Anthropic,
    ticket: dict,
    severity_ref: str,
    model: str,
) -> dict:
    """Send ticket to Claude for severity analysis."""
    ticket_text = f"""Ticket: {ticket['key']}
Summary: {ticket['summary']}
Description: {ticket['description']}
Components: {', '.join(ticket['components'])}
Labels: {', '.join(ticket['labels'])}
Status: {ticket['status']}
Current Priority: {ticket['priority']}
Issue Type: {ticket['issue_type']}
Fix Versions: {', '.join(ticket['fix_versions'])}
Reporter: {ticket['reporter']}
Assignee: {ticket['assignee']}

Recent Comments:
{ticket['comments'] if ticket['comments'] else '(no comments)'}
"""

    user_message = f"""## Severity Criteria Reference

{severity_ref}

---

## Ticket to Analyze

{ticket_text}

Analyze this ticket's priority based on the severity criteria above. Return your analysis as JSON."""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            attempt_label = f" (attempt {attempt + 1}/{max_retries})" if attempt > 0 else ""
            log(f"  Sending {ticket['key']} to Claude for analysis{attempt_label}...")
            api_start = time.monotonic()
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                system=ANALYSIS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            api_elapsed = time.monotonic() - api_start
            log(f"  Claude responded for {ticket['key']} in {api_elapsed:.1f}s "
                f"(tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out)")
            text = response.content[0].text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[: text.rfind("```")]
                text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError:
            if attempt < max_retries - 1:
                log(f"  Failed to parse Claude response for {ticket['key']}, retrying in 2s...", "WARN")
                time.sleep(2)
            else:
                log(f"  Could not parse Claude response for {ticket['key']} after {max_retries} attempts", "ERROR")
                return {
                    "current_priority": ticket["priority"],
                    "proposed_priority": ticket["priority"],
                    "change_needed": False,
                    "confidence": "low",
                    "rationale": "Error: Could not parse AI analysis response.",
                }
        except anthropic.APIError as e:
            if attempt < max_retries - 1:
                log(f"  API error for {ticket['key']}: {e}. Retrying in 5s...", "WARN")
                time.sleep(5)
            else:
                log(f"  API call failed for {ticket['key']}: {e}", "ERROR")
                return {
                    "current_priority": ticket["priority"],
                    "proposed_priority": ticket["priority"],
                    "change_needed": False,
                    "confidence": "low",
                    "rationale": f"Error: API call failed - {e}",
                }


# ---------------------------------------------------------------------------
# JSON log
# ---------------------------------------------------------------------------

def load_log(log_path: str) -> list[dict]:
    path = Path(log_path)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def save_log(log_path: str, log_data: list[dict]):
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2, default=str)


def find_log_entry(log_data: list[dict], ticket_key: str) -> dict | None:
    for entry in log_data:
        if entry["key"] == ticket_key:
            return entry
    return None


# ---------------------------------------------------------------------------
# Comment formatting
# ---------------------------------------------------------------------------

def build_comment(analysis: dict) -> str:
    return f"""*AI Priority Review*

*Current Priority:* {analysis['current_priority']}
*Proposed Priority:* {analysis['proposed_priority']}
*Confidence:* {analysis['confidence']}

*Rationale:*
{analysis['rationale']}

----

Please reply with 👍 if you agree with this suggestion, or 👎 if you disagree.

_This suggestion was generated by Claude AI (Anthropic) as part of an automated severity review process._"""

AI_COMMENT_MARKER = "AI Priority Review"


def ticket_already_reviewed(ticket: dict) -> str | None:
    """Check if a ticket was already processed by a previous run.

    Returns a reason string if it should be skipped, or None if it needs analysis.
    """
    if "AI-Priority-Check" in ticket["labels"]:
        return "already has 'AI-Priority-Check' label"
    if AI_COMMENT_MARKER in ticket["comments"]:
        return "already has an AI Priority Review comment"
    return None


# ---------------------------------------------------------------------------
# Dry mode
# ---------------------------------------------------------------------------

def run_dry_mode(tickets: list[dict], client: anthropic.Anthropic, severity_ref: str, model: str, config: dict):
    log_path = config.get("settings", {}).get("log_file", "severity_check_log.json")
    log_data = load_log(log_path)

    log(f"Starting DRY RUN — {len(tickets)} tickets to analyze")
    print("=" * 100)

    results = []
    total = len(tickets)
    skipped = 0
    interrupted = False
    for i, ticket in enumerate(tickets, 1):
        if _shutdown_requested:
            log(f"Stopping early — processed {i - 1}/{total} tickets")
            interrupted = True
            break

        log(f"[{i}/{total}] Analyzing {ticket['key']}: \"{ticket['summary'][:70]}\"")
        log(f"  Current priority: {ticket['priority']} | Status: {ticket['status']} | Assignee: {ticket['assignee']}")

        skip_reason = ticket_already_reviewed(ticket)
        if skip_reason:
            log(f"  SKIP — {skip_reason}")
            skipped += 1
            print("-" * 100)
            continue

        ticket_start = time.monotonic()
        analysis = analyze_ticket(client, ticket, severity_ref, model)
        ticket_elapsed = time.monotonic() - ticket_start
        change = "YES" if analysis["change_needed"] else "no"
        if analysis["change_needed"]:
            log(f"  RESULT: CHANGE PROPOSED — {analysis['current_priority']} -> {analysis['proposed_priority']} "
                f"(confidence: {analysis['confidence']}) [{ticket_elapsed:.1f}s]")
            log(f"  Rationale: {analysis['rationale']}")
        else:
            log(f"  RESULT: OK — priority {analysis['current_priority']} is correct "
                f"(confidence: {analysis['confidence']}) [{ticket_elapsed:.1f}s]")
        print("-" * 100)

        results.append({
            "key": ticket["key"],
            "summary": ticket["summary"][:60],
            "current": analysis["current_priority"],
            "proposed": analysis["proposed_priority"],
            "change": change,
            "confidence": analysis["confidence"],
            "rationale": analysis["rationale"],
        })

        # Update log
        entry = find_log_entry(log_data, ticket["key"])
        log_entry = {
            "key": ticket["key"],
            "summary": ticket["summary"],
            "current_priority": analysis["current_priority"],
            "proposed_priority": analysis["proposed_priority"],
            "change_needed": analysis["change_needed"],
            "confidence": analysis["confidence"],
            "rationale": analysis["rationale"],
            "status": ticket["status"],
            "mode": "dry",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reviewed": False,
        }
        if entry:
            entry.update(log_entry)
        else:
            log_data.append(log_entry)

    save_log(log_path, log_data)
    log(f"Log saved to {log_path}")

    # Print summary table
    print("\n" + "=" * 100)
    print("SEVERITY CHECK RESULTS (DRY RUN)")
    print("=" * 100)

    table_data = [
        [r["key"], r["summary"], r["current"], r["proposed"], r["change"], r["confidence"]]
        for r in results
    ]
    print(tabulate(
        table_data,
        headers=["Ticket", "Summary", "Current", "Proposed", "Change?", "Confidence"],
        tablefmt="grid",
        maxcolwidths=[15, 40, 10, 10, 8, 10],
    ))

    changes = [r for r in results if r["change"] == "YES"]
    status = "INTERRUPTED" if interrupted else "COMPLETE"
    log(f"DRY RUN {status} — {len(results)}/{total} tickets analyzed, {skipped} skipped, {len(changes)} changes proposed")

    if changes:
        print("\nProposed changes:")
        for r in changes:
            print(f"  {r['key']}: {r['current']} -> {r['proposed']} ({r['confidence']} confidence)")
            print(f"    Reason: {r['rationale']}")


# ---------------------------------------------------------------------------
# Actual mode
# ---------------------------------------------------------------------------

def run_actual_mode(
    tickets: list[dict],
    jira: JIRA,
    client: anthropic.Anthropic,
    severity_ref: str,
    model: str,
    config: dict,
):
    log_path = config.get("settings", {}).get("log_file", "severity_check_log.json")
    log_data = load_log(log_path)

    total = len(tickets)
    commented = 0
    skipped = 0

    log(f"Starting ACTUAL RUN — {total} tickets to analyze")
    print("=" * 100)

    processed = 0
    for i, ticket in enumerate(tickets, 1):
        if _shutdown_requested:
            log(f"Stopping early — processed {processed}/{total} tickets")
            break

        log(f"[{i}/{total}] Processing {ticket['key']}: \"{ticket['summary'][:70]}\"")
        log(f"  Current priority: {ticket['priority']} | Status: {ticket['status']} | Assignee: {ticket['assignee']}")

        skip_reason = ticket_already_reviewed(ticket)
        if skip_reason:
            log(f"  SKIP — {skip_reason}")
            skipped += 1
            processed += 1
            print("-" * 100)
            continue

        ticket_start = time.monotonic()
        analysis = analyze_ticket(client, ticket, severity_ref, model)
        ticket_elapsed = time.monotonic() - ticket_start

        if not analysis["change_needed"]:
            log(f"  RESULT: OK — priority {analysis['current_priority']} is correct "
                f"(confidence: {analysis['confidence']}) [{ticket_elapsed:.1f}s]")
            # Log it but don't comment
            entry = find_log_entry(log_data, ticket["key"])
            log_entry = {
                "key": ticket["key"],
                "summary": ticket["summary"],
                "current_priority": analysis["current_priority"],
                "proposed_priority": analysis["proposed_priority"],
                "change_needed": False,
                "confidence": analysis["confidence"],
                "rationale": analysis["rationale"],
                "status": ticket["status"],
                "mode": "actual",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reviewed": False,
            }
            if entry:
                entry.update(log_entry)
            else:
                log_data.append(log_entry)
            processed += 1
            print("-" * 100)
            continue

        log(f"  RESULT: CHANGE PROPOSED — {analysis['current_priority']} -> {analysis['proposed_priority']} "
            f"(confidence: {analysis['confidence']}) [{ticket_elapsed:.1f}s]")
        log(f"  Rationale: {analysis['rationale']}")

        # Add comment
        comment = build_comment(analysis)
        add_comment_to_ticket(jira, ticket["key"], comment)

        # Add label
        add_label_to_ticket(jira, ticket["key"], "AI-Priority-Check")

        commented += 1
        processed += 1
        print("-" * 100)

        # Update log
        entry = find_log_entry(log_data, ticket["key"])
        log_entry = {
            "key": ticket["key"],
            "summary": ticket["summary"],
            "current_priority": analysis["current_priority"],
            "proposed_priority": analysis["proposed_priority"],
            "change_needed": True,
            "confidence": analysis["confidence"],
            "rationale": analysis["rationale"],
            "status": ticket["status"],
            "mode": "actual",
            "commented": True,
            "comment_date": datetime.now(timezone.utc).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reviewed": False,
        }
        if entry:
            entry.update(log_entry)
        else:
            log_data.append(log_entry)

    save_log(log_path, log_data)

    status = "INTERRUPTED" if _shutdown_requested else "COMPLETE"
    log(f"ACTUAL RUN {status} — {processed}/{total} tickets processed, {commented} commented, {skipped} skipped")
    log(f"Log saved to {log_path}")


# ---------------------------------------------------------------------------
# Review mode
# ---------------------------------------------------------------------------

LEARNING_SYSTEM_PROMPT = """You are helping maintain the SeverityCheck.md reference document for WEKAPP bug priority decisions.

You will be given:
1. The current SeverityCheck.md content
2. A list of review results — tickets where the AI proposed a priority change and we now know the outcome

For each ticket, you know:
- Whether the priority was actually changed to match the proposal (accepted)
- Whether the ticket owner gave thumbs up or thumbs down feedback
- The final priority of the closed ticket

Based on this data, propose specific edits to the SeverityCheck.md file to improve future accuracy:
- If a proposal was correct (accepted or thumbs up), consider adding it as a confirmed example
- If a proposal was wrong (rejected or thumbs down), consider adding it as a misclassification example
- Only propose changes that add genuine learning value

Respond in this exact JSON format (no markdown, no code fences):
{
  "changes": [
    {
      "section": "<which section to update>",
      "action": "append_row",
      "table_row": "| [TICKET](url) | Component | Summary | **Priority** | Rationale |",
      "explanation": "Why this change improves the document"
    }
  ],
  "summary": "Brief summary of all proposed changes"
}

If no changes are warranted, return:
{
  "changes": [],
  "summary": "No changes needed — insufficient data or no clear learning."
}
"""


def check_feedback_in_comments(jira: JIRA, ticket_key: str, comment_date: str) -> str | None:
    """Check for thumbs up/down replies after the AI comment."""
    issue = jira.issue(ticket_key, fields="comment")
    comments = issue.fields.comment.comments

    # Find comments after our AI comment
    for comment in comments:
        # Skip comments before the AI comment date
        if comment.created < comment_date:
            continue
        body = comment.body.lower()
        if "👍" in body or ":thumbsup:" in body or "thumbs up" in body or "agree" in body:
            return "positive"
        if "👎" in body or ":thumbsdown:" in body or "thumbs down" in body or "disagree" in body:
            return "negative"
    return None


def run_review_mode(jira: JIRA, client: anthropic.Anthropic, severity_ref: str, model: str, config: dict):
    log_path = config.get("settings", {}).get("log_file", "severity_check_log.json")
    severity_file = config.get("settings", {}).get("severity_file", "SeverityCheck.md")
    log_data = load_log(log_path)

    if not log_data:
        log("No log entries found. Run dry or actual mode first.")
        return

    # Find entries that need review (change was proposed, not yet reviewed)
    to_review = [
        entry for entry in log_data
        if entry.get("change_needed") and not entry.get("reviewed")
    ]

    if not to_review:
        log("No unreviewed tickets with proposed changes found.")
        return

    total = len(to_review)
    log(f"Starting REVIEW MODE — {total} tickets to review")
    print("=" * 100)

    review_results = []

    for i, entry in enumerate(to_review, 1):
        if _shutdown_requested:
            log(f"Stopping early — reviewed {i - 1}/{total} tickets")
            break

        key = entry["key"]
        log(f"[{i}/{total}] Reviewing {key}: \"{entry.get('summary', '')[:70]}\"")
        log(f"  Original priority: {entry['current_priority']} | Proposed: {entry['proposed_priority']}")

        try:
            log(f"  Fetching current state from Jira...")
            issue = jira.issue(key, fields="status,priority")
            current_status = str(issue.fields.status)
            current_priority = str(issue.fields.priority)
        except Exception as e:
            log(f"  Error fetching {key}: {e}", "ERROR")
            continue

        # Only review closed tickets (Done or Rejected)
        if current_status not in ("Done", "Rejected", "Fixed"):
            log(f"  SKIP — status is '{current_status}' (not closed)")
            print("-" * 100)
            continue

        proposed = entry["proposed_priority"]
        original = entry["current_priority"]
        priority_changed_to_proposed = current_priority == proposed

        # Check for feedback in comments
        feedback = None
        if entry.get("commented") and entry.get("comment_date"):
            log(f"  Checking for feedback in comments...")
            feedback = check_feedback_in_comments(jira, key, entry["comment_date"])

        outcome = "unknown"
        if priority_changed_to_proposed:
            outcome = "accepted"
        elif current_priority == original:
            outcome = "unchanged"
        else:
            outcome = f"changed_to_{current_priority}"

        log(f"  RESULT: {original} -> {current_priority} (proposed: {proposed}) "
            f"| Outcome: {outcome} | Feedback: {feedback or 'none'}")
        print("-" * 100)

        review_results.append({
            "key": key,
            "summary": entry.get("summary", ""),
            "original_priority": original,
            "proposed_priority": proposed,
            "final_priority": current_priority,
            "outcome": outcome,
            "feedback": feedback,
            "status": current_status,
        })

        # Mark as reviewed in log
        entry["reviewed"] = True
        entry["review_date"] = datetime.now(timezone.utc).isoformat()
        entry["final_priority"] = current_priority
        entry["final_status"] = current_status
        entry["outcome"] = outcome
        entry["feedback"] = feedback

    save_log(log_path, log_data)

    if not review_results:
        log("No closed tickets to review yet.")
        return

    log(f"Review complete — {len(review_results)} closed tickets reviewed")

    # Print review summary
    print("\n" + "=" * 100)
    print("REVIEW RESULTS")
    print("=" * 100)
    table_data = [
        [r["key"], r["original_priority"], r["proposed_priority"],
         r["final_priority"], r["outcome"], r["feedback"] or "-"]
        for r in review_results
    ]
    print(tabulate(
        table_data,
        headers=["Ticket", "Original", "Proposed", "Final", "Outcome", "Feedback"],
        tablefmt="grid",
    ))

    accepted = sum(1 for r in review_results if r["outcome"] == "accepted")
    reviewed_total = len(review_results)
    log(f"Accepted proposals: {accepted}/{reviewed_total}")

    # Ask Claude to propose SeverityCheck.md updates
    results_with_learning = [
        r for r in review_results
        if r["outcome"] in ("accepted", "unchanged") or r["feedback"] in ("positive", "negative")
    ]

    if not results_with_learning:
        log("No actionable learning data from this review cycle.")
        return

    log(f"Sending {len(results_with_learning)} results to Claude for learning analysis...")

    review_text = json.dumps(results_with_learning, indent=2)
    user_message = f"""## Current SeverityCheck.md

{severity_ref}

---

## Review Results

{review_text}

Based on these outcomes, propose specific edits to SeverityCheck.md to improve future severity analysis accuracy."""

    try:
        api_start = time.monotonic()
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=LEARNING_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        api_elapsed = time.monotonic() - api_start
        log(f"Claude learning analysis completed in {api_elapsed:.1f}s "
            f"(tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out)")
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[: text.rfind("```")]
            text = text.strip()
        learning = json.loads(text)
    except Exception as e:
        log(f"Error getting learning suggestions: {e}", "ERROR")
        return

    if not learning.get("changes"):
        log("Claude suggests no changes to SeverityCheck.md at this time.")
        log(f"Reason: {learning.get('summary', 'N/A')}")
        return

    # Show proposed changes and ask for approval
    print("\n" + "=" * 100)
    print("PROPOSED CHANGES TO SeverityCheck.md")
    print("=" * 100)
    print(f"\nSummary: {learning['summary']}\n")

    for i, change in enumerate(learning["changes"], 1):
        print(f"Change {i}:")
        print(f"  Section: {change['section']}")
        print(f"  Action:  {change['action']}")
        print(f"  Content: {change['table_row']}")
        print(f"  Why:     {change['explanation']}")
        print()

    approval = input("Apply these changes to SeverityCheck.md? [y/N]: ").strip().lower()
    if approval != "y":
        print("Changes discarded.")
        return

    # Apply changes
    apply_learning_changes(severity_file, learning["changes"])
    print(f"SeverityCheck.md updated successfully.")


def apply_learning_changes(severity_file: str, changes: list[dict]):
    """Apply approved learning changes to SeverityCheck.md."""
    with open(severity_file) as f:
        content = f.read()

    for change in changes:
        if change["action"] == "append_row":
            section = change["section"]
            row = change["table_row"]

            # Find the section and append the row after the last table row
            lines = content.split("\n")
            new_lines = []
            in_section = False
            last_table_line = -1

            for i, line in enumerate(lines):
                if section.lower() in line.lower():
                    in_section = True
                elif in_section and line.startswith("## "):
                    in_section = False

                if in_section and line.startswith("|"):
                    last_table_line = i

            if last_table_line >= 0:
                lines.insert(last_table_line + 1, row)
                content = "\n".join(lines)
            else:
                # Fallback: append to end of file
                content += f"\n{row}\n"

    with open(severity_file, "w") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="WEKAPP Severity Check - Analyze Jira ticket priorities using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run - analyze tickets without making changes
  python severity_check.py --mode dry --jql "project = WEKAPP AND priority = Critical AND status = Open"

  # Actual run - add comments and labels to tickets
  python severity_check.py --mode actual --jql "project = WEKAPP AND priority = Critical"

  # Review closed tickets and learn from outcomes
  python severity_check.py --mode review
        """,
    )
    parser.add_argument(
        "--mode",
        choices=["dry", "actual", "review"],
        required=True,
        help="Operation mode: dry (list only), actual (comment+label), review (check outcomes)",
    )
    parser.add_argument(
        "--jql",
        type=str,
        help="Jira JQL query to fetch tickets (required for dry and actual modes)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )

    args = parser.parse_args()

    if args.mode in ("dry", "actual") and not args.jql:
        parser.error("--jql is required for dry and actual modes")

    # Load config
    config = load_config(args.config)
    provider = config.get("claude", {}).get("provider", "direct")
    if provider == "bedrock":
        default_model = "us.anthropic.claude-sonnet-4-6-20250514-v1:0"
    else:
        default_model = "claude-sonnet-4-6-20250514"
    model = config.get("settings", {}).get("claude_model", default_model)

    log(f"Mode: {args.mode} | Claude provider: {provider} | Model: {model}")
    severity_ref = load_severity_reference(config)

    # Initialize clients
    jira = get_jira_client(config)
    claude = get_anthropic_client(config)

    if args.mode == "review":
        run_review_mode(jira, claude, severity_ref, model, config)
        total_elapsed = time.monotonic() - _start_time
        log(f"Total run time: {total_elapsed:.1f}s")
        return

    # Fetch tickets
    tickets = fetch_tickets(jira, args.jql)

    if not tickets:
        log("No tickets found. Check your JQL query.")
        return

    if args.mode == "dry":
        run_dry_mode(tickets, claude, severity_ref, model, config)
    elif args.mode == "actual":
        run_actual_mode(tickets, jira, claude, severity_ref, model, config)

    total_elapsed = time.monotonic() - _start_time
    log(f"Total run time: {total_elapsed:.1f}s")


if __name__ == "__main__":
    main()
