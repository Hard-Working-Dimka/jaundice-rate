import json

from aiohttp import web
from main import start_analyses


async def handle(request):
    raw_data = request.query.get('urls')

    urls = [url for url in raw_data.split(',')]
    analyses = await start_analyses(urls)

    data = []
    for analysis in analyses:
        data.append({
            'Заголовок:': analysis['url'],
            'Рейтинг:': analysis['score'],
            'Слов в статье:': analysis['article_words'],
            'Статус:': analysis['status'],
        })

    return web.json_response(data, text=None, body=None, status=200, reason=None, headers=None,
                             content_type='application/json', dumps=json.dumps)


app = web.Application()
app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app)
    # web.run_app(app, access_log=None)
