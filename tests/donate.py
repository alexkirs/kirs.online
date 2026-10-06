"""Run from the repository root: python3 tests/donate.py (requires Node.js)."""
from pathlib import Path
import re
import subprocess

html = Path('donate.html').read_text()
assert 'href="https://web.tribute.tg/d/RJ1"' in html
assert 'href="https://t.me/tribute/app?startapp=dRJ1"' in html
assert re.findall(r'href="([^"]+)"', html) == ['/style.css', '/', 'https://web.tribute.tg/d/RJ1', 'https://t.me/tribute/app?startapp=dRJ1']
assert 'Pay by card · Tribute' in html
assert '<details>' not in html
assert html.count('class="donation-qr"') == 3
assert html.index('id="tribute-heading"') < html.index('id="binance-heading"') < html.index('id="tron-heading"')
binance = '18813173'
assert html.count(binance) == 1
assert 'Binance · Pay / transfer to Binance ID' in html
assert 'In Binance app, Pay &gt; Send, enter this ID, zero fee.' in html
assert '<button type="button">Copy ID</button>' in html
address = '0xF68639DA4C0a0670ee3712F0ae46b2C03C59aDCc'
assert re.findall(r'0x[0-9a-fA-F]{40}', html) == [address]
assert 'href="/donate"' in Path('index.html').read_text()
assert 'BNB Smart Chain, Ethereum, Base' in html
assert 'Send only on the listed networks.' in html
tron = 'TL3Jom82eDp4yJewcuWN4njWvSFW7VBP7M'
assert html.count(tron) == 1
ton = 'UQCoCOniO8A7STZAnFp4WK463i05NxNTrc3ulmtvtkeUKNiM'
assert html.count(ton) == 1
assert html.index(tron) < html.index(ton) < html.index(address)
assert 'TON / USDT · TON network' in html
assert 'Send only on TON network.' in html
assert 'src="/donate-ton-qr.png"' in html
assert 'USDT · Tron (TRC20)' in html
assert 'Send only on Tron (TRC20).' in html
assert 'src="/donate-tron-qr.png"' in html
script = re.search(r'<script>(.*?)</script>', html, re.S)[1]
subprocess.run(['node', '-e', '''
const assert = require('node:assert/strict');
const sections = [BINANCE, TRON, TON, ADDRESS].map(address => {
  const section = {address, status: {textContent: ''}};
  section.querySelector = selector => ({
    'button': {addEventListener: (_, fn) => section.click = fn},
    '.wallet-address': {textContent: address}, '.copy-status': section.status
  })[selector];
  return section;
});
global.document = {querySelectorAll: selector => {
  assert.equal(selector, '.donation:has(.wallet-address)');
  return sections;
}};
Object.defineProperty(global, 'navigator', {value: {}, configurable: true});
SCRIPT
(async () => {
  for (const {click, status, address} of sections) {
    navigator.clipboard = {writeText: async value => assert.equal(value, address)};
    await click();
    assert.equal(status.textContent, 'Copied.');
    navigator.clipboard.writeText = async () => {throw Error('denied')};
    await click();
    assert.equal(status.textContent, 'Could not copy. Select and copy the value above.');
    delete navigator.clipboard;
    await click();
    assert.equal(status.textContent, 'Could not copy. Select and copy the value above.');
  }
})().catch(error => {console.error(error); process.exitCode = 1});
'''.replace('BINANCE', repr(binance)).replace('ADDRESS', repr(address)).replace('TRON', repr(tron)).replace('TON', repr(ton)).replace('SCRIPT', script)], check=True)
print('Donation values and clipboard success/failure: OK')
