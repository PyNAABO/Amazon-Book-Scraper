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
  if (!url.match(/^https?:\/\/(www\.)?amazon\.[a-z.]+\/.+$/)) {
    showStatus('That doesn’t look like a valid Amazon URL, friend. 🧐', 'red');
    return;
  }

  showStatus('Scraping book info...', getStatusColor());
  bookDetails.style.display = 'none';
  bookImage.style.display = 'none';

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

    bookImage.onload = () => bookImage.style.display = 'block';
    bookImage.onerror = () => bookImage.style.display = 'none';

    bookDetails.style.display = 'block';
    showStatus('Book data loaded!', 'green');
  } catch (err) {
    showStatus('Fetch failed: ' + err.message, 'red');
  }
});

amazonUrlInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    scrapeButton.click();
  }
});

function showStatus(msg, color = 'black') {
  statusMessage.innerHTML = `<span style="color:${color}">${msg}</span> <span class="dots"></span>`;
  animateDots();
}

function animateDots() {
  const dots = document.querySelector('.dots');
  if (!dots) return;

  let count = 0;
  const interval = setInterval(() => {
    dots.textContent = '.'.repeat(count % 4);
    count++;
  }, 300);

  setTimeout(() => clearInterval(interval), 4000);
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

function toggleDarkMode() {
  const body = document.body;
  const toggle = document.getElementById('darkToggle');
  const isDark = body.classList.toggle('dark-mode');
  toggle.textContent = isDark ? '☀️' : '🌙';
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Determine appropriate status message color
function getStatusColor() {
  return document.body.classList.contains('dark-mode') ? '#e0e0e0' : 'black';
}

// Auto theme detection + apply saved preference
window.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const shouldBeDark = savedTheme === 'dark' || (!savedTheme && prefersDark);

  if (shouldBeDark) {
    document.body.classList.add('dark-mode');
    document.getElementById('darkToggle').textContent = '☀️';
  } else {
    document.getElementById('darkToggle').textContent = '🌙';
  }
});
