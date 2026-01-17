import re
import spacy
from nlp_modules.document_ingestion import run_document_ingestion

nlp = None

def keyword_extraction_pipeline(pdf_path, top_k=10):
    global nlp

    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

    text = run_document_ingestion(pdf_path)
    if not text or "Error" in text:
        return []

    # basic cleaning (do NOT remove meaning)
    text = re.sub(r"\s+", " ", text)

    doc = nlp(text)

    keywords = set()

    # noun phrases
    for chunk in doc.noun_chunks:
        phrase = chunk.text.lower().strip()
        if len(phrase.split()) > 1 and len(phrase) > 4:
            keywords.add(phrase)

    # named entities
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE", "DATE", "EVENT"]:
            keywords.add(ent.text.lower())

    # remove noisy words
    blacklist = {
        "this type", "the way", "a human", "all aspects",
        "one of the", "such as", "in daily life"
    }

    clean_keywords = [
        kw for kw in keywords
        if not any(bad in kw for bad in blacklist)
    ]

    return clean_keywords[:top_k]
