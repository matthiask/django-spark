import logging

from django.core.mail import EmailMultiAlternatives

from spark.spark_mails.models import Mail


logger = logging.getLogger(__name__)


def process_mail_events(iterable, *, defaults=None, fail_silently=False):
    for mail in mails_from_events(iterable, defaults=defaults):
        mail.send(fail_silently=fail_silently)


def mails_from_events(iterable, *, defaults=None, mails=None):
    mails = Mail.objects.as_mails() if mails is None else mails
    defaults = {} if defaults is None else defaults

    for e in iterable:
        if "spark_mail" not in e["context"]:
            continue
        kwargs = {**defaults, **e["context"]["spark_mail"]}
        if e["group"] in mails:
            try:
                kwargs = mails[e["group"]].render(e["context"], **kwargs)
            except Exception:
                logger.exception("Error while rendering mail subject and body")
        yield EmailMultiAlternatives(**kwargs)
