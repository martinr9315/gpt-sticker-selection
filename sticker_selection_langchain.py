import openai
import csv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

# Initialize API client
openai.api_key = "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"

# Load sticker text csv
loader = CSVLoader(file_path='./sticker_slugs.csv')
data = loader.load()

# Split it into chunks, embed each chunk and load it into the vector store.
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
slugs = text_splitter.split_documents(data)
db = FAISS.from_documents(slugs, OpenAIEmbeddings())
