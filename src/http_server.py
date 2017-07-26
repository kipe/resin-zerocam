import os
import io
import json
import picamera
import logging
import socketserver
from datetime import datetime
from threading import Condition
from http import server

PAGE = '''\
<html>
<head>
<title>RPi Zero W with FishEye Zerocam</title>
</head>
<body>
<h1>RPi Zero W with FishEye Zerocam</h1>
<img src="stream.mjpg" width="%s" height="%s" />
</body>
</html>
'''.format(*os.environ.get('RESOLUTION', '640x480').split('x'))


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            content = PAGE
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        elif self.path == '/index.html':
            self.send_response(301)
            self.send_header('Location', '/')
            self.end_headers()
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/api/capture':
            content = json.dumps(os.listdir('/data/capture'))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/capture':
            if not os.path.exists('/data/capture'):
                os.makedirs('/data/capture')

            filename = '%s.jpg' % (datetime.utcnow().isoformat())

            self.server.camera.capture('/data/capture/%s' % (filename), use_video_port=True)
            content = '{"status": "ok", "filename": "%s"}' % (filename)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, handler, camera):
        self.camera = camera
        super(StreamingServer, self).__init__(address, handler)


with picamera.PiCamera(resolution='%s' % os.environ.get('RESOLUTION', '640x480'), framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 80)
        server = StreamingServer(address, StreamingHandler, camera)
        server.serve_forever()
    finally:
        camera.stop_recording()
