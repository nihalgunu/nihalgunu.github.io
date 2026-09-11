"""Switch the homepage intro to another fold model (edits index.html, no commit).

Usage: python3 intro-src/install.py <model>   e.g. python3 intro-src/install.py crane

Replaces the fold JSON embedded in index.html's intro overlay with
intro-src/<model>.json. The runtime (intro.js), the intro styles and the
photos are already installed and are left alone.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent

model = sys.argv[1]
data = (HERE / f'{model}.json').read_text()

index = SITE / 'index.html'
html = index.read_text()
html, n = re.subn(r'(<script type="application/json" id="fold-data">).*?(</script>)',
                  lambda m: m.group(1) + data + m.group(2), html, count=1, flags=re.S)
assert n == 1, 'fold-data block not found in index.html'
index.write_text(html)
print('installed', model, 'into', index)
