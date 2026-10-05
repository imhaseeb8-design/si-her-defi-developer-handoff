"""Package the static routes in a Worker so ICS receives calendar MIME headers."""
import base64
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
dist = root / 'dist'
email = re.sub(r'>\s+<', '><', (root/'newsletter.html').read_text())
(root/'newsletter.html').write_text(email)
(dist/'newsletter').mkdir(exist_ok=True)
(dist/'newsletter/index.html').write_text(email)
files = {}
for path in sorted(dist.rglob('*')):
    if not path.is_file() or path.name == '_headers' or 'server' in path.relative_to(dist).parts:
        continue
    key = '/' + str(path.relative_to(dist))
    content_type = {'.html':'text/html; charset=utf-8','.ics':'text/calendar; charset=utf-8','.png':'image/png'}.get(path.suffix,'application/octet-stream')
    files[key] = [content_type, base64.b64encode(path.read_bytes()).decode()]
worker = '''const files = __FILES__;
export default { async fetch(request) {
  if (!['GET','HEAD'].includes(request.method)) return new Response('Method not allowed',{status:405});
  const path = new URL(request.url).pathname;
  let key = path.endsWith('/') ? path + 'index.html' : path;
  if (!files[key] && files[key + '/index.html']) return Response.redirect(new URL(path + '/', request.url), 308);
  const entry = files[key];
  if (!entry) return new Response('Not found', {status:404});
  const headers = {'Content-Type':entry[0], 'X-Content-Type-Options':'nosniff'};
  if (key.endsWith('.ics')) {headers['Content-Disposition']='attachment; filename="'+key.split('/').pop()+'"'; headers['Cache-Control']='no-store';}
  const bytes = Uint8Array.from(atob(entry[1]), c => c.charCodeAt(0));
  return new Response(request.method === 'HEAD' ? null : bytes, {headers});
}};
'''.replace('__FILES__', json.dumps(files))
(dist/'server').mkdir(exist_ok=True)
(dist/'server/index.js').write_text(worker)
print(json.dumps({'routes':len(files),'email_bytes':len(email.encode()),'worker_bytes':len(worker.encode())}))
