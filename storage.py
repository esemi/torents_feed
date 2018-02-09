import logging
import datetime

import pymongo
from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio

from config import MONGO_HOST, MONGO_PORT, MONGO_DB


class Storage(object):
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_HOST, MONGO_PORT)
        db = self.client[MONGO_DB]
        self.bookmarks = db.bookmark_collection
        self.torrents = db.torrent_collection

    def set_io_loop(self, loop):
        self.client.io_loop = loop

    async def save_rows(self, items: list) -> tuple():
        new_bookmarks = 0
        new_items = 0
        for item in items:
            if not item.success:
                continue

            bookmark_document = {'_id': item.bookmark_title, 'favorite': False, 'trash': False,
                                 'date_create': datetime.datetime.utcnow()}
            try:
                insert_bookmark = await self.bookmarks.insert_one(bookmark_document)
                logging.debug('save new bookmark %s', insert_bookmark.inserted_id)
                new_bookmarks += 1
            except DuplicateKeyError:
                logging.debug('bookmark already exist %s', item.bookmark_title)

            try:
                await self.torrents.insert_one(item.repr_storage_object())
                logging.debug('save new torrent item %s', item.repr_storage_object())
                new_items += 1
            except DuplicateKeyError:
                logging.debug('torrent item already exist %s %s', item.id, item.title)

        return new_items, new_bookmarks

    async def get_stat(self) -> dict:
        o = dict()

        last_bookmark = await self.bookmarks.find_one(sort=[('date_create', pymongo.DESCENDING)], limit=1)
        last_torrent = await self.torrents.find_one(sort=[('date_create', pymongo.DESCENDING)], limit=1)

        o['last_bookmark'] = None if not last_bookmark else last_bookmark['_id']
        o['last_torrent'] = None if not last_torrent else last_torrent['title']
        try:
            o['last_update'] = max(last_bookmark['date_create'], last_torrent['date_create'])
        except KeyError:
            o['last_update'] = None
        o['total_bookmarks'] = await self.bookmarks.find().count()
        o['total_torrents'] = await self.torrents.find().count()
        return o

    async def get_torrents_by_bookmark(self, bookmark_id: str) -> list:
        return await self.torrents.find({'bookmark_id': bookmark_id}, sort=[('size_gb', pymongo.ASCENDING)]).to_list(None)

    async def get_unsort_bookmarks(self, limit: int) -> list:
        return await self.bookmarks.find({'favorite': False, 'trash': False}, projection=['_id'],
                                         sort=[('date_create', pymongo.DESCENDING)], limit=limit).to_list(None)

    async def get_trash_bookmarks(self, limit: int, offset: int=0) -> list:
        return await self.bookmarks.find({'trash': True}, projection=['_id'],
                                         sort=[('date_create', pymongo.DESCENDING)], limit=limit, skip=offset).to_list(None)

    async def get_favorite_bookmarks(self, limit: int, offset: int=0) -> list:
        return await self.bookmarks.find({'favorite': True, 'trash': False}, projection=['_id'],
                                         sort=[('date_create', pymongo.DESCENDING)], limit=limit, skip=offset).to_list(None)
