from dotenv import load_dotenv
load_dotenv()

from langchain_core import __version__  as core_version
from langgraph import __version__ as graph_version
from langchain_ollama import __version__ as ollama_version

def main():
    print("Hello from rag-stack!")
    print(f"langchain-core version: {core_version}")
    print(f"langgraph version: {graph_version}")
    print(f"langchain-ollama version: {ollama_version}")

if __name__ == "__main__":
    main()
