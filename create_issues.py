import csv
import subprocess

CSV_PATH = "documentation/FEATURES_BUGS_ISSUES.csv"

with open(CSV_PATH, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        title = row['Title']
        body = row['Description']
        labels = row['Type']
        status = row['Status']
        priority = row['Priority']
        assignee = row['Assignee']

        issue_body = f"**Status:** {status}\n**Priority:** {priority}\n**Assignee:** {assignee}\n\n{body}"
        cmd = [
            'gh', 'issue', 'create',
            '--title', title,
            '--body', issue_body,
            '--label', labels
        ]
        subprocess.run(cmd)

print("Issue creation complete.")
