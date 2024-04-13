import tkinter as tk
from pathlib import Path
from tkinter import StringVar, ttk

import yaml

from log_my_printer.paths import Paths
from log_my_printer.printer_manager import PrinterManager
from log_my_printer.smtp2go import SMTP2GO, EmailConfig
from log_my_printer.tools import RepeatingTimer, get_email_config


def lauch_app() -> None:
    printlogger = App()
    printlogger.title("Log my printer")
    printlogger.mainloop()


class App(tk.Tk):
    def __init__(self) -> None:
        tk.Tk.__init__(self)
        self._paths = Paths.from_defaults(working_dir=Path.cwd())
        self._print_manager = PrinterManager(SMTP2GO(self._paths.config))
        self._frame: ttk.Frame | ttk.LabelFrame | None = None
        self.open_main()

    def open_main(self) -> None:
        if self._frame is not None:
            self._frame.destroy()
        self._frame = MainFrame(self, self._paths, self._print_manager)
        self._frame.tkraise()
        self._frame.pack()

    def open_config(self) -> None:
        if self._frame is not None:
            self._frame.destroy()
        self._frame = ConfigFrame(self, self._paths)
        self._frame.tkraise()
        self._frame.pack()


class MainFrame(ttk.Frame):
    def __init__(
        self, master: App, paths: Paths, print_manager: PrinterManager
    ) -> None:
        super().__init__(master)
        self.repeater = RepeatingTimer(60, self, print_manager.check_printers)
        self.repeater_no_email = RepeatingTimer(
            10, self, lambda: print_manager.check_printers(False)
        )

        self.start_b = ttk.Button(self, text="Démarrer", command=self._start)
        self.start_b.pack(side="left")
        self.start_alt_b = ttk.Button(
            self, text="Démarrer (sans email)", command=self._start_no_email
        )
        self.start_alt_b.pack(side="left")
        self.stop_b = ttk.Button(self, text="Stop", command=self._stop)
        self.stop_b.pack(side="left")
        self.config_b = ttk.Button(self, text="Configurer", command=master.open_config)
        self.config_b.pack(side="left")
        self.quit_b = ttk.Button(self, text="Quitter", command=master.quit)
        self.quit_b.pack(side="left")
        self.stop_b["state"] = "disabled"

    def _start(self) -> None:
        self.stop_b["state"] = "normal"
        self.start_b["state"] = "disabled"
        self.start_alt_b["state"] = "disabled"
        self.config_b["state"] = "disabled"
        self.repeater.start()

    def _start_no_email(self) -> None:
        self.stop_b["state"] = "normal"
        self.start_b["state"] = "disabled"
        self.start_alt_b["state"] = "disabled"
        self.config_b["state"] = "disabled"
        self.repeater_no_email.start()

    def _stop(self) -> None:
        self.stop_b["state"] = "disabled"
        self.start_b["state"] = "normal"
        self.start_alt_b["state"] = "normal"
        self.config_b["state"] = "normal"
        self.repeater.stop()
        self.repeater_no_email.stop()


class ConfigFrame(ttk.LabelFrame):
    def __init__(self, master: "App", paths: Paths) -> None:
        super().__init__(master, text="Configuration")
        self.paths = paths
        self.container = master
        email_config = get_email_config(paths)
        self.sender = StringVar(value=email_config.sender)
        self.to = StringVar(value=",".join(email_config.to))
        self.api_key = StringVar(value=email_config.api_key)

        ttk.Label(self, text="Émetteur").grid(row=0, column=0)
        ttk.Entry(self, textvariable=self.sender, width=50).grid(row=0, column=1)
        ttk.Label(self, text="Récepteur").grid(row=1, column=0)
        ttk.Entry(self, textvariable=self.to, width=50).grid(row=1, column=1)
        ttk.Label(self, text="Clef d'API").grid(row=2, column=0)
        ttk.Entry(self, textvariable=self.api_key, width=50).grid(row=2, column=1)

        ttk.Button(self, text="Enregistrer", command=self.save).grid(row=1, column=2)
        ttk.Button(self, text="Annuler", command=master.open_main).grid(row=2, column=2)

    def save(self) -> None:
        email_config = EmailConfig(
            sender=self.sender.get(),
            to=self.to.get().split(","),
            api_key=self.api_key.get(),
        )
        with self.paths.config.open("w") as f:
            yaml.safe_dump(email_config.model_dump(), f)
        self.container.open_main()

    def save_and_close(self) -> None:
        self.save()
        self.destroy()
