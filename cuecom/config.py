"""Repository paths shared by every cuecom module.

Modules read `ROOT`. Code that runs against another checkout or a temporary folder (tests, tools)
builds its own `Settings(root)` and passes the root down.
"""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    root: Path = ROOT

    @property
    def config_dir(self):
        return self.root / 'config'

    @property
    def data_dir(self):
        return self.root / 'data'

    @property
    def models_dir(self):
        return self.root / 'models'

    def session_home(self, profile='default'):
        """Ignored private folder for one profile's packets, motifs and trace."""
        return self.root / '.scratch_session' / profile


settings = Settings()
