"""Regression checks for corrupt metadata and preview request routing."""
import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from catalog import validate_catalog
from serve import Handler

ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / 'data/videos.json').read_text())

    def reject(self, field, value):
        self.catalog['videos'][0][field] = value
        with self.assertRaises(ValueError):
            validate_catalog(self.catalog)

    def test_current_catalog(self):
        self.assertEqual(len(validate_catalog(self.catalog)), len(self.catalog['videos']))

    def test_duplicate_video(self):
        self.catalog['videos'].append(copy.deepcopy(self.catalog['videos'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate_catalog(self.catalog)

    def test_duration_mismatch(self): self.reject('duration', 'PT1S')
    def test_empty_duration(self): self.reject('duration', 'PT')
    def test_negative_views(self): self.reject('views', -1)
    def test_missing_timezone(self): self.reject('uploadDate', '2026-11-22T10:00:00')
    def test_wrong_image_identity(self): self.reject('thumbnail', 'assets/thumbs/another-640.webp')
    def test_empty_summary(self): self.reject('summary', '  ')
    def test_unknown_channel(self): self.reject('channel', 'unknown')


class PreviewRoutingTests(unittest.TestCase):
    def handler(self, path, command='GET'):
        handler = Handler.__new__(Handler)
        handler.path = path
        handler.command = command
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = io.BytesIO()
        return handler

    def test_head_uses_same_project_path_as_get(self):
        handler = self.handler('/darkecho/watch/example.html?v=1', 'HEAD')
        with patch('http.server.SimpleHTTPRequestHandler.do_HEAD') as head:
            handler.do_HEAD()
        head.assert_called_once()
        self.assertEqual(handler.path, '/watch/example.html?v=1')

    def test_get_uses_project_path(self):
        handler = self.handler('/darkecho/index.html')
        with patch('http.server.SimpleHTTPRequestHandler.do_GET') as get:
            handler.do_GET()
        get.assert_called_once()
        self.assertEqual(handler.path, '/index.html')

    def test_missing_page_head_has_no_body(self):
        handler = self.handler('/missing', 'HEAD')
        handler.send_error(404)
        handler.send_response.assert_called_with(404)
        self.assertEqual(handler.wfile.getvalue(), b'')

    def test_missing_page_get_has_custom_body(self):
        handler = self.handler('/missing')
        handler.send_error(404)
        self.assertEqual(handler.wfile.getvalue(), (ROOT / '404.html').read_bytes())

    def test_slash_redirect(self):
        handler = self.handler('/darkecho')
        handler.do_GET()
        handler.send_header.assert_called_with('Location', '/darkecho/')


if __name__ == '__main__': unittest.main()
