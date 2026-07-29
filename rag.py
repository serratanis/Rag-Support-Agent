import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# A separate vector database folder and collection are used for this bot.
# If another bot/service is running on the same server (e.g., a different chatbot),
# they are consciously isolated so that knowledge bases do not mix.
VECTOR_DB_PATH = "./vector_store"
KNOWLEDGE_DIR = "knowledge_base"


def create_database():

    documents = []

    for file in os.listdir(KNOWLEDGE_DIR):

        if file.endswith(".txt"):

            loader = TextLoader(
                f"{KNOWLEDGE_DIR}/{file}",
                encoding="utf-8"
            )

            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=220,   # FAQ entries are short - small chunk prevents
        chunk_overlap=0,  # answers belonging to different questions from mixing
        separators=["\n\n\n", "\n\n", "\n", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH
    )

    return db


db = create_database()


def search_knowledge(query):

    results = db.similarity_search(query, k=3)

    if not results:
        return ""

    context = ""

    for result in results:
        context += result.page_content + "\n"

    return context
