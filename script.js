const backendUrl = 'https://amazon-book-scraper.onrender.com/scrape';

const scrapeButton = document.getElementById('scrapeButton');
const amazonUrlInput = document.getElementById('amazonUrl');
const statusMessage = document.getElementById('statusMessage');

const bookDetails = document.getElementById('bookDetails');
const bookTitle = document.getElementById('bookTitle');
const bookAuthor = document.getElementById('bookAuthor');
const bookImageUrl = document.getElementById('bookImageUrl');
const bookImage = document.getElementById('bookImage');

scrapeButton.addEventListener('click', async () => {
  const url = amazonUrlInput.value.trim();
  if (!url) {
    showStatus('Please enter a valid Amazon book URL.', 'red');
    return;
  }

  showStatus('Scraping book info...', 'black');
  bookDetails.style.display = 'none';

  try {
    const response = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
    const data = await response.json();

    if (data.error) {
      showStatus('Error: ' + data.error, 'red');
      return;
    }

    bookTitle.textContent = data.bookName || 'No title found';
    bookAuthor.textContent = data.authors?.join(', ') || 'No author found';
    bookImageUrl.textContent = data.imageUrl || 'No image found';
    bookImage.src = data.imageUrl || '';
    bookImage.alt = data.bookName || 'Book Cover';

    bookDetails.style.display = 'block';
    showStatus('Book data loaded!', 'green');
  } catch (err) {
    showStatus('Fetch failed: ' + err.message, 'red');
  }
});

function showStatus(msg, color = 'black') {
  statusMessage.textContent = msg;
  statusMessage.style.color = color;
}

function copyText(elementId) {
  const text = document.getElementById(elementId).textContent;
  const button = event.target;

  navigator.clipboard.writeText(text).then(() => {
    const originalText = button.textContent;
    const originalColor = button.style.backgroundColor;

    button.textContent = 'Copied✅';
    button.style.backgroundColor = 'green';

    setTimeout(() => {
      button.textContent = originalText;
      button.style.backgroundColor = originalColor;
    }, 1500);
  });
}
