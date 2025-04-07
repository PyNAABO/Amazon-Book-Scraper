from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import json
import os

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOOKS_FILE = 'books.json'


@app.get("/")
def read_root():
    return {"message": "Backend is live 👋"}


print("hello world!!")


@app.get("/scrape")
def scrape_amazon(url: str):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/89.0.4389.82 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        with open('response.html', 'w', encoding='utf-8') as file:
            file.write(str(response.text))

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find(id='productTitle')
        title = title.get_text(strip=True) if title else "Title not found"

        if (title == "Title not found" and "enter the characters you see below"
                in response.text.lower()):
            return {
                "error":
                "🚫 Blocked by Amazon CAPTCHA!! Please try again later."
            }

        authors = soup.select('.author .a-link-normal')
        if not authors:
            authors = soup.select('.contributorNameID')
        author_names = [a.get_text(strip=True) for a in authors]

        image = (soup.find(id='imgBlkFront')
                 or soup.find(id='ebooksImgBlkFront')
                 or soup.select_one('.imgTagWrapper img')
                 or soup.find(id='landingImage'))
        image_url = image[
            'src'] if image and 'src' in image.attrs else "No image found"

        book_data = {
            "id": get_next_id(),
            "bookName": title,
            "authors": author_names if author_names else ["Unknown Author"],
            "imageUrl": image_url
        }

        save_to_json(book_data)
        return book_data

    except Exception as e:
        return {"error": str(e)}


@app.get("/books")
def get_all_scraped_books():
    return load_books()


@app.get("/books/consume")
def consume_and_clear_books():
    books = load_books()

    # Clear the file right after reading
    with open(BOOKS_FILE, 'w') as f:
        f.write('[]')

    return books


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    books = load_books()
    filtered_books = [book for book in books if book["id"] != book_id]

    if len(books) == len(filtered_books):
        raise HTTPException(status_code=404, detail="Book not found")

    with open(BOOKS_FILE, 'w') as f:
        json.dump(filtered_books, f, indent=2)

    return {"message": f"Book with id {book_id} deleted ✅"}


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


def get_next_id():
    books = load_books()
    if not books:
        return 1
    return max(book["id"] for book in books) + 1
