"""Run from the repository root: python3 tests/donate.py (requires Node.js)."""
from pathlib import Path
import re
import subprocess

html = Path('donate.html').read_text()
address = '0xF68639DA4C0a0670ee3712F0ae46b2C03C59aDCc'
assert re.findall(r'0x[0-9a-fA-F]{40}', html) == [address]
assert 'href="/donate"' in Path('index.html').read_text()
assert 'BNB Smart Chain, Ethereum, Base' in html
assert 'Send only on the listed networks.' in html
script = re.search(r'<script>(.*?)</script>', html, re.S)[1]
subprocess.run(['node', '-e', '''
const assert = require('node:assert/strict');
let click;
const status = {textContent: ''};
global.document = {getElementById: id => ({
  'copy-address': {addEventListener: (_, fn) => click = fn},
  'wallet-address': {textContent: ADDRESS}, 'copy-status': status
})[id]};
Object.defineProperty(global, 'navigator', {value: {clipboard: {
  writeText: async value => assert.equal(value, ADDRESS)
}}, configurable: true});
SCRIPT
(async () => {
  await click();
  assert.equal(status.textContent, 'Address copied.');
  navigator.clipboard.writeText = async () => {throw Error('denied')};
  await click();
  assert.equal(status.textContent, 'Could not copy. Select and copy the address above.');
  delete navigator.clipboard;
  await click();
  assert.equal(status.textContent, 'Could not copy. Select and copy the address above.');
})().catch(error => {console.error(error); process.exitCode = 1});
'''.replace('ADDRESS', repr(address)).replace('SCRIPT', script)], check=True)
print('Donation values and clipboard success/failure: OK')
