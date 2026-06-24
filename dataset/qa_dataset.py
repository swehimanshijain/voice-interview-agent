import json

with open("dataset/qa_dataset.json", "r", encoding="utf-8") as file:
    QUESTIONS = json.load(file)