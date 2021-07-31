import json
from pyppeteer import launch
from ..models import HashTag
from .helpers import (
    userAgent,
    login
)

async def get_hashtag(name):
    try:
        tag = HashTag.objects.get(name=name)
        if tag.post is not None:
            return

        browser = await launch()
        page = await browser.newPage()
        await page.setUserAgent(userAgent)
        await login(page)

        await page.goto(
            "https://www.instagram.com/web/search/topsearch/?context=hashtag&query="
            + name.lower(),
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
            if hashtag['name'] == name.lower():
                tag.post = hashtag['media_count']
                tag.save()
                break
        await browser.close()
    except Exception as e:
        await browser.close()
        print(f'Exception raised {e}')