import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import time

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create a serverless index
index_name = "news-index"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)

news_index = pc.Index(index_name)


