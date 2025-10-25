from aiohttp import web
from main import start_analyses

MAX_URLS = 2
MAX_TIME_DOWNLOADING = 3
MAX_TIME_ANALYZING = 3


async def handle(request):
    raw_data = request.query.get('urls')
    urls = [url for url in raw_data.split(',')]

    if len(urls) > MAX_URLS:
        data = {'error': 'Too many urls'}
        return web.json_response(data=data, status=400, content_type='application/json', )

    analyses = await start_analyses(urls, MAX_TIME_DOWNLOADING, MAX_TIME_ANALYZING)

    data = []
    for analysis in analyses:
        data.append({
            'Заголовок:': analysis['url'],
            'Рейтинг:': analysis['score'],
            'Слов в статье:': analysis['article_words'],
            'Статус:': analysis['status'],
        })

    return web.json_response(data, status=200, reason=None, content_type='application/json')


app = web.Application()
app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app)
    # web.run_app(app, access_log=None) FIXME: turn on to fix error with start time (aiohttp)
