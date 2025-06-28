import pdfplumber
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import spacy
import os

# Load spaCy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

# ========== Step 1: Extract text from PDF ==========
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# ========== Step 2: Word frequency ==========
def get_word_frequencies(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())
    # Keep only alphabetic words and remove stopwords
    words = [word for word in words if word.isalpha() and word not in stop_words]
    return Counter(words)

def plot_frequencies(freq, top_n=20):
    os.makedirs("output", exist_ok=True)
    common = freq.most_common(top_n)
    words, counts = zip(*common)
    plt.figure(figsize=(10, 5))
    plt.bar(words, counts, color="skyblue")
    plt.title("Top Word Frequencies")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/frequency_plot.png")
    plt.close()

# ========== Step 3: Word cloud ==========
def create_wordcloud(freq):
    wc = WordCloud(width=800, height=400, background_color='white')
    wc.generate_from_frequencies(freq)
    wc.to_file("output/wordcloud.png")

# ========== Step 4: Named Entity Recognition ==========
def extract_named_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

# ========== Step 5: Summarize ==========
def summarize_text(text, num_sentences=5):
    sentences = sent_tokenize(text)
    freq = get_word_frequencies(text)
    scores = {}
    for sent in sentences:
        words = word_tokenize(sent.lower())
        scores[sent] = sum(freq.get(word, 0) for word in words)
    top_sents = sorted(scores, key=scores.get, reverse=True)[:num_sentences]
    summary = "\n".join(top_sents)
    with open("output/summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

# ========== Step 6: Main ==========
def main():
    pdf_path = "sample.pdf"
    os.makedirs("output", exist_ok=True)

    if not os.path.exists(pdf_path):
        print("sample.pdf not found. Please add a PDF to your folder.")
        return

    print(" Extracting text...")
    text = extract_text_from_pdf(pdf_path)

    # Save the full extracted text
    with open("output/full_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("Analyzing word frequencies...")
    freq = get_word_frequencies(text)
    plot_frequencies(freq)
    create_wordcloud(freq)

    print("Performing Named Entity Recognition...")
    entities = extract_named_entities(text)
    print("Top 10 Named Entities:")
    for ent, label in entities[:10]:
        print(f"{ent} ({label})")

    print(" Summarizing text...")
    summarize_text(text)

    print(" Done! Check the 'output' folder for your results.")

if __name__ == "__main__":
    main()
