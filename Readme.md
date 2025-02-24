# AI-Powered News Summarization System

## Project Title
- **AI-Powered News Aggregation and Summarization System**
- **Leveraging LLM and RAG for Efficient News Summarization**

## Project Overview
- **Objective:** Provide concise and relevant news summaries from different sources using AI.
- **Purpose:** Enhance user experience with accurate news summaries.
- **Tech Stack:**
  - **Frontend:** HTML/CSS, JavaScript
  - **Backend:** FastAPI
  - **Database:** SQLite, Pinecone Vector DB
- **GPT Models Implemented:**
  - GPT-4o-mini (OpenAI)
  - Gemini-2.0-Flash (Google AI)
  - Llama-3-70B-Versatile (Groq)
- **Key Technique:**
  - **RAG (Retrieval-Augmented Generation):** Used for relevant news retrieval and enhanced summarization accuracy.

---

## Workflow Overview

1. **User Authentication & Account Creation**
   - Secure login mechanisms for access.
   - New users must create an account before accessing the news features.

2. **User Requests News**
   - Natural language prompts for news queries (e.g., "Latest tech trends in AI").

3. **Keyword Extraction Using GPT**
   - The selected LLM processes the user’s prompt to generate optimized search keywords.
   - Keywords are used to:
     - Formulate an accurate search query for the News API.
     - Create vector embeddings for retrieval using the RAG system.

4. **Fetching News Articles**
   - Request is sent to NewsAPI using the generated search query.
   - Relevant news articles are returned based on the keywords.

5. **Storing News in Vector Database**
   - Fetched articles are embedded and stored in a vector database (Pinecone or equivalent).
   - Full content is also stored in a relational database for later use.

6. **Retrieving Relevant Articles**
   - Retrieves the top 5 most relevant articles using semantic similarity to the generated keywords.
   - Ranks articles based on relevance using vector embeddings.

7. **News Summarization with LLM**
   - Summarizes the top 5 articles while maintaining key facts.
   - Only the sources used in the summary are explicitly listed for transparency.

8. **Delivering Summarized News**
   - Summarized news is sent to the frontend in a structured and readable format.
   - Includes source URLs for credibility.

9. **Storing Summaries**
   - The generated summary and source articles are stored in the database.
   - Users can access previously generated summaries from their profile.

---

## Key Features & Enhancements

- ✅ **User Authentication** – Secure access for registered users.
- ✅ **LLM-Powered Search Optimization** – Accurate news retrieval.
- ✅ **RAG Implementation** – Improved news relevance.
- ✅ **Vector Database for Similarity Search** – Efficient article retrieval.
- ✅ **LLM-Based Summarization** – Clear and engaging news summaries.
- ✅ **Source Transparency** – Credible referencing for user trust.

---

## GPT Model Comparison

| Feature               | GPT-4o-mini (OpenAI)       | Gemini-2.0-Flash (Google AI) | Llama-3-70B-Versatile (Groq) |
|-----------------------|----------------------------|-------------------------------|------------------------------|
| **Token Limit**       | 128K tokens                 | Up to 1M tokens                | 5K tokens (Groq-enforced)     |
| **Cost**              | Cheaper than GPT-4          | More cost-efficient             | Most affordable               |
| **API Structure**     | Standard OpenAI API         | Similar to Google AI API        | Uses Meta AI's API structure   |
| **Custom Instructions** | Developer role (optional) | System instructions supported   | Uses system role               |
| **Temperature Control** | ✅ Yes                     | ✅ Yes                          | ✅ Yes                         |
| **Direct Object Parsing** | ✅ Structured JSON      | ✅ Structured JSON               | ❌ Raw text response only      |

---

## Conclusion & Future Scope

- **Summary:** Efficient news aggregation and summarization using AI.
- **Impact:** Enhanced user experience with relevant and concise news.
- **Future Scope:**
  - Multi-language support for global reach.
  - Enhanced personalization with advanced user preferences.
  - Integration with more news APIs for comprehensive coverage.

---

## Installation & Setup

1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```bash
    cd ai-news-aggregator
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set Up Environment Variables
Create a `.env` file in the root directory and add:
```env
SECRET_KEY=your-fastapi-secret-key
OPENAI_API_KEY=your-openapi-secret-key
GEMINI_API_KEY=
NEWS_API_KEY=
PINECONE_API_KEY=your-pinecone-api-key
```

5. Run the FastAPI backend:
    ```bash
    uvicorn main:app --reload
    ```
6. Access the application
Once the server is running, open:
- URL: http://127.0.0.1:8000/

---


