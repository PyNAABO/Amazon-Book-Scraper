from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import json
import os

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend origin for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOOKS_FILE = 'books.json'


@app.get("/")
def read_root():
    return {"message": "Backend is live 👋"}


@app.get("/scrape")
def scrape_amazon(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/89.0.4389.82 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find(id='productTitle')
        title = title.get_text(strip=True) if title else "Title not found"

        authors = soup.select('.author .a-link-normal')
        if not authors:
            authors = soup.select('.contributorNameID')
        author_names = [a.get_text(strip=True) for a in authors]

        image = (
            soup.find(id='imgBlkFront') or
            soup.find(id='ebooksImgBlkFront') or
            soup.select_one('.imgTagWrapper img') or
            soup.find(id='landingImage')
        )
        image_url = image['src'] if image and 'src' in image.attrs else "No image found"

        # Create book data dictionary
        book_data = {
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
    if not os.path.exists(BOOKS_FILE):
        return []

    with open(BOOKS_FILE, 'r') as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError:
            return []


def save_to_json(book):
    # Load existing data
    data = []
    if os.path.exists(BOOKS_FILE):
        try:
            with open(BOOKS_FILE, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

    # Add new book
    data.append(book)

    # Save back to file
    with open(BOOKS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
