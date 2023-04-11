import logging

from langchain import OpenAI

logging.basicConfig(level=logging.CRITICAL)

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from llama_index import GPTSimpleVectorIndex, ComposableGraph, LLMPredictor, ServiceContext, download_loader
import openai

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd

from site_scraper import recursive_scrape


load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

FILES = "./files"


def init():
    if not os.path.exists(FILES):
        os.mkdir(FILES)


def handle_exit():
    print("\nGoodbye!\n")
    

def ask(file):
    print("👀 Loading...")
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(file=Path(file))

    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt3.5-turbo"))

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=1024)
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)

    # clear the screen
    os.system("clear")

    print("✅ Ready! Let's start the conversation")
    print("ℹ️ Press Ctrl+C to exit")

    try:
        while True:
            prompt = input("\n😎 Prompt: ")
            if prompt == "exit":
                handle_exit()

            response = index.query(prompt)
            print()

            # transform response to string
            response = str(response)

            # if response starts with "\n", remove it
            if response.startswith("\n"):
                response = response[1:]

            print("👻 Response: " + response)
    except KeyboardInterrupt:
        handle_exit()


def select_file():
    os.system("clear")
    files = [file for file in os.listdir(FILES) if file.endswith(".pdf")]
    if len(files) == 0:
        return "file.pdf" if os.path.exists("file.pdf") else None
    print("📁 Select a file")
    for i, file in enumerate(files):
        print(f"{i+1}. {file}")
    print()

    try:
        possible_selections = [i for i in range(len(files) + 1)]
        selection = int(input("Enter a number, or 0 to exit: "))
        if selection == 0:
            handle_exit()
        elif selection not in possible_selections:
            select_file()
        else:
            file_path = os.path.abspath(os.path.join(FILES, files[selection - 1]))
    except ValueError:
        select_file()

    return file_path


if __name__ == "__main__":
    import pickle
    init()
    starting_url = 'https://www.ruralhealthinfo.org'
    scrapes = recursive_scrape(starting_url)
    scrapes.to_pickle("./ruralhealthinfo")
    
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt3.5-turbo"))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=1024)

    docs = GPTSimpleVectorIndex.from_documents(scrapes['text'], service_context=service_context)
    docs.query("What is the most important tool a rural community can do to prepare for risk of flooding?")

