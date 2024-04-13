from datetime import datetime

import win32print as wp

from log_my_printer.smtp2go import SMTP2GO, Email


class PrinterManager:
    def __init__(self, emailer: SMTP2GO) -> None:
        self.emailer = emailer
        self.ERRORS = {
            # wp.PRINTER_STATUS_BUSY: "PRINTER_STATUS_BUSY",
            wp.PRINTER_STATUS_DOOR_OPEN: "PRINTER_STATUS_DOOR_OPEN",
            wp.PRINTER_STATUS_ERROR: "PRINTER_STATUS_ERROR",
            # wp.PRINTER_STATUS_INITIALIZING: "PRINTER_STATUS_INITIALIZING",
            # wp.PRINTER_STATUS_IO_ACTIVE: "PRINTER_STATUS_IO_ACTIVE",
            wp.PRINTER_STATUS_MANUAL_FEED: "PRINTER_STATUS_MANUAL_FEED",
            wp.PRINTER_STATUS_NO_TONER: "PRINTER_STATUS_NO_TONER",
            wp.PRINTER_STATUS_NOT_AVAILABLE: "PRINTER_STATUS_NOT_AVAILABLE",
            wp.PRINTER_STATUS_OFFLINE: "PRINTER_STATUS_OFFLINE",
            wp.PRINTER_STATUS_OUT_OF_MEMORY: "PRINTER_STATUS_OUT_OF_MEMORY",
            wp.PRINTER_STATUS_OUTPUT_BIN_FULL: "PRINTER_STATUS_OUTPUT_BIN_FULL",
            wp.PRINTER_STATUS_PAGE_PUNT: "PRINTER_STATUS_PAGE_PUNT",
            wp.PRINTER_STATUS_PAPER_JAM: "PRINTER_STATUS_PAPER_JAM",
            wp.PRINTER_STATUS_PAPER_OUT: "PRINTER_STATUS_PAPER_OUT",
            wp.PRINTER_STATUS_PAPER_PROBLEM: "PRINTER_STATUS_PAPER_PROBLEM",
            wp.PRINTER_STATUS_PAUSED: "PRINTER_STATUS_PAUSED",
            wp.PRINTER_STATUS_PENDING_DELETION: "PRINTER_STATUS_PENDING_DELETION",
            # wp.PRINTER_STATUS_POWER_SAVE: "PRINTER_STATUS_POWER_SAVE",
            # wp.PRINTER_STATUS_PRINTING: "PRINTER_STATUS_PRINTING",
            # wp.PRINTER_STATUS_PROCESSING: "PRINTER_STATUS_PROCESSING",
            wp.PRINTER_STATUS_SERVER_UNKNOWN: "PRINTER_STATUS_SERVER_UNKNOWN",
            wp.PRINTER_STATUS_TONER_LOW: "PRINTER_STATUS_TONER_LOW",
            wp.PRINTER_STATUS_USER_INTERVENTION: "PRINTER_STATUS_USER_INTERVENTION",
            # wp.PRINTER_STATUS_WAITING: "PRINTER_STATUS_WAITING",
            # wp.PRINTER_STATUS_WARMING_UP: "PRINTER_STATUS_WARMING_Up",
        }

    def check_printers(self, send_email: bool = True) -> bool:
        printer_names = [
            printer["pPrinterName"]
            for printer in wp.EnumPrinters(wp.PRINTER_ENUM_NAME, None, 2)
        ]
        for printer_name in printer_names:
            printer = wp.OpenPrinter(printer_name)
            status = wp.GetPrinter(printer, 6)["Status"]
            if status != 0:
                if send_email:
                    self._send_email(printer_name, self.ERRORS[status])
                else:
                    print(
                        f"{printer_name} a envoyé le code {self.ERRORS[status]} "
                        f"à {datetime.now().strftime('%H:%M:%S le %d-%m-%Y')}"
                    )
                return True
        return False

    def _send_email(self, printer_name: str, status: str) -> None:
        subject = f"Log my printer - {status}"
        text_body = (
            f"{printer_name} a envoyé le code {status} "
            f"à {datetime.now().strftime('%H:%M:%S le %d-%m-%Y')}"
        )
        self.emailer.send_email(Email(subject=subject, text_body=text_body))
