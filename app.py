import urllib.parse

from sanic import Sanic
from sanic.response import json
from sanic import Blueprint

from storage import Storage
import config

S = Storage()

app = Sanic(__name__)
app.config.from_object({'KEEP_ALIVE': False})
app.static('/static', './static')


@app.listener('before_server_start')
def init(sanic, loop):
    S.set_io_loop(loop)


@app.get("/stat.json")
async def stat(request):
    stat = await S.get_stat()
    return json({'stat': stat})


@app.get("/torrents/<bookmark_id>")
async def bookmark_torrents(request, bookmark_id):
    torrents = await S.get_torrents_by_bookmark(urllib.parse.unquote(bookmark_id))
    return json({'torrents': torrents})


@app.get("/bookmarks/unsort.json")
async def bookmark_unsort(request):
    limit = int(request.args.get('limit', 100))
    bookmarks = await S.get_unsort_bookmarks(max(config.LIMIT_MAX, limit))
    return json({'bookmarks': bookmarks})


@app.get("/bookmarks/trash.json")
async def bookmark_trash(request):
    limit = int(request.args.get('limit', 100))
    bookmarks = await S.get_trash_bookmarks(max(config.LIMIT_MAX, limit))
    return json({'bookmarks': bookmarks})


@app.get("/bookmarks/favorite.json")
async def bookmark_favorite(request):
    limit = int(request.args.get('limit', 100))
    bookmarks = await S.get_favorite_bookmarks(max(config.LIMIT_MAX, limit))
    return json({'bookmarks': bookmarks})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8020, debug=config.DEBUG, workers=1)

