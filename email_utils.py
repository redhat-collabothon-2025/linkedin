import time
import imaplib
import email
import re


def get_latest_otp(user: str, password: str, subject_filter: str, timeout: int = 60, poll_interval: int = 5,
                   ) -> str | None:
    end_time = time.time() + timeout

    while time.time() < end_time:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(user, password)
        mail.select("INBOX")

        typ, data = mail.search(None, f'(UNSEEN SUBJECT "{subject_filter}")')

        if data[0]:
            latest_id = data[0].split()[-1]
            typ, msg_data = mail.fetch(latest_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            body = msg.get_payload(decode=True).decode(errors="ignore")
            match = re.search(r"\b(\d{6})\b", body)
            if match:
                mail.logout()
                return match.group(1)

        mail.logout()
        time.sleep(poll_interval)
    return None
