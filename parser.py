#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

import time
import asyncio
import logging
from typing import Optional
import re

import aiohttp
import async_timeout
import lxml.html
from lxml.etree import ParserError


USER_AGENT = 'todo'
RUTOR_HOST = 'http://rus-tor.com'
URL = '%s/browse/%%d/1/0/0' % RUTOR_HOST
TIMEOUT = 25
CONCURRENCY = 1
PAGES_COUNT = 10
DEBUG = True

assert CONCURRENCY
assert PAGES_COUNT


def torrent_size_to_gbytes(size_str: str):
    value, metric = re.search('^(\d+(\.\d+)?)\s+((G|M|T)?B)$', size_str).group(1, 3)
    value = float(value)
    if metric == 'MB':
        return value / 1024.
    elif metric == 'GB':
        return value
    elif metric == 'TB':
        return value * 1024.
    else:
        raise Exception('not valid metric %s' % size_str)


class TorrentItem(object):
    success = True
    id = None
    link = None
    tor_link = None
    size = None
    title = None
    bookmark_title = None

    def __init__(self, row_elem: lxml.html.HtmlElement):
        """Русское название / Оригинальное название (Год выпуска) Качество видео | Качество перевода | Версия"""
        try:
            torent_link = row_elem.xpath('.//a[@class="downgif"]/@href')[0].strip()
            logging.debug('parse id debug "%s"', torent_link)
            self.id = int(re.findall("/download/([\d]+)", torent_link)[0])
            self.tor_link = RUTOR_HOST + torent_link
            self.link = '%s/torrent/%d' % (RUTOR_HOST, self.id)
        except Exception as e:
            logging.warning('parse id exception %s', e)
            self.success = False

        try:
            td = row_elem.xpath('.//td[last()-1]/text()')[0].strip()
            logging.debug('parse size debug "%s"', td)
            self.size = torrent_size_to_gbytes(td)
        except Exception as e:
            logging.warning('parse size exception %s', e)
            self.success = False

        try:
            title_text_full = row_elem.xpath('.//td[2]/a[3]/text()')[0].strip()
            logging.debug('parse title debug "%s"', title_text_full)
            self.title = title_text_full
            self.bookmark_title = self.get_bookmark_title(title_text_full)
        except Exception as e:
            logging.warning('parse title exception %s', e)
            self.success = False

    @staticmethod
    def get_bookmark_title(full_title: str) -> str:
        year_match = re.search("\s(\(\d{4}(-\d{4})?\))\s", full_title)
        year = year_match.group(1).strip()
        title = full_title[:year_match.start()].strip()
        try:
            title = title[:title.index(' / ')]
        except ValueError:
            pass
        return '%s %s' % (title, year)


def parse(source: str) -> Optional[list]:
    try:
        document = lxml.html.fromstring(source)
    except (ParserError, TypeError) as e:
        logging.warning('parse exception %s', e)
        return None

    try:
        rows = document.xpath('//div[@id="index"]//tr[@class!="backgr"]')
    except IndexError:
        return None

    return [TorrentItem(r) for r in rows]


async def fetch(session, page: int) -> bool:
    start_time = time.time()
    url = URL % page
    async with session.get(url, headers={'User-Agent': USER_AGENT}) as resp:
        response_content = await resp.text()
        fetch_time = time.time()
        logging.debug('Fetch {}: {} {}, took: {:.2f} seconds'.format(url, len(response_content), resp.status,
                                                                     fetch_time - start_time))
        if resp.status != 200:
            return False

        result, parse_data = parse(response_content)
        parse_time = time.time()
        logging.debug('Parse %s: %s %s, took: {%.2f} seconds', url, result, len(parse_data), parse_time - fetch_time)

        # todo save rows
        save_time = time.time()
        logging.debug('Save %s: took: {%.2f} seconds', url, save_time - parse_time)

        return True


async def task(pid: int, page_number: int, sem: asyncio.Semaphore):
    async with sem:
        logging.debug('Task {} started ({})'.format(pid, page_number))
        async with aiohttp.ClientSession() as session:
            try:
                async with async_timeout.timeout(TIMEOUT):
                    result = await fetch(session, page_number)
                    logging.info('process result %d %s', page_number, result)
            except BaseException as e:
                logging.warning('Exception %s %s' % (type(e), str(e)))


async def main():
    logging.info('Start %s clients for %s pages parse' % (CONCURRENCY, PAGES_COUNT))
    start_time = time.time()

    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = [asyncio.ensure_future(task(page, page, sem)) for page in range(PAGES_COUNT)]
    await asyncio.wait(tasks)

    end_time_in_sec = time.time() - start_time
    logging.info("End %.2f seconds" % end_time_in_sec)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.DEBUG if DEBUG else logging.INFO)

    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(main())
    ioloop.close()
