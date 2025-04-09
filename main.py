from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests
import random
import json
import os
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15"
]

FREE_PROXIES = ["http://34.140.197.165:3128", "http://64.225.8.174:9991"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOOKS_FILE = 'books.json'


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <h1>Backend is live 👋</h1>
    <p>View the <a href='/latest'>latest scraped HTML</a>.</p>
    """


def get_random_proxy():
    return {
        "http": random.choice(FREE_PROXIES),
        "https": random.choice(FREE_PROXIES)
    }


def log_blocked_url(url):
    with open('blocked_urls.json', 'a') as f:
        f.write(json.dumps({"url": url}) + '\n')


@app.get("/scrape")
def scrape_amazon(url: str):
    SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY')
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1"
    }

    time.sleep(random.uniform(2, 6))
    print(f"Using User-Agent: {headers['User-Agent']}")

    try:
        scraper_url = (f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}"
                       f"&url={url}&country_code=us&render=true")
        response = requests.get(scraper_url, headers=headers, timeout=10)
        with open('response.html', 'w', encoding='utf-8') as file:
            file.write(str(response.text))

        if "captcha" in response.text.lower(
        ) or "enter the characters you see below" in response.text.lower():
            raise Exception("Blocked by CAPTCHA")

    except Exception:
        print(
            "ScraperAPI failed or CAPTCHA detected. Falling back to proxy...")
        proxy = get_random_proxy()
        try:
            response = requests.get(url,
                                    headers=headers,
                                    proxies=proxy,
                                    timeout=10)
        except Exception as inner_err:
            log_blocked_url(url)
            return {"error": f"All attempts failed: {inner_err}"}

    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find(id='productTitle')
    title = title.get_text(strip=True) if title else "Title not found"

    if title == "Title not found" or "enter the characters you see below" in response.text.lower(
    ):
        log_blocked_url(url)
        return {
            "error": "🚫 Blocked by Amazon CAPTCHA!! Please try again later."
        }

    authors = soup.select('.author .a-link-normal')
    if not authors:
        authors = soup.select('.contributorNameID')
    author_names = [a.get_text(strip=True) for a in authors]

    image = (soup.find(id='imgBlkFront') or soup.find(id='ebooksImgBlkFront')
             or soup.select_one('.imgTagWrapper img')
             or soup.find(id='landingImage'))
    image_url = image[
        'src'] if image and 'src' in image.attrs else "No image found"

    book_data = {
        "bookName": title,
        "authors": author_names if author_names else ["Unknown Author"],
        "imageUrl": image_url
    }

    save_to_json(book_data)
    return book_data


@app.get("/books")
def get_all_scraped_books():
    return load_books()


@app.get("/latest")
def get_latest_response():
    file_path = "response.html"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404,
                            detail="No HTML response saved yet.")
    return FileResponse(file_path, media_type="text/html")


@app.get("/books/consume")
def consume_and_clear_books():
    books = load_books()
    with open(BOOKS_FILE, 'w') as f:
        f.write('[]')
    return books


@app.delete("/books/title/{book_title}")
def delete_book_by_title(book_title: str):
    decoded_title = unquote(book_title).strip().lower()
    books = load_books()

    filtered_books = [
        book for book in books
        if book.get("bookName", "").strip().lower() != decoded_title
    ]

    if len(books) == len(filtered_books):
        raise HTTPException(status_code=404, detail="Book not found")

    with open(BOOKS_FILE, 'w') as f:
        json.dump(filtered_books, f, indent=2)

    return {"message": f"Book titled '{book_title}' deleted ✅"}


# Utilities
def load_books():
    if not os.path.exists(BOOKS_FILE):
        return []
    try:
        with open(BOOKS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_to_json(book):
    books = load_books()
    books.append(book)
    with open(BOOKS_FILE, 'w') as f:
        json.dump(books, f, indent=4)
