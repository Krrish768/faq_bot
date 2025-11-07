# bot.py
# FAQ Bot: normalization, tokenization, Jaccard matching with SQLite storage
# Replace your current bot.py with this file.

import string
import re
import sqlite3
import datetime
from typing import List, Tuple, Optional
from datetime import datetime, UTC

# Toggle debug prints that show ORIGINAL / NORMALIZED / TOKENS (like your screenshot)
DEBUG = True

# small stopword list to ignore very common words (helps matching)
STOPWORDS = {
    "a", "an", "the", "is", "are", "to", "of", "in", "on", "for", "how", "do", "i", "my",
    "and", "with", "by", "from", "be", "this", "that", "it", "we", "you", "your"
}

# add near STOPWORDS/CONTRACTIONS
SYNONYMS = {
    # ==== ACCOUNT & LOGIN ====
    "signup": "create",
    "sign-up": "create",
    "sign": "create",
    "register": "create",
    "registration": "create",
    "create": "create",
    "make": "create",
    "open": "create",
    "login": "log",
    "log-in": "log",
    "logon": "log",
    "signin": "log",
    "sign-in": "log",
    "logout": "log",
    "log-out": "log",
    "account": "account",
    "profile": "account",
    "reactivate": "activate",
    "activate": "activate",
    "deactivate": "delete",
    "remove": "delete",
    "delete": "delete",
    "close": "delete",

    # ==== PASSWORD ====
    "reset": "change",
    "update": "change",
    "change": "change",
    "modify": "change",
    "forgot": "reset",
    "recover": "reset",

    # ==== ORDER & DELIVERY ====
    "buy": "order",
    "purchase": "order",
    "place": "order",
    "cancelled": "cancel",
    "cancellation": "cancel",
    "canceling": "cancel",
    "cancel": "cancel",
    "track": "track",
    "tracking": "track",
    "shipment": "delivery",
    "shipping": "delivery",
    "deliver": "delivery",
    "delivery": "delivery",
    "reschedule": "change",
    "slot": "delivery",
    "modify": "change",
    "status": "track",
    "order": "order",

    # ==== PAYMENT & BILLING ====
    "payment": "payment",
    "payments": "payment",
    "method": "payment",
    "mode": "payment",
    "gateway": "payment",
    "transaction": "payment",
    "checkout": "payment",
    "billing": "payment",
    "pay": "payment",
    "paid": "payment",
    "upi": "payment",
    "paytm": "payment",
    "googlepay": "payment",
    "gpay": "payment",
    "netbanking": "payment",
    "card": "payment",
    "creditcard": "payment",
    "debitcard": "payment",
    "wallet": "wallet",
    "balance": "wallet",

    # ==== REFUND / RETURN ====
    "refund": "refund",
    "refunded": "refund",
    "refunding": "refund",
    "return": "return",
    "replace": "return",
    "replacement": "return",
    "exchange": "return",
    "damaged": "return",
    "defective": "return",
    "broken": "return",

    # ==== EMAIL / COMMUNICATION ====
    "mail": "email",
    "emails": "email",
    "e-mail": "email",
    "email": "email",
    "message": "email",
    "notification": "notification",
    "notifications": "notification",
    "push": "notification",
    "alert": "notification",

    # ==== SUPPORT / CONTACT ====
    "help": "support",
    "support": "support",
    "customer": "support",
    "technical": "support",
    "service": "support",
    "assistance": "support",
    "query": "question",
    "question": "question",
    "issue": "problem",
    "problem": "problem",
    "bug": "problem",
    "error": "problem",
    "report": "problem",
    "contact": "support",
    "call": "support",
    "chat": "support",

    # ==== APP & WEBSITE ====
    "app": "application",
    "application": "application",
    "software": "application",
    "mobile": "application",
    "site": "website",
    "web": "website",
    "page": "website",
    "website": "website",
    "browser": "website",
    "install": "download",
    "installation": "download",
    "download": "download",
    "update": "update",
    "upgrade": "update",
    "installing": "download",

    # ==== MEMBERSHIP / REWARD ====
    "membership": "membership",
    "member": "membership",
    "join": "membership",
    "subscribe": "membership",
    "subscription": "membership",
    "unsubscribe": "membership",
    "reward": "points",
    "rewards": "points",
    "points": "points",
    "coins": "points",
    "credits": "points",
    "coupon": "coupon",
    "coupons": "coupon",
    "voucher": "coupon",
    "promo": "coupon",
    "discount": "coupon",

    # ==== GENERAL VERBS & ACTIONS ====
    "see": "view",
    "view": "view",
    "check": "view",
    "look": "view",
    "find": "view",
    "show": "view",
    "see": "view",
    "know": "view",
    "get": "view",
    "see": "view",
    "add": "add",
    "apply": "add",
    "use": "add",
    "enter": "add",
    "input": "add",
    "submit": "add",
    "upload": "add",
    "fill": "add",
    "type": "add",

    # ==== DELIVERY / TIME ====
    "time": "duration",
    "day": "duration",
    "days": "duration",
    "soon": "duration",
    "when": "duration",
    "howlong": "duration",
    "deliverytime": "duration",
    "delay": "duration",

    # ==== DEVICE & SETTINGS ====
    "settings": "settings",
    "preferences": "settings",
    "options": "settings",
    "language": "settings",
    "notification": "settings",
    "permissions": "settings",

    # ==== MISC ====
    "safe": "secure",
    "security": "secure",
    "privacy": "secure",
    "data": "secure",
    "information": "secure",
    "policy": "policy",
    "terms": "policy",
    "conditions": "policy",
    "rules": "policy",
    "procedure": "process",
    "process": "process",
    "steps": "process",
    "instructions": "process",
    "guide": "process",
    "enable": "activate",
    "activation": "activate",
    "2fa": "authentication",
    "twofactor": "authentication",
    "security": "authentication",

}



# contraction replacements (we'll handle some explicit forms first)
CONTRACTIONS = {
    "can't": "cannot",
    "won't": "will not",
    "i'm": "i am",
    "it's": "it is",
    "you're": "you are",
    "we're": "we are",
    "they're": "they are",
    "ain't": "is not",
    # suffix-style handled programmatically below: n't -> not, 're -> are, etc.
}

DB_FILE = "db.sqlite"
MATCH_THRESHOLD = 0.45  # tune as needed (0.3-0.6 common range)

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def apply_contractions(text: str) -> str:
    """
    Expand common contractions. Do replacements on a lowercased copy before removing punctuation.
    """
    s = text.lower()
    # explicit full contractions first
    for k, v in CONTRACTIONS.items():
        if k in s:
            s = s.replace(k, v)
    # handle suffix-like contractions (n't, 're, 's, 'd, 'll, 've)
    suffix_map = {
        "n't": " not",
        "'re": " are",
        "'s": " is",
        "'d": " would",
        "'ll": " will",
        "'ve": " have",
    }
    for suf, exp in suffix_map.items():
        if suf in s:
            s = s.replace(suf, exp)
    return s


def normalize_text(text: Optional[str]) -> str:
    """
    Lowercase, expand contractions, remove punctuation (replace with spaces),
    collapse whitespace and trim.
    Returns cleaned string.
    """
    if text is None:
        return ""
    s = apply_contractions(text)
    # replace punctuation characters with spaces (so words stay separated)
    trans = str.maketrans(string.punctuation, " " * len(string.punctuation))
    s = s.translate(trans)
    # collapse multiple whitespace to single space
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize(text: Optional[str]) -> List[str]:
    """
    Turn normalized text into a list of tokens (words), removing stopwords.
    Then map tokens through SYNONYMS to canonical forms.
    """
    norm = normalize_text(text)
    if not norm:
        return []
    tokens = [t for t in norm.split(" ") if t and t not in STOPWORDS]

    # map synonyms to canonical token (preserve token if not in map)
    mapped = [SYNONYMS.get(t, t) for t in tokens]

    # optional: remove duplicates while preserving order if you want lists without repeats
    # seen = set(); unique = []
    # for t in mapped:
    #     if t not in seen:
    #         unique.append(t); seen.add(t)
    # return unique

    return mapped



def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Compute Jaccard similarity between two sets of tokens: |A ∩ B| / |A ∪ B|.
    Returns float between 0 and 1.
    """
    if not set1 or not set2:
        return 0.0
    inter = set1.intersection(set2)
    uni = set1.union(set2)
    return len(inter) / len(uni)


def ensure_db_and_tables(db_path: str = DB_FILE) -> None:
    """
    Ensure that the DB file has the tables we rely on. If they already exist this is a no-op.
    Tables:
      - faq(id INTEGER PRIMARY KEY, question TEXT, answer TEXT)
      - pending_queries(id INTEGER PRIMARY KEY, question TEXT, email TEXT, created_at TEXT)
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS faq (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   question TEXT NOT NULL,
                   answer TEXT NOT NULL
               )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS pending_queries (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   question TEXT NOT NULL,
                   email TEXT,
                   created_at TEXT
               )"""
        )
        conn.commit()
    finally:
        conn.close()


def load_faqs_from_db(db_path: str = DB_FILE) -> List[Tuple[int, str, str]]:
    """
    Return list of (id, question, answer). Empty list if none or DB error.
    """
    ensure_db_and_tables(db_path)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, question, answer FROM faq")
        rows = cur.fetchall()
    except Exception:
        rows = []
    finally:
        conn.close()
    return rows


def find_best_match_in_db(user_question: str, db_path: str = DB_FILE) -> Tuple[Optional[Tuple[int, str, str]], float]:
    """
    Given a user question string, return (best_row, score) where best_row is (id,question,answer)
    or (None, 0.0) if no faqs exist or none matched. Score is Jaccard similarity.
    """
    token_user = set(tokenize(user_question))
    if DEBUG:
        print("ORIGINAL:", user_question)
        print("NORMALIZED:", normalize_text(user_question))
        print("TOKENS:", token_user)
        print("-" * 40)
    faqs = load_faqs_from_db(db_path)
    best_row = None
    best_score = 0.0
    for row in faqs:
        qid, qtext, qans = row
        tokens_q = set(tokenize(qtext))
        score = jaccard_similarity(token_user, tokens_q)
        if score > best_score:
            best_score = score
            best_row = row
    return best_row, best_score


def is_valid_email(email: Optional[str]) -> bool:
    """Very small email validation via regex; accepts typical addresses."""
    if not email:
        return False
    return EMAIL_REGEX.match(email.strip()) is not None


def insert_pending(question: str, email: str = "", db_path: str = DB_FILE) -> bool:
    """Insert a pending query into the pending_queries table. Returns True on success."""
    ensure_db_and_tables(db_path)
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO pending_queries (question, email, created_at) VALUES (?, ?, ?)",
            (question, email or None, datetime.now(UTC).isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def print_intro():
    print("FAQ Bot (type 'quit' or 'exit' to stop)\n")


def main_loop():
    print_intro()
    while True:
        try:
            user_q = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBot: Bye!")
            break

        if not user_q:
            continue
        if user_q.lower() in ("quit", "exit"):
            print("Bot: Bye!")
            break

        best_row, score = find_best_match_in_db(user_q)
        if best_row and score >= MATCH_THRESHOLD:
            # best_row is (id, question, answer)
            print("Bot:", best_row[2])
        else:
            print("Bot: I don't have a confident answer for that.")
            # ask for email
            try:
                email = input("Bot: Can I have your email so admin can reply? (leave blank to skip) ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nBot: No email provided. Question not saved.")
                continue

            if not email:
                print("Bot: No email provided. Question not saved.")
                continue

            if not is_valid_email(email):
                print("Bot: That doesn't look like a valid email. Question not saved.")
                continue

            ok = insert_pending(user_q, email)
            if ok:
                print("Bot: Thanks — your question has been saved for admin review.")
            else:
                print("Bot: Sorry, there was an error saving your question. Try again later.")


if __name__ == "__main__":
    # ensure db exists and tables present (safe no-op if already there)
    ensure_db_and_tables(DB_FILE)
    main_loop()
