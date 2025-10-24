import json

from aiohttp import web


async def handle(request):
    raw_data = request.query.get('urls')

    urls = [ url for url in raw_data.split(',')]
    print(urls)

    data = {'urls': urls}

    return web.json_response(data, text=None, body=None, status=200, reason=None, headers=None,
                            content_type='application/json', dumps=json.dumps)


app = web.Application()
app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app)
