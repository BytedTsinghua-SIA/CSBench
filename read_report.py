# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
import json
import argparse
import sys
import pandas as pd
from collections import Counter, defaultdict

from src.config import REPORTS_DIR, get_task_log_dir

parser = argparse.ArgumentParser()
parser.add_argument("--report", type=Path, default=None,
                    help='Report directory (default: REPORTS_DIR)')
parser.add_argument("--attempts", type=int, default=None,
                    help='Number of attempts to consider (default: auto-detect)')
args = parser.parse_args()

REPORT_DIR = args.report if args.report else REPORTS_DIR

ls = []
print(len(list(REPORT_DIR.glob("*.json"))))
for f in sorted(REPORT_DIR.glob("*.json")):
    with open(f, "r") as fp:
        try:
            data = json.load(fp)
        except:
            print(f)
            continue
        
        if "attempt_id" in data:
            log_dir = get_task_log_dir(data["task_name"], data["attempt_id"])   
        else:
            log_dir = get_task_log_dir(data["task_name"])

        patch_file = log_dir / "patch"
        json_file = log_dir / "conversation_history.json"
        
        if not patch_file.exists():
            empty_patch = None
        else:
            # empty_patch = not patch_file.read_bytes().strip()
            empty_patch = False
        
        if json_file.exists():
            with open(json_file, "r") as fp:
                data["turn"] = len([x for x in json.load(fp) if x["role"] == "assistant"])
        
        if "evaluate_result" not in data:
            print(f)
        data["name"] = "{}/attempt{}".format(data["task_name"], data["attempt_id"])
        data["empty_patch"] = empty_patch
        ls.append(data)

df = pd.DataFrame(ls)
print(df.columns)

def error_code(x):
    if not isinstance(x, dict):
        return None
    if "Failed to zip" in x["stderr"]:
        if "sudo: command not" in x["stderr"]:
            return "Nosudo"
        elif "Failed to zip repository (code=-1):\nCommand timed out after " in x["stderr"]:
            return "ZipTimedout"
        else:
            return "Zip"
    if "Command timed out after " in x["stderr"]:
        return "Timeout"
    if "passed" in x["stdout"]:
        return bool(x["returncode"])
    return "Error"

df["evaluate"] = df.apply(
    lambda x: (
        x['evaluate_result']
        if x['evaluate_result'] in ["Pass", "Failed"]
        else error_code(x['evaluate_info'])
    ),
    axis=1
)


for col in df.columns:
    if "info" not in col and "name" not in col:
        print(col, Counter(list(df[col])))

def get_name(x):
    if isinstance(x, str) and "-" in x:
        return x.split("-")[0]
    return x

print("docker build fail")
lst = df[df["docker_build"] == False]["name"]
print(list(sorted(get_name(x) for x in lst)))
print("coldstart fail")
lst = df[df["coldstart"] == False]["name"]
print(list(sorted(get_name(x) for x in lst)))
print("run agent fail")
lst = df[df["run_agent"] == False]["name"]
print(list(sorted(get_name(x) for x in lst)))
print("evaluate_timeout")
df['evaluate_timeout'] = df['evaluate_info'].apply(lambda x: isinstance(x, dict) and "stdout" in x and "Command timed out after " in x["stdout"])
lst = df[df['evaluate_timeout'] == True]["name"]
print(list(sorted(get_name(x) for x in lst)))
print("empty patch")
lst = df[df["empty_patch"] == True]["name"]
print(list(sorted(get_name(x) for x in lst)))
print("====Evaluate====")
for bad in ["Error", "Nosudo", "Zip", "ZipTimedout", "Timeout"]:
    lst = df[df["evaluate"] == bad]["name"]
    print(f"{bad}")
    print(list(sorted(get_name(x) for x in lst)))
print("====TooSlow====")
for sample in df.to_dict(orient="records"):
    for col in df.columns:
        if "info" in col and "agent" not in col and "docker" not in col:
            if isinstance(sample[col], dict) and sample[col]['duration'] > 1000:
                print(sample["name"], col, sample[col]['duration'])
print(len(df))
print(df["evaluate_result"].value_counts())

# Count successes per CS ID
if args.attempts is None:
    # Auto-detect the number of attempts by looking at the most common attempt count per CS ID
    attempt_counts = df.groupby('task_name').size()
    args.attempts = attempt_counts.mode().iloc[0] if len(attempt_counts) > 0 else 2
    print(f"Auto-detected {args.attempts} attempts per CS ID")

# Calculate success rate distribution
cs_groups = df.groupby('task_name')
success_counts = []
for cs_id, group in cs_groups:
    group_attempts = group.head(args.attempts)
    passes = len(group_attempts[group_attempts['evaluate'] == 'Pass'])
    if all(group_attempts['evaluate'].isna()):
        passes = -1
    success_counts.append((cs_id, passes))
print(len(cs_groups))
# Calculate 50 turns achieves success rate
has_50_turns = []
for cs_id, group in cs_groups:
    group_attempts = group.head(args.attempts)
    passes = any(group_attempts[group_attempts['turn'] == 50])
    has_50_turns.append(cs_id)
# Calculate 50 turns success rate
print(len(has_50_turns))
# Show success rate distribution
print(f"\n=== SUCCESS RATE DISTRIBUTION ({args.attempts} attempts per CS) ===")
for i in range(-1, args.attempts + 1):
    matching_cs = [cs_id for cs_id, passes in success_counts if passes == i]
    print(f"{i}/{args.attempts} cases: {len(matching_cs)}")
    
# Show detailed breakdown of each success rate
print(f"\n=== DETAILED SUCCESS RATE BREAKDOWN ===")
for i in range(-1,args.attempts + 1):
    matching_cs = [cs_id for cs_id, passes in success_counts if passes == i]
    if matching_cs:
        print(f"{i}/{args.attempts} successes: {matching_cs}")
