import re
import json


# Sensitive information patterns
SENSITIVE_PATTERNS = {

    "password": r'(?i)(password|passwd|pwd)\s*[:=]\s*[^\s,;]+',

    "api_key": r'(?i)(api[_-]?key)\s*[:=]\s*[^\s,;]+',

    "token": r'(?i)(access[_-]?token|auth[_-]?token)\s*[:=]\s*[^\s,;]+',

    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',

}


def redact_sensitive_data(text):

    redacted = text

    for category, pattern in SENSITIVE_PATTERNS.items():

        if category == "email":

            redacted = re.sub(
                pattern,
                "[EMAIL_REDACTED]",
                redacted
            )

        else:

            redacted = re.sub(
                pattern,
                lambda match: match.group(0).split(
                    match.group(0)[
                        :match.group(0).find("=")
                    ] if "=" in match.group(0) else
                    match.group(0)[
                        :match.group(0).find(":")
                    ]
                )[0] + "=[REDACTED]",
                redacted
            )

    return redacted


def create_safe_metadata(data):

    safe_data = {}

    for key, value in data.items():

        if isinstance(value, str):

            safe_data[key] = redact_sensitive_data(value)

        else:

            safe_data[key] = value

    return safe_data


if __name__ == "__main__":

    test_data = {

        "hostname": "server-01",

        "password": "password=admin123",

        "api_information": "api_key=ABC123XYZ",

        "user_email": "darshan@example.com",

        "cpu_usage": 95.5

    }

    print("\n===== CICADA PRIVACY FILTER =====")

    safe_data = create_safe_metadata(test_data)

    print(json.dumps(safe_data, indent=4))