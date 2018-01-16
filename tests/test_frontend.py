import unittest

from app import app


class FrontEndpointTest(unittest.TestCase):

    def _check_bookmark_structure(self, res):
        self.assertEqual(res.status, 200)
        for r in res.json['bookmarks']:
            self.assertIsInstance(r, dict)
            self.assertIn('_id', r)
            self.assertIn('date_create', r)
            self.assertIsInstance(r['_id'], str)
            self.assertIsInstance(r['date_create'], int)

    def test_unsort_bookmarks(self):
        request, response = app.test_client.get('/rutor/bookmarks/unsort.json')
        self._check_bookmark_structure(response)

    def test_trash_bookmarks(self):
        request, response = app.test_client.get('/rutor/bookmarks/trash.json')
        self._check_bookmark_structure(response)

    def test_favorite_bookmarks(self):
        request, response = app.test_client.get('/rutor/bookmarks/favorite.json')
        self._check_bookmark_structure(response)


if __name__ == '__main__':
    unittest.main()
