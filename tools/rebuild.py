"""Rebuild the handed-off source and refresh website/email delivery artifacts."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ORIGIN = 'https://si-her-defi-calendar-test.imhaseeb8.chatgpt.site'


def run(args):
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default=DEFAULT_ORIGIN)
    args = parser.parse_args()
    origin = args.base_url.rstrip('/')
    parsed = urlsplit(origin)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.path or parsed.query or parsed.fragment):
        parser.error('--base-url must be an HTTPS origin without a path or credentials')
    compiler = ROOT / 'node_modules/mjml/bin/mjml'
    if not compiler.exists():
        parser.error('MJML is not installed; run npm ci first')
    run([sys.executable, 'build.py', '--base-url', origin])
    # Preserve the original generator; override its origin only for an explicit migration.
    sys.path.insert(0, str(ROOT))
    import newsletter
    newsletter.ORIGIN = origin
    newsletter.build()
    run(['node', str(compiler), '--config.validationLevel=strict', '-r',
         'newsletter.mjml', '-o', 'newsletter.html'])
    run([sys.executable, 'package_site.py'])
    (ROOT / 'email').mkdir(exist_ok=True)
    for name in ('newsletter.mjml', 'newsletter.html'):
        shutil.copy2(ROOT / name, ROOT / 'email' / name)
    run([sys.executable, 'tools/package_email.py', '--asset-origin', origin])


if __name__ == '__main__':
    main()
