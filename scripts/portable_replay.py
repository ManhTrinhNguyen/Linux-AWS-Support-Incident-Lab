"""Local automated replay, NOT validation of Docker, Nginx, systemd or AWS.
Requires Linux /dev/full; permissions must be enforced for the executing user.
Uses a Python proxy instead of Nginx and a /dev/full symlink for storage errors.
"""
import http.client
import importlib.util
import json
from pathlib import Path
import socket
import tempfile
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lab_server', ROOT / 'app/server.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Proxy(BaseHTTPRequestHandler):
    target = None
    def dispatch(self):
        conn = http.client.HTTPConnection('127.0.0.1', self.target, timeout=0.7)
        try:
            conn.request(self.command, self.path)
            res = conn.getresponse()
            body, status = res.read(), res.status
        except (TimeoutError, socket.timeout):
            body, status = b'portable proxy: upstream timeout', 504
        except (ConnectionError, OSError):
            body, status = b'portable proxy: upstream connection failed', 502
        finally:
            conn.close()
        self.send_response(status)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    do_GET = dispatch
    do_POST = dispatch

class Running:
    def __init__(self, handler, port=0):
        self.server = ThreadingHTTPServer(('127.0.0.1', port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port
    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

def request(port, path='/', method='GET'):
    start = time.monotonic()
    try:
        res = urlopen(Request(f'http://127.0.0.1:{port}{path}', method=method), timeout=8)
    except HTTPError as e:
        res = e
    with res:
        status, body = res.status, res.read().decode()
    return {'status': status, 'body': body, 'elapsed_seconds': round(time.monotonic()-start,3)}

def main():
    if not Path('/dev/full').exists():
        raise RuntimeError('This replay requires Linux /dev/full.')
    evidence = ROOT / 'evidence' / 'automated-replay'
    evidence.mkdir(exist_ok=True)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='support-replay-') as tmp:
        app.DATA=Path(tmp)/'data'; app.DATA.mkdir()
        app.CONTROL=Path(tmp)/'control'; app.CONTROL.mkdir()
        backend=Running(app.Handler)
        Proxy.target=backend.port
        proxy=Running(Proxy)
        def healthy():
            checks=[request(proxy.port,'/health'), request(proxy.port,'/notes','POST'),request(proxy.port)]
            assert [r['status'] for r in checks]==[200,201,200],checks
            return checks
        healthy()
        def record(key, injection, before, failed, recovery, after):
            row={'scenario':key,'executed_at_utc':datetime.now(timezone.utc).isoformat(),
                 'execution':'Automated assistant execution; portable Python proxy, not Nginx/Docker',
                 'injection':injection,'before':before,'failure':failed,'recovery':recovery,'after':after}
            (evidence/f'{key}.json').write_text(json.dumps(row,indent=2)+'\n')
            rows.append(row)
            print('PASS portable scenario:',key)
        try:
            before=healthy()
            original_port=backend.port
            backend.close()
            failed=request(proxy.port)
            assert failed['status']==502,failed
            backend=Running(app.Handler,original_port)
            record('stopped-backend','Stop the actual local application HTTP server.',before,failed,
                   'Restart the local server on its original port.',healthy())

            before=healthy()
            # Reserve a socket without listening; it reliably rejects TCP connections.
            with socket.socket() as unused:
                unused.bind(('127.0.0.1',0))
                Proxy.target=unused.getsockname()[1]
                failed=request(proxy.port)
                assert failed['status']==502,failed
            Proxy.target=backend.port
            record('wrong-port','Point Python proxy at a bound, non-listening port.',before,failed,
                   'Restore the proxy target to the actual backend listener.',healthy())

            before=healthy()
            (app.DATA/"notes.txt").unlink(missing_ok=True)
            app.DATA.chmod(0o500)
            try:
                failed=request(proxy.port,'/notes','POST')
                assert failed['status']==500 and 'write_failed' in failed['body'],failed
            finally:
                app.DATA.chmod(0o700)
            record('permissions','Set actual local data-directory mode to 0500.',before,failed,
                   'Restore owner write permission with mode 0700.',healthy())

            before=healthy()
            (app.DATA/'notes.txt').unlink()
            (app.DATA/'notes.txt').symlink_to('/dev/full')
            try:
                failed=request(proxy.port,'/notes','POST')
                assert failed['status']==500 and 'storage_full' in failed['body'],failed
            finally:
                (app.DATA/'notes.txt').unlink()
            record('storage-error','Redirect note writes to Linux /dev/full, which returns real ENOSPC. No filesystem was filled.',
                   before,failed,'Remove the device symlink and allow a regular note file to be created.',healthy())

            before=healthy()
            (app.CONTROL/'slow').touch()
            try:
                failed=request(proxy.port)
                assert failed['status']==504,failed
                assert request(proxy.port,'/health')['status']==200
            finally:
                (app.CONTROL/'slow').unlink()
            record('timeout','Actual five-second handler delay exceeds Python proxy timeout of 0.7 seconds.',
                   before,failed,'Remove the delay marker; repeat all application checks.',healthy())
            # Let the original delayed request finish before temporary directories disappear.
            time.sleep(5)
        finally:
            proxy.close(); backend.close()
    (evidence/'summary.json').write_text(json.dumps({'completed':len(rows),'scope':'Portable replay only','results':rows},indent=2)+'\n')
    print('All 5 portable scenarios reproduced and recovered.')

if __name__=='__main__':
    main()
