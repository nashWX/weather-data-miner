from pyppeteer import launch


# get all links from .download-box container in the page

async def download_media(url='https://www.instagram.com/p/CeJUPtRJyhI/?utm_source=ig_web_copy_link'):
    browser = await launch({
        'headless': True,   
        'handleSIGINT':False,
        'handleSIGTERM':False,
        'handleSIGHUP':False,
        'args': ['--no-sandbox', '--disable-setuid-sandbox']
    })
    page = await browser.newPage()
    links = []
    try:
        await page.goto('https://snapinsta.app')
        await page.waitForSelector('#url')
        await page.type('#url', url)
        await page.waitFor(300)
        await page.click('#send')
        await page.waitForSelector('.download-items')

        links = await page.evaluate('''() => {
            const links = []
            document.querySelectorAll('.download-items').forEach(item => {
                links.push({
                    cover: item.querySelector('.download-items__thumb > img').src,
                    url: item.querySelector('.download-items__btn > a').href,
                    isVideo: item.querySelector('.download-items__thumb').classList.contains('video')
                });
            });
            return links;
        }''')
        await page.close()
        await browser.close()
        return links
    except Exception as e:
        print(f'got this exception {e}')
    await page.close()
    await browser.close()
    return links

if __name__ == '__main__':
    import asyncio
    val = asyncio.run(download_media())
    print(val)