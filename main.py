import logging
import time
from contextlib import contextmanager
from enum import Enum

import aiofiles
import aiohttp
import asyncio
import pymorphy2
from async_timeout import timeout
import adapters
from adapters.inosmi_ru import sanitize
from text_tools import split_by_words, calculate_jaundice_rate
from anyio import create_task_group

MAX_TIME_OF_RUNNING_FUNC = 3


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


@contextmanager
def count_runtime():
    time_of_start = time.monotonic()
    yield
    time_of_end = time.monotonic()
    logging.info(f'Анализ закончен за {time_of_end - time_of_start}')


async def process_article(session, morph, charged_words, url, analyses):
    with count_runtime():
        try:
            async with timeout(MAX_TIME_OF_RUNNING_FUNC):
                html = await fetch(session, url)
            text = sanitize(html, True)

            async with timeout(MAX_TIME_OF_RUNNING_FUNC):
                article_words = await split_by_words(morph, text)

            score = calculate_jaundice_rate(article_words, charged_words)
            article_words_count = len(article_words)

            status = ProcessingStatus.OK.name
        except aiohttp.ClientError:
            score = None
            article_words_count = None
            status = ProcessingStatus.FETCH_ERROR.name
        except adapters.ArticleNotFound:
            score = None
            article_words_count = None
            status = ProcessingStatus.PARSING_ERROR.name
        except asyncio.TimeoutError:
            score = None
            article_words_count = None
            status = ProcessingStatus.TIMEOUT.name
        finally:
            analyses.append({
                'url': url,
                'score': score,
                'article_words': article_words_count,
                'status': status,
            })


async def read_file(filename):
    async with aiofiles.open(filename, mode='r', encoding='utf-8') as file:
        lines = await file.readlines()
    cleaned_lines = [line.rstrip('\n') for line in lines]
    return cleaned_lines


async def start_analyses(urls: list):
    async with aiohttp.ClientSession() as session:
        charged_words = await read_file('lists_of_words/negative_words.txt')
        morph = pymorphy2.MorphAnalyzer()
        analyses = []
        async with create_task_group() as tg:
            for article in urls:
                tg.start_soon(process_article, session, morph, charged_words, article, analyses)

    return analyses


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    urls = []
    asyncio.run(start_analyses(urls))
