import os
import re
import yaml
import subprocess
from datetime import datetime
import argparse

# Configuration
DOC_PATH = "Final_Deliverables/Documentation.md"
AUDIT_LOG_HEADER = "| Date | Contributor | Section Updated | Reason / Rationale |"

def get_git_info():
    """Detects current branch and maps it to a contributor."""
    try:
        branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()
    except:
        branch = "unknown"
    
    mapping = {
        "feature/balu/": "K. Bala Chowdappa",
        "feature/uday/": "Uday",
        "feature/nishitha/": "Nishitha",
        "feature/ai/": "AI Agent"
    }
    
    contributor = "Unknown"
    for pattern, name in mapping.items():
        if branch.startswith(pattern):
            contributor = name
            break
    
    return branch, contributor

def update_version(content, contributor):
    """Updates the document version and date."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    version_pattern = r"(### Document Version\s+)\bv\d+\.\d+.*"
    
    # Try to find existing version
    match = re.search(r"v(\d+)\.(\d+)", content)
    if match:
        major = match.group(1)
        minor = int(match.group(2)) + 1
        new_version = f"v{major}.{minor} ({contributor} | {date_str})"
        content = re.sub(version_pattern, f"\\1{new_version}", content)
    
    return content

def update_audit_log(content, contributor, sections, reasoning):
    """Adds a new entry to the SR. DEV AUDIT LOG."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"| {date_str} | {contributor} | {', '.join(sections)} | {reasoning} |"
    
    # Find the audit log table
    log_pattern = r"\| Date \| Contributor \| Section Updated \| Reason / Rationale \|\s*\n\| :--- \| :--- \| :--- \| :--- \|"
    match = re.search(log_pattern, content)
    
    if match:
        insertion_point = match.end()
        # Ensure we are on a new line
        content = content[:insertion_point] + "\n" + new_entry + content[insertion_point:]
            
    return content

def apply_updates(content, updates, contributor):
    """Parses the document and replaces [TO FILL] based on field names."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    for update in updates:
        field = update.get("field")
        value = update.get("value")
        reason = update.get("reasoning", "")
        proof = update.get("proof", "")
        
        # Format the replacement string if it's not a direct table value
        # Some tables have specific columns for Reason/Proof, others don't
        # We'll try to find the row starting with the field name
        
        # Escaping field name for regex
        escaped_field = re.escape(field)
        
        # Pattern to find the row and the first [TO FILL]
        # This matches the field name and then looks for the next [TO FILL] in the same line
        row_pattern = rf"(^\|.*{escaped_field}.*?)\| \[TO FILL\]"
        
        # For D1.1 type tables where there are multiple [TO FILL] in one row:
        # Decision | Options | [TO FILL] (Decision) | [TO FILL] (Evidence)
        # We replace them sequentially
        
        if field in ["Primary Vector Store", "Graph Store", "Sparse Search", "LLM Serving", "Orchestration Framework", "Fusion Strategy"]:
            # These are D1.1 specific replacements
            content = re.sub(row_pattern, f"\\g<1>{value} ({reason})", content, count=1, flags=re.MULTILINE)
            content = re.sub(row_pattern, f"\\g<1>{proof}", content, count=1, flags=re.MULTILINE)
        else:
            # General replacement
            formatted_value = f"{value} ({contributor} | {date_str} | {reason} | {proof})"
            content = re.sub(row_pattern, f"\\g<1>{formatted_value}", content, count=1, flags=re.MULTILINE)
            
    return content

def main():
    parser = argparse.ArgumentParser(description="AI-PMS RAG Bootcamp Deliverables Auto-Updater")
    parser.add_argument("--yaml", required=True, help="Path to the YAML submission file")
    args = parser.parse_args()
    
    if not os.path.exists(args.yaml):
        print(f"Error: YAML file not found at {args.yaml}")
        return

    with open(args.yaml, 'r') as f:
        data = yaml.safe_load(f)
    
    updates = data.get("updates", [])
    if not updates:
        print("No updates found in YAML.")
        return

    branch, contributor = get_git_info()
    print(f"Detected Contributor: {contributor} (Branch: {branch})")
    
    if not os.path.exists(DOC_PATH):
        print(f"Error: Documentation file not found at {DOC_PATH}")
        return

    with open(DOC_PATH, 'r') as f:
        content = f.read()

    # 1. Apply field updates
    content = apply_updates(content, updates, contributor)
    
    # 2. Update Version
    content = update_version(content, contributor)
    
    # 3. Update Audit Log
    sections = list(set([u.get("section", "Misc") for u in updates]))
    reasoning = updates[0].get("reasoning", "Bulk update") if updates else "Manual update"
    content = update_audit_log(content, contributor, sections, reasoning)
    
    with open(DOC_PATH, 'w') as f:
        f.write(content)
    
    version_match = re.search(r'v\d+\.\d+', content)
    version_str = version_match.group(0) if version_match else 'N/A'
    print(f"Successfully updated {DOC_PATH}")
    print(f"New Version: {version_str}")

if __name__ == "__main__":
    main()
