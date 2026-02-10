def normalize_phone(
        *,
        phone: str
) -> str:
    import re
    regex = r"(\+7|7|8)?([\s\-]?\(?[1-9][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2})"
    phone = re.search(regex, phone)
    if phone:
        phone = '+7' + phone.group(2).replace(
            ' ', '').replace(
            '-', '').replace(
            ')', '').replace(
            '(', '')
    return str(phone)


def normalize_passport(
        *,
        passport: str
) -> str:
    import re
    regex = r'(\d{4})\s?(\d{6})'
    passport = re.search(regex, passport)
    if passport:
        passport = " ".join(passport.groups())
    return str(passport)


def normalize_policy(
        *,
        policy: str
) -> str:
    import re
    regex = r"(\d{4})\s?(\d{4})\s?(\d{4})\s?(\d{4})"
    policy = re.search(regex, policy)
    if policy:
        policy = " ".join(policy.groups())
    return str(policy)
