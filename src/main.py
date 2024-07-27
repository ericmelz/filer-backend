from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from typing import List
import openai
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = [
    'http://localhost:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")


class FileSuggestionRequest(BaseModel):
    fileName: str
    currentHierarchy: List[str]


@app.post("/upload/")
async def suggest_folder(request: FileSuggestionRequest):
    # response = openai.Completion.create(
    #     engine="davinci",
    #     prompt=f"Given the file name {request.fileName} and the current hierarchy {request.currentHierarchy}, suggest a folder to move the file to.",
    #     max_tokens=100
    # )

    suggested_folder = f'{request.fileName=}, {request.currentHierarchy=}'
    # suggested_folder = response.choices[0].text
    return {"suggestedFolder": suggested_folder}