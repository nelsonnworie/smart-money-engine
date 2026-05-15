from scripts.fetcher import get_token_price, parse_transaction

print('=== PRICE FILTER ===')
for t in ['4CHAN','CHUD','DTOKEN','BAD']:
    p = get_token_price(t)
    print(f'${t}: price={p} -> {"DROPPED" if p == 0 else "KEPT"}')

print()
for t in ['PEPE','SHIB','ETH','USDT']:
    p = get_token_price(t)
    print(f'${t}: price={p}')

print()
print('=== AMOUNT FILTER ===')
bad_tx = {'tokenSymbol':'4CHAN','tokenDecimal':'9','value':'1000000000000000000000','hash':'0xabc','from':'0xaaa','to':'0xbbb','timeStamp':'1700000000'}
result = parse_transaction(bad_tx)
print(f'4CHAN quadrillion tx: {"DROPPED" if result is None else "BUG still passing: " + str(result)}')

pepe_raw = int(2_000_000 / 0.0000142 * (10**18))
good_tx = {'tokenSymbol':'PEPE','tokenDecimal':'18','value':str(pepe_raw),'hash':'0xdef','from':'0xccc','to':'0xddd','timeStamp':'1700000001'}
result = parse_transaction(good_tx)
print(f'PEPE $2M tx: {"KEPT at $" + str(result["amount_usd"]) if result else "DROPPED (bug)"}')