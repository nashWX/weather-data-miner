import json
from asgiref.sync import sync_to_async
from pyppeteer import launch
from ..models import HashTag
from .helpers import (
    userAgent,
    login
)

async def get_hashtag():
    try:
        tags = await sync_to_async(HashTag.objects.filter)(post=None)
        if not len(tags):
            return

        browser = await launch({'args': [
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--no-first-run',
            '--no-sandbox',
            '--no-zygote',
            '--deterministic-fetch',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials'],
        })
        page = await browser.newPage()
        await page.setUserAgent(userAgent)
        await login(page)

        for tag in tags:
            await page.goto(
                "https://www.instagram.com/web/search/topsearch/?context=hashtag&query="
                + tag.name.lower(),
                {
                    "waitUntil": "networkidle0",
                },
            )

            finalResponse = await page.evaluate("""() => {
                const pre = document.querySelector('pre');
                return pre.textContent;
            }""")

            data = json.loads(finalResponse)
            
            for hash in data['hashtags']:
                hashtag = hash['hashtag']
                if hashtag['name'] == tag.name.lower():
                    tag.post = hashtag['media_count']
                    await sync_to_async(tag.save)()
                    break
    except Exception as e:
        print(f'Exception raised {e}')
    await page.close()
    await browser.close()