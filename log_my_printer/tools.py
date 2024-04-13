from multiprocessing.pool import ThreadPool
from typing import TYPE_CHECKING, Callable

import yaml
from pydantic import ValidationError

if TYPE_CHECKING:
    from tkinter import ttk

from log_my_printer.paths import Paths
from log_my_printer.smtp2go import EmailConfig


class RepeatingTimer:
    def __init__(
        self,
        interval: int,
        frame: "ttk.Frame",
        function: Callable[[], bool],
    ) -> None:
        """Crée un objet en charge de répéter une fonction à intervalle régulier

        Args:
            interval (int): Intervalle de répétition en secondes
            frame (tk.Frame): Frame parente
            function (Callable[[], None]): Fonction à exécuter
        """
        self._interval = interval * 1000
        self._frame = frame
        self._function = function
        self._continue_run = False

    def _run(self) -> None:
        if self._continue_run:
            pool = ThreadPool(processes=1)
            async_result = pool.apply_async(self._function)
            error = async_result.get()
            if error:
                self._frame.after(self._interval * 60, self._run)
            else:
                self._frame.after(self._interval, self._run)

    def start(self) -> None:
        self._continue_run = True
        self._run()

    def stop(self) -> None:
        self._continue_run = False


def get_email_config(paths: Paths) -> EmailConfig:
    if not paths.config.exists():
        return reset_config_file(paths)
    else:
        try:
            return EmailConfig(**yaml.safe_load(paths.config.read_text()))
        except ValidationError:
            return reset_config_file(paths)


def reset_config_file(paths: Paths) -> EmailConfig:
    email_config = EmailConfig(sender="", to=[], api_key="")
    with paths.config.open("w") as f:
        yaml.safe_dump(email_config.model_dump(), f)
    return email_config
