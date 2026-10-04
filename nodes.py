
from html import escape
from email.message import EmailMessage
import os
import smtplib

from state import NewsState, Article, DeduplicationResult
from dotenv import load_dotenv
from news_fetchers.hackernews import fetch_news_using_hackernews_id
from llm import get_dedup_llm
from prompts.dedup_prompt import build_dedup_prompt


load_dotenv()




def fetch_news_from_hackernews_node(state: NewsState) -> dict:
    news_data: list[Article] | None = fetch_news_using_hackernews_id()
    print(f"Executed node: fetch_news_from_hackernews_node")
    return {"raw_articles": news_data} if news_data is not None else {"raw_articles": []}


def fetch_news_from_rss_node(state: NewsState) -> dict:
    pass


def fetch_news_from_github_node(state: NewsState) -> dict:
    pass


def fetch_news_from_reddit_node(state: NewsState) -> dict:
    pass


def deduplicate_news_node(state: NewsState) -> dict:
    dedup_llm = get_dedup_llm()
    prompt = build_dedup_prompt(state["raw_articles"])
    try:
        response: DeduplicationResult = dedup_llm.invoke(prompt)
        print(f"Executed node: deduplicate_news_node")
        return {"deduped_articles": response.articles}
    except Exception as e:
        print(f"Error occurred during deduplication: {e}")
        return {"deduped_articles": []}



def generate_email_body_node(state: NewsState) -> dict:
        articles = state.get("deduped_articles", [])
        article_cards = []

        for article in articles:
                title = escape(article.title)
                source = escape(article.source.upper())
                published_at = (
                        article.published_at.strftime("%b %d, %Y at %H:%M %Z")
                        if article.published_at
                        else "Date unavailable"
                )
                published_at = escape(published_at)

                if article.url:
                        url = escape(article.url, quote=True)
                        title_markup = (
                                f'<a href="{url}" style="color:#16324f;text-decoration:none;">'
                                f"{title}</a>"
                        )
                else:
                        title_markup = title

                article_cards.append(
                        f"""
                        <article style="padding:20px 0;border-bottom:1px solid #d9e2ec;">
                                <div style="font-size:12px;font-weight:700;letter-spacing:.08em;color:#6b7c93;">
                                        {source} &nbsp; | &nbsp; {published_at}
                                </div>
                                <h2 style="margin:8px 0 0;font-size:20px;line-height:1.35;font-weight:650;">
                                        {title_markup}
                                </h2>
                        </article>
                        """
                )

        if article_cards:
                content = "".join(article_cards)
                count_label = f"{len(articles)} stories"
        else:
                content = (
                        '<p style="margin:0;color:#526173;font-size:16px;line-height:1.6;">'
                        "No unique stories were found in this run.</p>"
                )
                count_label = "No stories"

        email_body = f"""
        <!doctype html>
        <html lang="en">
            <body style="margin:0;background:#eef3f7;color:#16324f;font-family:Arial,sans-serif;">
                <main style="max-width:680px;margin:0 auto;padding:32px 20px;">
                    <section style="background:#ffffff;border:1px solid #d9e2ec;border-radius:10px;padding:32px;">
                        <div style="font-size:12px;font-weight:700;letter-spacing:.12em;color:#3f7d8c;">
                            NEWS MANIA
                        </div>
                        <h1 style="margin:10px 0 6px;font-size:32px;line-height:1.15;">
                            Your daily news digest
                        </h1>
                        <p style="margin:0 0 20px;color:#6b7c93;font-size:15px;">
                            {count_label} after duplicate stories were removed.
                        </p>
                        {content}
                    </section>
                </main>
            </body>
        </html>
        """
        print(f"Generated email body with {len(articles)} articles.")
        return {"email_body": email_body}
    


def send_email_node(state: NewsState) -> dict:
    required_settings = (
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "EMAIL_FROM",
        "EMAIL_TO",
    )
    missing_settings = [name for name in required_settings if not os.getenv(name)]
    if missing_settings:
        return {"errors": f"Missing email configuration: {', '.join(missing_settings)}"}

    recipients = [
        address.strip()
        for address in os.environ["EMAIL_TO"].split(",")
        if address.strip()
    ]
    if not recipients:
        return {"errors": "EMAIL_TO does not contain a recipient"}

    message = EmailMessage()
    message["Subject"] = os.getenv("EMAIL_SUBJECT", "News Mania Daily Digest")
    message["From"] = os.environ["EMAIL_FROM"]
    message["To"] = ", ".join(recipients)
    message.set_content("Your News Mania digest is available in HTML format.")
    message.add_alternative(state.get("email_body", ""), subtype="html")

    try:
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = int(os.environ["SMTP_PORT"])
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
            smtp.send_message(message)
            print(f"Email sent successfully to: {', '.join(recipients)}")
    except (OSError, smtplib.SMTPException, ValueError) as error:
        return {"errors": f"Email sending failed: {error}"}

    return {"errors": ""}



def important_news_node(state: NewsState) -> dict:
    pass


def summarize_news_node(state: NewsState) -> dict:
    pass




