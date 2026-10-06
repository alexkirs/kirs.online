"""Run from the repository root: python3 tests/donate.py (requires Node.js)."""
from pathlib import Path
import re
import hashlib
import subprocess

css_version = hashlib.sha256(Path('style.css').read_bytes()).hexdigest()[:12]
for page in Path('.').rglob('*.html'):
    content = page.read_text()
    assert f'href="/style.css?v={css_version}"' in content, page
    for svg, body in re.findall(r'(<svg\b[^>]*>)(.*?)</svg>', content, re.S):
        size = '20' if 'class="copy-glyph"' in body else '24'
        assert f'width="{size}"' in svg and f'height="{size}"' in svg, page
assert '.donation-qr { color-scheme: light;' in Path('style.css').read_text()
html = Path('donate.html').read_text()
assert 'href="https://web.tribute.tg/d/RJ1"' in html
assert 'href="https://t.me/tribute/app?startapp=dRJ1"' in html
assert re.findall(r'href="([^"]+)"', html) == [f'/style.css?v={css_version}', '/', 'https://web.tribute.tg/d/RJ1', 'https://t.me/tribute/app?startapp=dRJ1']
assert 'Pay by card · Tribute' in html
assert '<h2 id="tribute-heading">' in html
assert 'Card · any country</h2>' in html
assert '<p>Visa, Mastercard, Mir via Tribute</p>' in html
assert '<details>' not in html
assert html.count('class="donation-icon"') == 6
assert html.count('aria-hidden="true"') == 10
assert html.count('class="copy-button"') == 4
assert html.count('aria-live="polite"') == 4
assert 'Copy address</button>' not in html and 'Copy ID</button>' not in html
assert html.count('class="copy-glyph"') == html.count('class="check-glyph"') == 4
assert 'class="donation-quick"' in html
assert html.count('class="donation-qr"') == 3
assert html.index('id="tribute-heading"') < html.index('id="binance-heading"') < html.index('id="tron-heading"')
binance = '18813173'
assert html.count(binance) == 1
assert 'Binance · send to Binance ID' in html
assert 'bybit' not in html.lower()
assert 'In Binance app: Pay &gt; Send, enter this ID, zero fee' in html
assert 'aria-label="Copy Binance ID"' in html
address = '0xF68639DA4C0a0670ee3712F0ae46b2C03C59aDCc'
assert re.findall(r'0x[0-9a-fA-F]{40}', html) == [address]
assert 'href="/donate"' in Path('index.html').read_text()
assert 'USDT / BNB / ETH · BNB Chain, Ethereum, Base</h2>' in html
assert 'Send only' not in html
tron = 'TL3Jom82eDp4yJewcuWN4njWvSFW7VBP7M'
assert html.count(tron) == 1
ton = 'UQCoCOniO8A7STZAnFp4WK463i05NxNTrc3ulmtvtkeUKNiM'
assert html.count(ton) == 1
assert html.index(tron) < html.index(ton) < html.index(address)
assert 'TON / USDT · TON network' in html
assert 'src="/donate-ton-qr.png"' in html
assert 'USDT · Tron (TRC20)' in html
assert 'src="/donate-tron-qr.png"' in html
script = re.search(r'<script>(.*?)</script>', html, re.S)[1]
subprocess.run(['node', '-e', '''
const assert = require('node:assert/strict');
let timeout;
global.setTimeout = fn => {timeout = fn; return 1};
global.clearTimeout = () => {timeout = undefined};
const sections = [BINANCE, TRON, TON, ADDRESS].map(address => {
  const section = {address, status: {textContent: ''}};
  section.classes = new Set();
  section.querySelector = selector => ({
    'button': {classList: {add: name => section.classes.add(name), remove: name => section.classes.delete(name)}, addEventListener: (_, fn) => section.click = fn},
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
  for (const {click, status, address, classes} of sections) {
    navigator.clipboard = {writeText: async value => assert.equal(value, address)};
    await click();
    assert.equal(status.textContent, 'Copied.');
    assert(classes.has('copied'));
    timeout();
    assert(!classes.has('copied'));
    assert.equal(status.textContent, '');
    navigator.clipboard.writeText = async () => {throw Error('denied')};
    await click();
    assert.equal(status.textContent, 'Could not copy. Select the value to copy.');
    delete navigator.clipboard;
    await click();
    assert.equal(status.textContent, 'Could not copy. Select the value to copy.');
  }
})().catch(error => {console.error(error); process.exitCode = 1});
'''.replace('BINANCE', repr(binance)).replace('ADDRESS', repr(address)).replace('TRON', repr(tron)).replace('TON', repr(ton)).replace('SCRIPT', script)], check=True)
print('Donation values and clipboard success/failure: OK')
