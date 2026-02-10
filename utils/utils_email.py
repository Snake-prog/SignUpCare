import smtplib
import socket
import typing

from django.core import mail

from utils import utils_dto
from utils import utils_exceptions


class CommonEmailMessageDto(utils_dto.BaseDto):
    subject: str
    from_email: str
    to: typing.Iterable[str] | str
    attachments: list[tuple[str, bytes, str]] | None
    body: str


class EmailMessageSendingDto(CommonEmailMessageDto):
    headers: dict


class EmailMultiAlternativesDto(CommonEmailMessageDto):
    html_content: str = ""


NOT_ANY_SENT_MESSAGES = "Не было отправлено ни одного сообщения"


def email_multi_alternatives__send(
        *,
        message_data_dto: EmailMultiAlternativesDto,
        content_type: str = "text/html",
        connection: typing.Any | None = None,
) -> int:
    message_data = message_data_dto.model_dump()
    if not message_data_dto.attachments:
        message_data.pop("attachments")
    if connection:
        message_data["connection"] = connection
    html_content = message_data.pop("html_content", "")
    try:
        email_message = mail.EmailMultiAlternatives(**message_data)
        email_message.attach_alternative(html_content, content_type)
        email_messages_count = email_message.send()
        if not email_messages_count:
            raise utils_exceptions.BusinessLogicException(NOT_ANY_SENT_MESSAGES)
        return email_messages_count

    except (
            smtplib.SMTPServerDisconnected,
            smtplib.SMTPDataError,
            socket.gaierror,
    ) as error:
        raise utils_exceptions.BusinessLogicException(f"{error}")
