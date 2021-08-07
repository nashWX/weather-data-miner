import asyncio
import json
from pathlib import Path
from decouple import config
from django.conf import settings
import aiofiles

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70"


def getCookiePath():
    filePath = settings.BASE_DIR / 'static' / 'cookie'
    Path(filePath).mkdir(parents=True, exist_ok=True)
    return filePath

async def get_population(location, page):
    try:
        await page.goto(
            f"https://www.google.com/search?q={location}+population&gl=us&hl=en",
            {
                "waitUntil": "load",
            },
        )

        pop = await page.evaluate(
            """() => {
            const content = document.querySelector(`div[role='heading'][aria-level="3"]`);
                if(content) {
                    return content.textContent.split(' ')[0]
                }
            }"""
        )

        if pop:
            return pop
    except Exception as e:
        print(f"cannot retrive population {e}")

    return "UNKNOWN"


async def get_population_from_wiki(name, page):
    try:
        url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
        await page.goto(url, {"waitUntil": "load"})

        result = await page.evaluate("""() => {
            const trList = document.querySelectorAll('table.infobox.geography tr');
            let pop = null;
            if (trList) {
                for (let i in trList) {
                    if(trList[Number(i)] && trList[Number(i)].textContent && trList[Number(i)+1] && trList[Number(i)+1].textContent &&  trList[Number(i)].textContent.includes('Population')) {
                        pop = trList[Number(i)+1].textContent.replace(/\D/g, '');
                        break;
                    }
                }
            }

            return pop;
        }""")

        if result:
            return result
    except Exception as e:
        print(f'cannot retrive population {e}')
    
    return 'UNKNOWN'
    

async def get_location(location, page):
    try:
        await page.goto(
            "https://www.instagram.com/web/search/topsearch/?context=place&query="
            + location,
            {
                "waitUntil": "networkidle0",
            },
        )
        finalResponse = await page.evaluate(
            """() => {
            const pre = document.querySelector('pre');
            return pre.textContent;
        }"""
        )
        data = json.loads(finalResponse)
        for place in data["places"]:
            if (
                location.lower() == place["place"]["title"].lower()
                or location.lower() == place["place"]["location"]["name"].lower()
            ):
                return place["place"]
    except Exception as e:
        print(f"unable to fetch location from Instagram {e}")

    return None


async def login(page, username='mahmudursiam'):
    try:
        if Path(getCookiePath()/f'{username}.json').is_file():
            async with aiofiles.open(getCookiePath()/f'{username}.json','r') as f:
                cookies = await f.read()
                cookieObject = json.loads(cookies)
                for cookie in cookieObject:
                    await page.setCookie(cookie)

        await page.goto(
            "https://www.instagram.com/accounts/login/",
            {
                "waitUntil": "load",
            },
        )

        loggedIn = await page.evaluate("""() => {
            const loggedIn = document.querySelector('.logged-in');
            return loggedIn ? true : false;
        }""")

        print(f'logged in {loggedIn} ')

        if loggedIn:
            print('hurrray user is already logged in ')
            return True
        
        username = username or config("insta_user", cast=str, default='motailab')
        password = config("insta_password", cast=str, default='12Mobile')

        await page.waitForSelector('input[name="username"]')
        await page.type('input[name="username"]', username)
        await page.type('input[name="password"]', password)
        await asyncio.wait(
            [
                asyncio.create_task(page.click('[type="submit"]')),
                asyncio.create_task(
                    page.waitForNavigation(
                        {
                            "waitUntil": "networkidle0",
                        }
                    )
                ),
            ]
        )

        async with aiofiles.open(getCookiePath()/f'{username}.json','w') as f:
            cookieObject = await page.cookies()
            await f.write(json.dumps(cookieObject))
    
    except Exception as e:
        print(f"cannot login to instagram {e}")
    
    return False
