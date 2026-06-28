import resend

from app.config import settings

resend.api_key = settings.RESEND_API_KEY


async def send_verification_email(to_email: str, token: str) -> None:
    """Send an email verification link via Resend."""
    verify_url = f"{settings.FRONTEND_URL}/auth/verify?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: sans-serif; background: #0d0d1a; color: #ffffff; padding: 40px;">
      <div style="max-width: 480px; margin: 0 auto; background: #1a1a2e; border-radius: 12px; padding: 40px;">
        <h1 style="color: #f5a623; margin-top: 0;">🎌 IndoAnimeList</h1>
        <p style="color: #cccccc;">Thank you for joining IndoAnimeList — India's anime leaderboard.</p>
        <p style="color: #cccccc;">Click the button below to verify your email address:</p>
        <a href="{verify_url}"
           style="display: inline-block; background: #f5a623; color: #0d0d1a; padding: 12px 28px;
                  border-radius: 8px; text-decoration: none; font-weight: bold; margin: 16px 0;">
          Verify Email
        </a>
        <p style="color: #888888; font-size: 12px;">
          If you didn't create an account, you can safely ignore this email.<br>
          This link expires in 24 hours.
        </p>
        <hr style="border-color: #333355;">
        <p style="color: #555577; font-size: 11px;">IndoAnimeList — Crowdsourced anime ratings from India</p>
      </div>
    </body>
    </html>
    """

    resend.Emails.send({
        "from": f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>",
        "to": [to_email],
        "subject": "Verify your IndoAnimeList account",
        "html": html_content,
    })
