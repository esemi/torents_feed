import logging
import time

import aiohttp
import async_timeout
from sanic import Sanic
from sanic.response import json, file

from config import *


logging.basicConfig(
    level=logging.INFO
)
log = logging.getLogger()

app = Sanic(__name__, log_config=None)
app.config.from_object({'KEEP_ALIVE': False})

# todo static serve for local run


@app.route("/rutor/bookmarks.json")
async def backlinks(request, rootdomain):
        start_time = time.time()
        bookmarks = []
        try:
            response = await fetch(session, BACKLINKS_URL_MAP % (API_KEY, rootdomain))
        except BaseException as e:
            log.warning('api request exception %s %s %.2f' % (e, rootdomain, time.time() - start_time))
            return json({'message': 'API timeout'}, status=500)
        else:
            log.info('api request %s %.2f' % (rootdomain, time.time() - start_time))
            backlinks = [i.split(';') for i in response.split('\r\n')[1:-1]]
            await cache.set(rootdomain, backlinks)
        return json({'bookmarks': bookmarks})


async def fetch(session, url):
    with async_timeout.timeout(API_TIMEOUT):
        async with session.get(url) as response:
            return await response.text()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8020, debug=DEBUG, workers=1)
