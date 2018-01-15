import unittest
import os

import lxml.html

from parser import parse, TorrentItem, RUTOR_HOST, torrent_size_to_gbytes

SOURCE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_pages'))


def _get_source(filename: str) -> str:
    with open(os.path.join(SOURCE_PATH, filename)) as f:
        return f.read()


class TorrentListParserTest(unittest.TestCase):
    def test_empty(self):
        data = ['', None]
        for d in data:
            self.assertIsNone(parse(d))

        self.assertEqual([], parse('<!doctype html> sd sd </sdsd  </sdsd> <sss'))

    def test_smoke(self):
        import logging
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
        res = parse(_get_source('torrents_list.html'))

        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 100)
        for row in res:
            self.assertIsInstance(row, TorrentItem)
            self.assertTrue(row.success,)


class TorrentItemParserTest(unittest.TestCase):
    def test_smoke(self):
        row_html = """<tr class="gai">
            <td>12&nbsp;Янв&nbsp;18</td>
            <td colspan = "2">
                <a class="downgif" href="/download/607050">
                    <img src="/s/i/d.gif" alt="D" />
                </a>
                <a href="magnet:?xt=urn:btih:6d6d9b4428cfa4137c3d3217a8bc93a7524cbf2c&dn=rutor.info&tr=udp://opentor.org:2710&tr=udp://opentor.org:2710&tr=http://retracker.local/announce">
                    <img src="/s/i/m.png" alt="M" />
                </a>
                <a href="/torrent/607050/drevesnyj-demon_arbor-demon_enclosure-2016-web-dlrip-l">
                    Древесный демон / Arbor Demon / Enclosure (2016) WEB-DLRip | L
                </a>
            </td>
            <td align="right">
                1.37&nbsp;TB
            </td>
            <td align="center">
                <span class="green"><img src="/s/t/arrowup.gif" alt="S" />&nbsp;26</span>&nbsp;
                <img src="/s/t/arrowdown.gif" alt="L" /><span class="red">&nbsp;3</span>
            </td>
        </tr>"""

        item = TorrentItem(lxml.html.fromstring(row_html))
        self.assertTrue(item.success)
        self.assertEqual(item.id, 607050)
        self.assertEqual(item.link, '%s/torrent/607050' % RUTOR_HOST)
        self.assertEqual(item.tor_link, '%s/download/607050' % RUTOR_HOST)
        self.assertEqual(item.size, 1402.88)
        self.assertEqual(item.title, 'Древесный демон / Arbor Demon / Enclosure (2016) WEB-DLRip | L')
        self.assertEqual(item.bookmark_title, 'Древесный демон (2016)')

    def test_too_many_years(self):
        """Фантомас: Трилогия / Fantomas: Trilogy (1964-1967) BDRip 1080p | D"""
        row_html = """<tr class="gai">
                    <td>12&nbsp;Янв&nbsp;18</td>
                    <td colspan = "2">
                        <a class="downgif" href="/download/607050">
                            <img src="/s/i/d.gif" alt="D" />
                        </a>
                        <a href="magnet:?xt=urn:btih:6d6d9b4428cfa4137c3d3217a8bc93a7524cbf2c&dn=rutor.info&tr=udp://opentor.org:2710&tr=udp://opentor.org:2710&tr=http://retracker.local/announce">
                            <img src="/s/i/m.png" alt="M" />
                        </a>
                        <a href="/torrent/607050/drevesnyj-demon_arbor-demon_enclosure-2016-web-dlrip-l">
                            Фантомас: Трилогия / Fantomas: Trilogy (1964-1967) BDRip 1080p | D
                        </a>
                    </td>
                    <td align="right">
                        1.37&nbsp;TB
                    </td>
                    <td align="center">
                        <span class="green"><img src="/s/t/arrowup.gif" alt="S" />&nbsp;26</span>&nbsp;
                        <img src="/s/t/arrowdown.gif" alt="L" /><span class="red">&nbsp;3</span>
                    </td>
                </tr>"""

        item = TorrentItem(lxml.html.fromstring(row_html))
        self.assertTrue(item.success)
        self.assertEqual(item.title, 'Фантомас: Трилогия / Fantomas: Trilogy (1964-1967) BDRip 1080p | D')
        self.assertEqual(item.bookmark_title, 'Фантомас: Трилогия (1964-1967)')


class TorrentSizeDecodeTest(unittest.TestCase):
    def test_invalid_size(self):
        for i in ['1.08 GsdsdB', '', '0.00 KB']:
            try:
                torrent_size_to_gbytes(i)
            except Exception as e:
                exc = e
            else:
                exc = None
            self.assertIsInstance(exc, Exception)

    def test_gbytes_size(self):
        res = torrent_size_to_gbytes('1.08 GB')
        self.assertEqual(1.08, res)

    def test_tbytes_size(self):
        res = torrent_size_to_gbytes('1.113 TB')
        self.assertEqual(1.113 * 1024., res)

    def test_mbytes_size(self):
        res = torrent_size_to_gbytes('107.08 MB')
        self.assertEqual(107.08 / 1024., res)


class TorrentBookmarkTokenTest(unittest.TestCase):
    def test_basic(self):
        provider = [
            ('Древесный демон / Arbor Demon / Enclosure (2016) WEB-DLRip | L', 'Древесный демон (2016)'),
            ('Древесный демон / Enclosure (2016) sdsd| L', 'Древесный демон (2016)'),
            ('Древесный демон (2016) WEB-DLRip', 'Древесный демон (2016)'),
            ('Древесный демон / Arbor Demon / Enclosure (2016) WEB-DLRip | sdsd | sdsd', 'Древесный демон (2016)'),
        ]

        for test, expected in provider:
            res = TorrentItem.get_bookmark_title(test)
            self.assertEqual(res, expected)


if __name__ == '__main__':
    unittest.main()
