import logging
import os
from typing import TextIO

import requests


def generateWebhook(
    console_log: bool,
    webhook_log: bool
) -> logging.StreamHandler:
  
  class WebhookStream(logging.StreamHandler):
    
    def emit(self, record: logging.LogRecord) -> None:
      try:
        msg = self.format(record)
        stream: TextIO = self.stream
        if console_log:
          stream.write(msg + self.terminator)
        if webhook_log:
          requests.post(os.environ["WBHK_URL"], json={ "content": msg })
        self.flush()
      except Exception:
        self.handleError(record)
  
  format_string = "`%(name)s : %(levelname)s - %(message)s`"
  handler = WebhookStream()
  handler.setFormatter(logging.Formatter(format_string))
  return handler
