# admin_tools.py
# Tools for admin to view, answer, and manage pending FAQ queries
# Usage: python admin_tools.py

import sqlite3
from datetime import datetime, timezone
import smtplib
from email.message import EmailMessage
import traceback

DB_FILE = "db.sqlite"

# ===============================
# Configuration - set admin creds here
# ===============================
ADMIN_EMAIL = "krrish.singh06@gmail.com"
ADMIN_APP_PASSWORD = "pljmzndewxvqvhuf"   # App password (use env vars in production)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
DEBUG = False   # Set True temporarily for detailed SMTP logs
# ===============================


# ===============================
# 📋 VIEW ALL PENDING QUERIES
# ===============================
def view_pending_queries():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, question, email, created_at FROM pending_queries")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("✅ No pending queries! All caught up.")
        return []

    print("\n--- Pending Queries ---")
    for r in rows:
        print(f"ID: {r[0]}\nQuestion: {r[1]}\nEmail: {r[2]}\nAsked at: {r[3]}")
        print("-" * 40)
    return rows


# ===============================
# ✉️ SEND EMAIL FUNCTION
# ===============================
def send_email(to_email: str, subject: str, body: str, debug: bool = False):
    """
    Send an email reply using Gmail SMTP (STARTTLS).
    to_email: recipient address (string)
    subject: email subject (string)
    body: plain-text body (string)
    debug: if True, prints SMTP exchange
    """
    if not to_email:
        return False, "No recipient email provided."

    msg = EmailMessage()
    msg["From"] = ADMIN_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    server = None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        if debug or DEBUG:
            server.set_debuglevel(1)
            print("DEBUG: SMTP connection opened.")
            print("DEBUG: msg['From'] repr:", repr(msg['From']))
            print("DEBUG: recipient repr:", repr(to_email))

        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(ADMIN_EMAIL, ADMIN_APP_PASSWORD)
        server.send_message(msg)

        if debug or DEBUG:
            print(f"DEBUG: Email sent to {to_email}")
        return True, f"Email sent to {to_email}"

    except smtplib.SMTPAuthenticationError as e:
        # Typical cause: wrong password or need App Password / blocked sign-in
        server_resp = getattr(e, "smtp_error", e)
        if debug or DEBUG:
            traceback.print_exc()
        return False, ("Authentication failed. Check ADMIN_APP_PASSWORD or create an App Password "
                       "if 2FA is enabled. Server response: " + str(server_resp))
    except smtplib.SMTPException as e:
        if debug or DEBUG:
            traceback.print_exc()
        return False, f"SMTP error: {e}"
    except Exception as e:
        if debug or DEBUG:
            traceback.print_exc()
        return False, f"Unexpected error: {type(e).__name__}: {e}"
    finally:
        if server:
            try:
                server.quit()
            except:
                pass


# ===============================
# 📤 REPLY TO A QUERY
# ===============================
def reply_to_query(pending_id: int, answer: str, debug: bool = False):
    """
    pending_id: ID of the pending query from view_pending_queries()
    answer: text answer to be added to FAQ and emailed
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Get the query details
    cur.execute("SELECT question, email FROM pending_queries WHERE id=?", (pending_id,))
    row = cur.fetchone()

    if not row:
        print("❌ No pending query found with that ID.")
        conn.close()
        return

    question, user_email = row

    # Insert into FAQ table
    cur.execute(
        "INSERT INTO faq (question, answer) VALUES (?, ?)",
        (question, answer)
    )

    # Remove from pending table
    cur.execute("DELETE FROM pending_queries WHERE id=?", (pending_id,))

    conn.commit()
    conn.close()

    print(f"✅ '{question}' has been added to FAQs and removed from pending queries.")

    # Send email (if user provided an email)
    if user_email:
        subject = f"Reply to your FAQ: {question}"
        body = (
            f"Hello,\n\nHere’s the answer to your question:\n\n"
            f"Q: {question}\nA: {answer}\n\n— Your FAQ Bot Admin"
        )
        ok, msg = send_email(user_email, subject, body, debug=debug)
        if ok:
            print(f"📧 Email sent to {user_email}")
        else:
            print(f"⚠️ Could not send email: {msg}")
    else:
        print("⚠️ No email found for this pending query; nothing was sent.")


# ===============================
# 🧠 SIMPLE COMMAND INTERFACE
# ===============================
def main():
    print("Admin Tools for FAQ Bot\n")
    print("1️⃣ View all pending queries")
    print("2️⃣ Reply to a query (auto-add to FAQ + remove + email)")

    choice = input("\nEnter option (1 or 2): ").strip()

    if choice == "1":
        view_pending_queries()
    elif choice == "2":
        try:
            pid_raw = input("Enter pending query ID to reply: ").strip()
            pid = int(pid_raw)
        except ValueError:
            print("❌ Invalid ID. Must be an integer.")
            return

        ans = input("Enter your answer: ").strip()
        if not ans:
            print("❌ Answer cannot be empty.")
            return

        # Ask whether to enable debug for this send (useful for diagnosing SMTP)
        dbg_choice = input("Enable SMTP debug for this send? (y/N): ").strip().lower()
        debug_flag = dbg_choice == "y"

        reply_to_query(pid, ans, debug=debug_flag)
    else:
        print("❌ Invalid option.")


if __name__ == "__main__":
    main()