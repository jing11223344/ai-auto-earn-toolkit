#!/usr/bin/env python3
"""Bounty Scanner — scans GitHub for real, claimable bounties (Python 3)"""
import json, os, sys, re, urllib.request, urllib.parse
from pathlib import Path

# Load from .env
env_path = Path(__file__).parent.parent / '.env'
GITHUB_TOKEN = ''
if env_path.exists():
    for line in open(env_path):
        line = line.strip()
        if line.startswith('GITHUB_TOKEN='):
            GITHUB_TOKEN = line.split('=', 1)[1]
            break

# Scam repos to exclude
SCAM_REPOS = [
    'ClankerNation/OpenAgents', 'SecureBananaLabs/bug-bounty',
    'UnsafeLabs/Bounty-Hunters', 'Scottcjn/rustchain-bounties',
    'claude-builders-bounty/claude-builders-bounty', 'yeheskieltame/claudelance',
]

def gh(query, per_page=20):
    url = f'https://api.github.com/search/issues?q={urllib.parse.quote(query)}&sort=created&order=desc&per_page={per_page}'
    headers = {'User-Agent': 'BountyHunter/1.0'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read())
    except Exception as e:
        return {'error': str(e), 'items': []}

def is_scam(repo_name):
    for s in SCAM_REPOS:
        if s.lower() in repo_name.lower():
            return True
    return False

def scan():
    print('===== 🎯 Bounty Scanner =====\n')
    queries = [
        ('funded by Algora state:open type:issue', '💰 Algora'),
        ('label:bounty state:open type:issue', '🏷️ Bounty Label'),
        ('"bug bounty" state:open type:issue', '🐛 Bug Bounty'),
        ('label:"help wanted" state:open type:issue', '🤝 Help Wanted'),
    ]
    total = 0
    for q, label in queries:
        print(f'--- {label} ---')
        r = gh(q, 5)
        if 'error' in r:
            print(f'  ⚠️ {r["error"]}')
            continue
        items = r.get('items', [])
        if not items:
            print('  (none)')
            continue
        for issue in items[:5]:
            repo = issue['repository_url'].replace('https://api.github.com/repos/', '')
            if is_scam(repo):
                continue
            title = issue.get('title', 'No title')
            url = issue.get('html_url', '')
            state = issue.get('state', '')
            comments = issue.get('comments', 0)
            print(f'  📄 [{repo}] {title}')
            print(f'     {url}')
            print(f'     State: {state} | Comments: {comments}')
            total += 1
        print()
    print(f'Total find: {total} bounties')

if __name__ == '__main__':
    scan()
