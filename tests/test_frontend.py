import unittest

from app import app


class FrontEndpointTest(unittest.TestCase):

    def _check_bookmark_structure(self, res):
        self.assertEqual(res.status, 200)
        for r in res.json['bookmarks']:
            self.assertIsInstance(r, dict)
            self.assertIn('_id', r)
            self.assertIsInstance(r['_id'], str)

    def test_bookmark_torrents(self):
        request, response = app.test_client.get('/torrents/%D0%92%D0%BE%D0%BB%D1%87%D1%8C%D1%8F%20%D1%8F%D0%BC%D0%B0%20(2005)')
        self.assertEqual(response.status, 200)
        for r in response.json['torrents']:
            self.assertIsInstance(r, dict)
            self.assertIn('_id', r)
            self.assertIn('title', r)
            self.assertIn('link', r)
            self.assertIn('tor_link', r)
            self.assertIn('size_gb', r)
            self.assertIsInstance(r['_id'], int)
            self.assertIsInstance(r['size_gb'], float)

    def test_unsort_bookmarks(self):
        request, response = app.test_client.get('/bookmarks/unsort.json?limit=10')
        self._check_bookmark_structure(response)

    def test_trash_bookmarks(self):
        request, response = app.test_client.get('/bookmarks/trash.json?limit=10')
        self._check_bookmark_structure(response)

    def test_favorite_bookmarks(self):
        request, response = app.test_client.get('/bookmarks/favorite.json?limit=10')
        self._check_bookmark_structure(response)

    def test_stat(self):
        request, response = app.test_client.get('/stat.json')
        self.assertEqual(response.status, 200)
        self.assertIsInstance(response.json, dict)
        self.assertIn('stat', response.json)
        self.assertIsInstance(response.json['stat'], dict)
        self.assertIn('last_update', response.json['stat'])
        self.assertIn('total_bookmarks', response.json['stat'])
        self.assertIn('total_torrents', response.json['stat'])
        self.assertIn('last_bookmark', response.json['stat'])
        self.assertIn('last_torrent', response.json['stat'])


if __name__ == '__main__':
    unittest.main()
