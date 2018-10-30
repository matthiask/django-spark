from django.core.mail import EmailMessage

from spark.spark_mails.models import Mail


def process_mail_events(iterable, *, defaults=None, fail_silently=False):
    mails = {m.event_group: m for m in Mail.objects.all()}

    for e in iterable:
        if "spark_mail" not in e["context"]:
            continue
        kwargs = dict(defaults) if defaults else {}
        kwargs.update(e["context"]["spark_mail"])
        if e["group"] in mails:
            # TODO What about invalid templates? (They should not be saveable, but...)
            subject, body = mails[e["group"]].render(e["context"])
            if subject:
                kwargs["subject"] = subject
            if body:
                kwargs["body"] = body
        EmailMessage(**kwargs).send(fail_silently=fail_silently)
