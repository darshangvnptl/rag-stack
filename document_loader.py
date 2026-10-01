import os
import sys
from dotenv import load_dotenv
load_dotenv()
from  pathlib import Path
from langchain-text-splitter import RecursiveCharacterTextSplitter
from lan

def load_text_file():   
    with tmpfile.NameTemporaryFile(suffix=".txt", delete=False) as tmpfile:
        tmpfile.write(b"This is a sample text file.")
        tmpfile_path = tmpfile.name

    try:
        loader = TextLoader(tmpfile_path)
        documents = loader.load()
        print(f"Loaded {len(documents)} document(s) from text file.")

        for doc in documents:
            print(f"Document content: {doc.page_content}")
    finally:
        os.remove(tmpfile_path)


