# check_db.py
from bot import load_faqs_from_db, normalize_text, tokenize, jaccard_similarity

user_q = "how do i reset my password?"

faqs = load_faqs_from_db()
if not faqs:
    print("No rows in faq table.")
else:
    print(f"Comparing user question: {user_q!r}\n")
    user_tokens = set(tokenize(user_q))
    for qid, qtext, answer in faqs:
        norm = normalize_text(qtext)
        tokens = set(tokenize(qtext))
        score = jaccard_similarity(user_tokens, tokens)
        print(f"ID: {qid}")
        print("QUESTION:", qtext)
        print("  NORMALIZED:", norm)
        print("  TOKENS:", tokens)
        print(f"  SCORE: {score:.3f}")
        print("  ANSWER:", answer)
        print("-" * 40)
