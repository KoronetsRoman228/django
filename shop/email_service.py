"""
Сервіс для надсилання листів у КактусShop.

Усі листи надсилаються у форматі HTML + текстова альтернатива.
"""

import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_welcome_email(subscriber):
    """
    Надсилає лист-привітання новому підписнику.
    Викликається одразу після підписки.
    """
    subject = '🌵 Ласкаво просимо до розсилки КактусShop!'
    from_email = getattr(settings, 'NEWSLETTER_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)

    html_content = render_to_string('shop/emails/welcome.html', {
        'subscriber': subscriber,
    })
    text_content = render_to_string('shop/emails/welcome.txt', {
        'subscriber': subscriber,
    })

    msg = EmailMultiAlternatives(subject, text_content, from_email, [subscriber.email])
    msg.attach_alternative(html_content, 'text/html')

    try:
        msg.send()
        logger.info('Welcome email sent to %s', subscriber.email)
        return True
    except Exception as exc:
        logger.error('Failed to send welcome email to %s: %s', subscriber.email, exc)
        return False


def send_campaign(campaign):
    """
    Надсилає кампанію всім активним підписникам.
    Повертає кількість успішно надісланих листів.
    """
    from .models import NewsletterSubscriber

    if campaign.is_sent:
        raise ValueError('Цю кампанію вже надіслано.')

    subscribers = NewsletterSubscriber.objects.filter(is_active=True)
    if not subscribers.exists():
        return 0

    from_email = getattr(settings, 'NEWSLETTER_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)

    # Якщо текстова версія не заповнена — генеруємо автоматично зі стриппінгом HTML
    text_body = campaign.body_text
    if not text_body:
        try:
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            text_body = h.handle(campaign.body_html)
        except ImportError:
            import re
            text_body = re.sub(r'<[^>]+>', '', campaign.body_html).strip()

    sent_count = 0
    for subscriber in subscribers:
        try:
            html_content = render_to_string('shop/emails/campaign.html', {
                'subscriber': subscriber,
                'campaign': campaign,
                'body_html': campaign.body_html,
            })
            text_content = render_to_string('shop/emails/campaign.txt', {
                'subscriber': subscriber,
                'campaign': campaign,
                'body_text': text_body,
            })

            msg = EmailMultiAlternatives(
                campaign.subject,
                text_content,
                from_email,
                [subscriber.email],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            sent_count += 1
            logger.info('Campaign "%s" sent to %s', campaign.subject, subscriber.email)
        except Exception as exc:
            logger.error('Failed to send campaign to %s: %s', subscriber.email, exc)

    # Позначаємо кампанію як надіслану
    campaign.is_sent = True
    campaign.sent_at = timezone.now()
    campaign.recipients_count = sent_count
    campaign.save(update_fields=['is_sent', 'sent_at', 'recipients_count'])

    return sent_count
