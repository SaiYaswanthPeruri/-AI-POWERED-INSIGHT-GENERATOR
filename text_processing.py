# text_processing.py
import nltk
import spacy
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

nlp = spacy.load("en_core_web_sm")
nltk.download(['punkt', 'stopwords', 'wordnet'])

def extract_quality_keywords(text, top_n=20):
    doc = nlp(text)
    nouns = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'PROPN'] and token.is_alpha]
    verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB' and token.is_alpha]
    
    words = nouns + verbs
    words = [w for w in words if len(w) > 2 and w not in stopwords.words('english')]
    
    word_counts = Counter(words)
    unique_words = []
    seen_lemmas = set()
    
    for word, count in word_counts.most_common(top_n*3):
        lemma = nlp(word)[0].lemma_
        if lemma not in seen_lemmas:
            unique_words.append((word, count))
            seen_lemmas.add(lemma)
            if len(unique_words) >= top_n:
                break
    
    return [w[0] for w in unique_words]

def improved_summarize(text, word_count=50):
    sentences = sent_tokenize(text)
    if len(sentences) < 2:
        return text[:500], len(word_tokenize(text[:500]))
    
    keywords = set(extract_quality_keywords(text, 15))
    sentence_scores = {}
    
    for i, sentence in enumerate(sentences):
        score = 0
        words = word_tokenize(sentence.lower())
        score += sum(1 for word in words if word in keywords)
        score += 0.5 * (1 - i/len(sentences))
        sentence_scores[sentence] = score
    
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    summary = []
    total_words = 0
    
    for sentence, _ in sorted_sentences:
        words_in_sentence = len(word_tokenize(sentence))
        if total_words + words_in_sentence <= word_count:
            summary.append(sentence)
            total_words += words_in_sentence
        else:
            break
    
    return ' '.join(summary), total_words