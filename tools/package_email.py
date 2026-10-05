"""Package the current generated MJML and its referenced PNG assets for Loops."""
import argparse
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset-origin', required=True)
    args = parser.parse_args()
    prefix = args.asset_origin.rstrip('/') + '/assets/'
    mjml = (ROOT / 'email/newsletter.mjml').read_text()
    references = re.findall(r'\bsrc="([^"]+)"', mjml)
    names = sorted({url.removeprefix(prefix) for url in references})
    if not references or any(not url.startswith(prefix) for url in references):
        raise ValueError('Every email image must use the configured asset origin')
    inventory = []
    for name in names:
        if Path(name).name != name or not name.endswith('.png'):
            raise ValueError('Unexpected image path: ' + name)
        raw = (ROOT / 'assets' / name).read_bytes()
        if raw[:8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError('Expected PNG: ' + name)
        width, height = struct.unpack('>II', raw[16:24])
        inventory.append({'path': 'assets/' + name, 'width': width, 'height': height,
                          'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    output = ROOT / 'email/loops-upload.zip'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('index.mjml', mjml.replace(prefix, 'assets/'))
        for asset in inventory:
            archive.write(ROOT / asset['path'], asset['path'])
    (ROOT / 'email/asset-manifest.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print(json.dumps({'zip': str(output), 'images': len(inventory),
                      'links': len(re.findall(r'\bhref="', mjml))}))


if __name__ == '__main__':
    main()
