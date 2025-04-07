const express = require('express');
const cors = require('cors');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.post('/scrape', async (req, res) => {
  const { url } = req.body;

  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0' // Trick Amazon into not blocking us
      }
    });

    const html = response.data;
    const $ = cheerio.load(html);

    const title = $('#productTitle').text().trim();
    const authors = [];
    
    $('.author .a-link-normal').each((i, el) => {
      const author = $(el).text().trim();
      if (author && !author.includes('Visit Amazon')) {
        authors.push(author);
      }
    });

    let imageUrl = $('#imgBlkFront').attr('src') || 
                   $('#ebooksImgBlkFront').attr('src') || 
                   $('.imgTagWrapper img').attr('src') || 
                   $('#landingImage').attr('src') || '';

    return res.json({
      bookName: title || 'Title not found',
      authors: authors.length ? authors : ['Author not found'],
      imageUrl: imageUrl || 'Image not found'
    });

  } catch (error) {
    console.error('Scraping failed:', error.message);
    res.status(500).json({ error: 'Failed to scrape data' });
  }
});

app.get('/', (req, res) => {
  res.send('Amazon Book Scraper is running!');
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
