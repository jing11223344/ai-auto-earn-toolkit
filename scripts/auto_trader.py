#!/usr/bin/env python3
"""自动交易系统 v1 — 动量衰竭框架 + OKX执行"""
import json, subprocess, hmac, base64, hashlib, datetime, os, sys, time
from pathlib import Path

# ===== 从 .env 加载配置 =====
def load_env():
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print("ERROR: .env not found! Run: cp .env.example .env and fill in your keys")
        sys.exit(1)
    for line in open(env_path):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()

load_env()

API_KEY = os.getenv('OKX_API_KEY', '')
SECRET_KEY = os.getenv('OKX_SECRET_KEY', '')
PASSPHRASE = os.getenv('OKX_PASSPHRASE', '')
BASE_URL = "https://www.okx.com"
PROXY = os.getenv('PROXY_URL', '')

# 交易对 & 合约规格
PAIRS = {
    'ETH': {'swap': 'ETH-USDT-SWAP', 'ctVal': 0.1, 'lotSz': 0.01, 'maxLev': 100, 'lev': 2, 'cat': 'major'},
    'SOL': {'swap': 'SOL-USDT-SWAP', 'ctVal': 1, 'lotSz': 0.01, 'maxLev': 50, 'lev': 1.5, 'cat': 'major'},
    'ARB': {'swap': 'ARB-USDT-SWAP', 'ctVal': 10, 'lotSz': 0.1, 'maxLev': 50, 'lev': 1, 'cat': 'alt'},
    'SUI': {'swap': 'SUI-USDT-SWAP', 'ctVal': 1, 'lotSz': 1, 'maxLev': 50, 'lev': 1, 'cat': 'alt'},
}

SL_PCT = float(os.getenv('STOP_LOSS_PCT', 5)) / 100  # 止损5%
TAKE_PROFIT_RSI = 60  # RSI到60止盈
MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', 2))
MAX_DRAWDOWN = float(os.getenv('MAX_DRAWDOWN_PCT', 10)) / 100  # 总回撤10%暂停

def okx_req(method, path, body=''):
    ts = datetime.datetime.utcnow().isoformat()[:-3] + 'Z'
    msg = ts + method + path + body
    mac = hmac.new(SECRET_KEY.encode(), msg.encode(), hashlib.sha256).digest()
    sign = base64.b64encode(mac).decode()
    headers = ['-H', f'OK-ACCESS-KEY: {API_KEY}', '-H', f'OK-ACCESS-SIGN: {sign}',
               '-H', f'OK-ACCESS-TIMESTAMP: {ts}', '-H', f'OK-ACCESS-PASSPHRASE: {PASSPHRASE}',
               '-H', 'Content-Type: application/json']
    proxy_args = ['--proxy', PROXY] if PROXY else []
    if method == 'GET':
        r = subprocess.run(['curl','-s','--max-time','10'] + proxy_args + headers + [BASE_URL+path],
                          capture_output=True,text=True,timeout=15)
    else:
        r = subprocess.run(['curl','-s','--max-time','10','-X','POST'] + proxy_args + headers + ['-d', body, BASE_URL+path],
                          capture_output=True,text=True,timeout=15)
    try: return json.loads(r.stdout)
    except: return {'error': r.stdout[:200]}

def get_balance():
    bal = okx_req('GET', '/api/v5/account/balance')
    if bal.get('code') == '0':
        for acct in bal['data']:
            for det in acct.get('details', []):
                if det['ccy'] == 'USDT':
                    return float(det['eq']), float(det.get('availBal',0)), float(det.get('frozenBal',0))
    return 0, 0, 0

def get_positions():
    pos = okx_req('GET', '/api/v5/account/positions')
    if pos.get('code') != '0': return []
    result = []
    for p in pos['data']:
        sz = float(p['pos'])
        if sz > 0:
            result.append({
                'inst': p['instId'], 'side': p['posSide'], 'size': sz,
                'entry': float(p['avgPx']), 'mark': float(p['markPx']),
                'upl': float(p['upl']), 'margin': float(p['margin']),
                'liq': float(p.get('liqPx', 0)), 'lever': int(p['lever']),
            })
    return result

def set_leverage(inst, lever, mgnMode='isolated'):
    body = json.dumps({"instId": inst, "lever": str(lever), "mgnMode": mgnMode})
    return okx_req('POST', '/api/v5/account/set-leverage', body)

def place_order(inst, side, pos_side, sz, ord_type='market', reduce=False):
    body = {"instId": inst, "tdMode": "isolated", "side": side,
            "posSide": pos_side, "ordType": ord_type, "sz": str(sz)}
    if reduce: body["reduceOnly"] = "true"
    return okx_req('POST', '/api/v5/trade/order', json.dumps(body))

def close_position(inst, pos_side, sz):
    side = 'sell' if pos_side == 'long' else 'buy'
    close_side = 'short' if pos_side == 'long' else 'long'
    return place_order(inst, side, close_side, sz, reduce=True)

# ===== 市场分析 =====
def calc_rsi(prices, n=14):
    if len(prices) < n+1: return 50
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

def get_market_data(symbol, timeframe='day'):
    if timeframe == 'day':
        url = f'https://min-api.cryptocompare.com/data/v2/histoday?fsym={symbol}&tsym=USD&limit=30'
    else:
        url = f'https://min-api.cryptocompare.com/data/v2/histohour?fsym={symbol}&tsym=USD&limit=120'
    r = subprocess.run(['curl','-s','--max-time','8', url], capture_output=True,text=True,timeout=10)
    try:
        d=json.loads(r.stdout)
        vals=[x for x in d['Data']['Data'] if x['close']>0]
        if len(vals)<14: return None
        c=[x['close'] for x in vals]
        vol=[x['volumefrom'] for x in vals]
        return {'close':c,'vol':vol,'price':c[-1], 'high': [x['high'] for x in vals], 'low': [x['low'] for x in vals]}
    except: return None

def analyze_signal(symbol):
    day_data = get_market_data(symbol, 'day')
    if not day_data: return None
    hour_data = get_market_data(symbol, 'hour')
    if not hour_data: return None
    c_day, v_day = day_data['close'], day_data['vol']
    c_hour, v_hour = hour_data['close'], hour_data['vol']
    rsi_day = calc_rsi(c_day)
    rsi_hour = calc_rsi(c_hour)
    
    def macd_vals(c):
        def ema(d,n): rr=[sum(d[:n])/n]*n; [rr.append(d[i]*2/(n+1)+rr[-1]*(n-1)/(n+1)) for i in range(n,len(d))]; return rr
        e12,e26=ema(c,12),ema(c,26)
        dif=[e12[i]-e26[i] for i in range(len(c))]
        dea=[sum(dif[:9])/9]*9
        for i in range(9,len(dif)): dea.append(dif[i]*2/10+dea[-1]*8/10)
        return [dif[i]-dea[i] for i in range(len(dif))], dif[-1]-dea[-1]
    hist_day, _ = macd_vals(c_day)
    v5=sum(v_day[-5:])/5
    v10=sum(v_day[-10:-5])/5 if len(v_day)>=10 else v5
    vr=v5/v10*100 if v10>0 else 100
    chg7=(c_day[-1]-c_day[-7])/c_day[-7]*100 if len(c_day)>=7 else 0
    signal = {'rsi': rsi_day, 'rsi_4h': rsi_hour, 'hist': hist_day[-1], 'vol_ratio': vr, 'chg7': chg7, 'price': c_day[-1]}
    macd_short = False
    if len(hist_day) >= 4:
        macd_short = all(abs(hist_day[-i]) < abs(hist_day[-i-1]) for i in range(1,4))
    day_long = (rsi_day <= 33 or (rsi_day <= 35 and macd_short))
    hour_long = rsi_hour <= 32 and vr < 90
    long_ok = day_long and (hour_long or vr < 75)
    day_short = rsi_day >= 67 or (rsi_day >= 60 and macd_short and vr < 85)
    hour_short = rsi_hour >= 65
    short_ok = day_short and hour_short
    signal['long'] = long_ok
    signal['short'] = short_ok
    return signal

def calc_position_size(avail_balance, price, pair_info):
    margin = avail_balance * float(os.getenv('PER_TRADE_RISK_PCT', 2)) / 100
    lev = pair_info['lev']
    notional = margin * lev
    ct_val = pair_info['ctVal']
    lot_sz = pair_info['lotSz']
    contracts = notional / (ct_val * price)
    contracts = max(lot_sz, round(contracts / lot_sz) * lot_sz)
    return contracts

def run():
    now = datetime.datetime.now().strftime('%m-%d %H:%M')
    print(f'===== 🤖 AutoTrader [{now}] =====')
    total, avail, frozen = get_balance()
    print(f'Account: ${total:.2f} total | ${avail:.2f} avail | ${frozen:.2f} frozen')
    positions = get_positions()
    pos_symbols = [p['inst'].replace('-USDT-SWAP','') for p in positions]
    print(f'Open positions: {len(positions)}')
    for p in positions:
        pnl_pct = p['upl']/p['margin']*100 if p['margin']>0 else 0
        print(f'  {p["inst"]} {p["side"]} x{p["lever"]} PnL{p["upl"]:+.2f}({pnl_pct:+.1f}%) Liq@{p["liq"]}')
    actions = []
    for p in positions:
        if p['margin'] <= 0: continue
        loss_pct = p['upl'] / p['margin']
        if loss_pct <= -SL_PCT:
            print(f'⚠️ SL triggered! {p["inst"]} loss {loss_pct*100:.1f}%')
            r = close_position(p['inst'], p['side'], p['size'])
            if r.get('code') == '0':
                actions.append(f'🛑 Stop-loss {p["inst"]} ${p["upl"]:.2f}')
            else: print(f'  ❌ Close failed: {r}')
    if positions:
        for p in positions:
            sym = p['inst'].replace('-USDT-SWAP','')
            data = get_market_data(sym)
            if data:
                rsi = calc_rsi(data['close'])
                if rsi >= TAKE_PROFIT_RSI and p['upl'] > 0:
                    print(f'💰 TP triggered! {p["inst"]} RSI{rsi:.0f} +${p["upl"]:.2f}')
                    r = close_position(p['inst'], p['side'], p['size'])
                    if r.get('code') == '0':
                        actions.append(f'💰 Take-profit {p["inst"]} +${p["upl"]:.2f}')
    positions = get_positions()
    if len(positions) < MAX_POSITIONS:
        for sym, info in PAIRS.items():
            if sym in [x['inst'].replace('-USDT-SWAP','') for x in positions]: continue
            signal = analyze_signal(sym)
            if not signal: continue
            print(f'\n{sym}: DailyRSI{signal["rsi"]:.0f} 4hRSI{signal["rsi_4h"]:.0f} MACD{signal["hist"]:+.4f} Vol{signal["vol_ratio"]:.0f}%')
            if signal['long']:
                sz = calc_position_size(avail, signal['price'], info)
                if sz <= 0: continue
                set_leverage(info['swap'], info['lev'])
                r = place_order(info['swap'], 'buy', 'long', sz)
                if r.get('code') == '0':
                    actions.append(f'📈 Long {sym} {sz} @${signal["price"]:.4f} x{info["lev"]}')
                else: print(f'  ❌ Long failed: {r.get("msg","")}')
            elif signal['short']:
                sz = calc_position_size(avail, signal['price'], info)
                if sz <= 0: continue
                set_leverage(info['swap'], info['lev'])
                r = place_order(info['swap'], 'sell', 'short', sz)
                if r.get('code') == '0':
                    actions.append(f'📉 Short {sym} {sz} @${signal["price"]:.4f} x{info["lev"]}')
                else: print(f'  ❌ Short failed: {r.get("msg","")}')
    print()
    if actions:
        print('📋 Actions:')
        for a in actions: print(f'  • {a}')
    else:
        print('📋 No action — waiting for signals')
    print(f'\n--- Scan complete ---')

if __name__ == '__main__':
    run()
