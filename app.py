from sanic import Sanic
from sanic.response import json
from sanic import Blueprint

from storage import Storage
import config

S = Storage()

app = Sanic(__name__)
app.config.from_object({'KEEP_ALIVE': False})

rutor_bp = Blueprint('rutor', url_prefix='/rutor')
rutor_bp.static('/static', './static')


@app.listener('before_server_start')
def init(sanic, loop):
    S.set_io_loop(loop)


@rutor_bp.get("/stat.json")
async def bookmark_unsort(request):
    stat = await S.get_stat()
    return json({'stat': stat})


@rutor_bp.get("/bookmarks/unsort.json")
async def bookmark_unsort(request):
    limit = int(request.args.get('limit', 100))
    bookmarks = await S.get_unsort_bookmarks(max(config.LIMIT_MAX, limit))
    return json({'bookmarks': bookmarks})


@rutor_bp.get("/bookmarks/trash.json")
async def bookmark_trash(request):
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    bookmarks = await S.get_trash_bookmarks(max(config.LIMIT_MAX, limit), offset)
    return json({'bookmarks': bookmarks})


@rutor_bp.get("/bookmarks/favorite.json")
async def bookmark_favorite(request):
    bookmarks = await S.get_favorite_bookmarks()
    return json({'bookmarks': bookmarks})


app.blueprint(rutor_bp, url_prefix='/rutor')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8020, debug=config.DEBUG, workers=1)

