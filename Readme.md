# NewsAI

NewsAI is an AI-powered news content creation system that collects, summarizes, and generates engaging news articles using FastAPI and Generative AI.

## Features
- Fetches news from  sources (NewsAPI, Web Scraping)
- Summarizes news content using AI
- Generates structured news articles
- Provides keyword extraction for better search

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/narayanghimire/newsai.git
cd newsai
```


### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory and add:
```env
SECRET_KEY=your-fastapi-secret-key
OPENAI_API_KEY=your-openapi-secret-key
GEMINI_API_KEY=
NEWS_API_KEY=
PINECONE_API_KEY=your-pinecone-api-key
```

### 5. Run the Application
```bash
uvicorn app.main:app --reload
```

### 6. Access the application
Once the server is running, open:
- URL: [http://127.0.0.1:8000/



