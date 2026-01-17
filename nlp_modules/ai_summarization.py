import PyPDF2
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------------- GLOBAL CACHE ----------------
tokenizer = None
model = None


def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        model_name = "sshleifer/distilbart-cnn-12-6"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PyPDF2.PdfReader(pdf_path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text.strip()


def chunk_text(text, chunk_size=450):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


def ai_summarization_pipeline(pdf_path):
    """
    FINAL AI Summarization Pipeline
    - Short documents → aggressive compression
    - Long documents → chunk + global summary
    """

    load_model()

    text = extract_text_from_pdf(pdf_path)
    if not text:
        return "No readable text found in the PDF."

    word_count = len(text.split())

    # ---------------- SHORT DOCUMENT ----------------
    if word_count < 400:
        inputs = tokenizer.encode(
            text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )

        summary_ids = model.generate(
            inputs,
            max_length=70,
            min_length=30,
            num_beams=6,
            length_penalty=3.0,
            no_repeat_ngram_size=3,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

        return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # ---------------- LONG DOCUMENT ----------------
    chunks = chunk_text(text)
    chunk_summaries = []

    for chunk in chunks:
        inputs = tokenizer.encode(
            chunk,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )

        summary_ids = model.generate(
            inputs,
            max_length=110,
            min_length=45,
            num_beams=4,
            length_penalty=2.0,
            no_repeat_ngram_size=3
        )

        chunk_summaries.append(
            tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        )

    # ---------------- FINAL GLOBAL SUMMARY ----------------
    combined_text = " ".join(chunk_summaries)

    inputs = tokenizer.encode(
        combined_text,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )

    final_ids = model.generate(
        inputs,
        max_length=130,
        min_length=55,
        num_beams=4,
        length_penalty=2.5,
        no_repeat_ngram_size=3
    )

    return tokenizer.decode(final_ids[0], skip_special_tokens=True)
