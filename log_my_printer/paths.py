# log_my_printer/paths.py
from pathlib import Path
from typing import Any, Dict, TypeVar

from appdirs import user_config_dir
from pydantic import BaseModel

from . import app_name

_PathsType = TypeVar("_PathsType", bound="Paths")


class Paths(BaseModel):
    working_dir: Path
    home_dir: Path
    config_dir: Path
    config: Path

    def model_post_init(self, *args: Any, **kwargs: Any) -> None:
        self.config.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _defaults_paths(cls, working_dir: Path) -> Dict[str, Path]:
        working_dir = working_dir.resolve()
        home_dir: Path = Path.home()
        config_dir = Path(user_config_dir(appname=app_name, appauthor=""))
        config = config_dir / "config.yml"
        return {
            "working_dir": working_dir,
            "home_dir": home_dir,
            "config_dir": config_dir,
            "config": config,
        }

    @classmethod
    def from_defaults(cls, working_dir: Path) -> "Paths":
        cls._defaults_paths(working_dir)
        return cls(**cls._defaults_paths(working_dir))
