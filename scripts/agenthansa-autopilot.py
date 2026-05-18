#!/usr/bin/env python3
"""AgentHansa Auto-Pilot — daily check-in + task monitor (from .env config)"""
import json, os, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = "https://www.agenthansa.com"

env_path = Path(__file__).parent.parent / '.env'
TOKEN = ''
WALLET = ''
if env_path.exists():
    for line in open(env_path):
        line = line.strip()
        if line.startswith('AH_TOKEN='):
            TOKEN = line.split('=', 1)[1]
        elif line.startswith('AH_WALLET='):
            WALLET = line.split('=', 1)[1]

if not TOKEN:
    print("ERROR: AH_TOKEN not set in .env")
    sys.exit(1)

def api(method, path, data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}

def check_in():
    """Daily check-in"""
    print('🏁 Daily check-in...')
    r = api('POST', '/api/checkin')
    if 'error' not in r:
        reward = r.get('reward', r.get('amount', 'unknown'))
        print(f'  ✅ Check-in success! Reward: {reward}')
        return True
    print(f'  ❌ Check-in failed: {r.get("error", "")}')
    return False

def get_profile():
    r = api('GET', '/api/user/profile')
    if 'error' not in r:
        rep = r.get('reputation', r.get('score', '?'))
        lvl = r.get('level', '?')
        streak = r.get('streak', 0)
        print(f'  Profile: Level {lvl} | Reputation {rep} | Streak {streak}')
        return r
    print(f'  ❌ Profile: {r.get("error", "")}')
    return None

def check_red_packets():
    r = api('GET', '/api/redpackets/available')
    if 'error' not in r:
        packets = r if isinstance(r, list) else r.get('data', [])
        if packets:
            for p in packets[:3]:
                pid = p.get('id', '?')
                amt = p.get('amount', '?')
                print(f'  🧧 Red packet #{pid}: {amt}')
        else:
            print('  📭 No red packets available')
    return r

def get_bounties():
    r = api('GET', '/api/bounties')
    if 'error' not in r:
        bounties = r if isinstance(r, list) else r.get('data', [])
        print(f'  📋 Available bounties: {len(bounties)}')
        for b in bounties[:3]:
            print(f'     • {b.get("title", "?")} — {b.get("reward", "?")}')
    return r

def run():
    print(f'===== 🤖 AgentHansa Autopilot =====')
    check_in()
    get_profile()
    check_red_packets()
    get_bounties()
    print(f'\n--- Done ---')

if __name__ == '__main__':
    run()
