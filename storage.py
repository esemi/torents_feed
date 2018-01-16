import logging
import datetime

from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio

from config import MONGO_HOST, MONGO_PORT, MONGO_DB


class Storage(object):
    def __init__(self):
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        self.bookmarks = db.bookmark_collection
        self.torrents = db.torrent_collection

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
