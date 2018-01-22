#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-
import datetime
import time
import asyncio
import logging
from typing import Optional
import re

import aiohttp
import async_timeout
import lxml.html
from lxml.etree import ParserError

import config
from storage import Storage

S = Storage()


class TorrentItem(object):
    success = True
    id = None
    link = None
    tor_link = None
    size = None
    title = None
    bookmark_title = None
    date_create = datetime.datetime.utcnow()

    def __init__(self, row_elem: lxml.html.HtmlElement=None):
        """Русское название / Оригинальное название (Год выпуска) Качество видео | Качество перевода | Версия"""
        try:
            torent_link = row_elem.xpath('.//a[@class="downgif"]/@href')[0].strip()
            logging.debug('parse id debug "%s"', torent_link)
            self.id = int(re.findall("/download/([\d]+)", torent_link)[0])
            self.tor_link = config.RUTOR_HOST + torent_link
            self.link = '%s/torrent/%d' % (config.RUTOR_HOST, self.id)
        except Exception as e:
            logging.warning('parse id exception %s', e)
            self.success = False

        try:
            td = row_elem.xpath('.//td[last()-1]/text()')[0].strip()
            logging.debug('parse size debug "%s"', td)
            self.size = self.torrent_size_to_gbytes(td)
        except Exception as e:
            logging.warning('parse size exception %s', e)
            self.success = False

        try:
            title_text_full = row_elem.xpath('.//td[2]/a[last()]/text()')[0].strip()
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

    @staticmethod
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

    def repr_storage_object(self):
        return {
            '_id': self.id,
            'title': self.title,
            'link': self.link,
            'tor_link': self.tor_link,
            'size_gb': self.size,
            'bookmark_id': self.bookmark_title,
            'date_create': self.date_create,
        }


def parse(source: str) -> Optional[list]:
    try:
        document = lxml.html.fromstring(source)
    except (ParserError, TypeError) as e:
        logging.warning('parse init exception %s', e)
        return None

    try:
        rows = document.xpath('//div[@id="index"]//tr[@class!="backgr"]')
    except IndexError:
        logging.warning('rows not found')
        return None

    return [TorrentItem(r) for r in rows]


async def fetch(session, page: int) -> bool:
    start_time = time.time()
    url = config.URL % page
    async with session.get(url, encoding='utf-8', headers={'User-Agent': config.USER_AGENT}) as resp:
        response_content = await resp.text(encoding='utf-8', errors='ignore')
        fetch_time = time.time()
        logging.info('Fetch {}: content len {}, code {}, took: {:.2f} seconds'.format(url, len(response_content),
                                                                                      resp.status,
                                                                                      fetch_time - start_time))
        if resp.status != 200:
            return False

        torrents_list = parse(response_content)
        parse_time = time.time()
        logging.info('Parse %s: rows %s, took: {%.2f} seconds', url, len(torrents_list), parse_time - fetch_time)

        if torrents_list:
            new_items_count, new_bookmarks_count = await S.save_rows(torrents_list)
            save_time = time.time()
            logging.info('Save %s: new items %d, new bookmarks %s, took: {%.2f} seconds', url, new_items_count,
                         new_bookmarks_count, save_time - parse_time)

        return True


async def task(page_number: int, sem: asyncio.Semaphore):
    async with sem:
        logging.info('Task {} started'.format(page_number))
        async with aiohttp.ClientSession() as session:
            try:
                async with async_timeout.timeout(config.TIMEOUT):
                    result = await fetch(session, page_number)
                    logging.info('Task %d ended %s', page_number, result)
            except BaseException as e:
                logging.warning('Task exception %s %s' % (type(e), str(e)))
                logging.exception(e)


async def main():
    logging.info('Start %s clients for %s pages parse' % (config.CONCURRENCY, config.PAGES_COUNT))
    start_time = time.time()

    sem = asyncio.Semaphore(config.CONCURRENCY)
    tasks = [asyncio.ensure_future(task(page, sem)) for page in range(config.PAGES_COUNT)]
    await asyncio.wait(tasks)

    end_time_in_sec = time.time() - start_time
    logging.info("End %.2f seconds" % end_time_in_sec)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.DEBUG if config.DEBUG else logging.INFO)

    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(main())
    ioloop.close()
