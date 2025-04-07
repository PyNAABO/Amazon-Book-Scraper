from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# CORS so the frontend can talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your GitHub Pages URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        return {
            "bookName": title,
            "authors": author_names if author_names else ["Unknown Author"],
            "imageUrl": image_url
        }

    except Exception as e:
        return {"error": str(e)}
