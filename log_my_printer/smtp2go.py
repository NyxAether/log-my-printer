import os
import sys
from pathlib import Path
from typing import List

import requests
import yaml
from pydantic import BaseModel


class EmailConfig(BaseModel):
    sender: str
    to: List[str]
    api_key: str


class Email(BaseModel):
    subject: str
    text_body: str


class SMTP2GO:
    def __init__(self, config_path: Path) -> None:
        if "SMTP2GO_API_KEY" in os.environ:
            self._config = EmailConfig(
                sender=os.environ["SMTP2GO_SENDER"],
                to=os.environ["SMTP2GO_TO"].split(","),
                api_key=os.environ["SMTP2GO_API_KEY"],
            )
        elif config_path.exists():
            self._config = EmailConfig(**yaml.safe_load(config_path.read_text()))
        else:
            self._config = EmailConfig(
                sender="",
                to=[],
                api_key="",
            )
        # # Read environment variables
        self._api_url = "https://api.smtp2go.com/v3/email/send"

    def send_email(self, email: Email) -> None:
        response = requests.post(
            self._api_url, json=self._config.model_dump().update(email.model_dump())
        )
        if response.status_code != 200:
            print(f"Error while sending email: {response.text}", file=sys.stderr)
