#!/usr/bin/env python3
"""Market Monitor — watchlist + crypto scans (combines crypto_scan + crypto_watch)"""
import json, subprocess, os, sys, datetime
from pathlib import Path

WATCHLIST = ['BTC', 'ETH', 'SOL', 'BSB', 'ARB', 'SUI', 'MON', 'TRX']

def get_data(symbol):
    url = f'https://min-api.cryptocompare.com/data/v2/histohour?fsym={symbol}&tsym=USD&limit=48'
    r = subprocess.run(['curl','-s','--max-time','8', url], capture_output=True,text=True,timeout=10)
    try:
        d=json.loads(r.stdout)
        vals=[x for x in d['Data']['Data'] if x['close']>0]
        if len(vals)<14: return None
        c=[x['close'] for x in vals]
        vol=[x['volumefrom'] for x in vals]
        h=[x['high'] for x in vals]
        l=[x['low'] for x in vals]
        return {'close':c,'vol':vol,'price':c[-1],'high':h,'low':l,'chg24':(c[-1]-c[0])/c[0]*100}
    except: return None

def calc_rsi(prices, n=14):
    if len(prices)<n+1: return 50
    g,l=[],[]
    for j in range(1,len(prices)):
        d=prices[j]-prices[j-1];g.append(max(d,0));l.append(max(-d,0))
    if sum(l[:n])==0: return 100
    ag,al=sum(g[:n])/n,sum(l[:n])/n
    r=100-100/(1+ag/al)
    for j in range(n,len(g)):
        ag=(ag*(n-1)+g[j])/n;al=(al*(n-1)+l[j])/n
        r=100-100/(1+(ag/al if al>0 else 999))
    return r

def scan():
    now = datetime.datetime.now().strftime('%m-%d %H:%M')
    print(f'===== 📊 Market Monitor [{now}] =====')
    print(f'{"Symbol":>6} {"Price":>10} {"24h%":>8} {"RSI":>6} {"Signal":>12}')
    print('-' * 45)
    for sym in WATCHLIST:
        d = get_data(sym)
        if not d: continue
        rsi = calc_rsi(d['close'])
        signal = '🟢 Long' if rsi <= 32 else ('🔴 Short' if rsi >= 67 else '⚪ Neutral')
        print(f'{sym:>6} ${d["price"]:>8.4f} {d["chg24"]:>+7.2f}% {rsi:>5.0f} {signal}')
    print()

if __name__ == '__main__':
    scan()
