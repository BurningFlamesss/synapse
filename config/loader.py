from pathlib import Path
from platformdirs import user_config_dir
import tomli
from config.config import Config
from utils.errors import ConfigError

CONFIG_FILE_NAME = "synapse_config.toml"

def get_config_dir() -> Path:
    return Path(user_config_dir("synapse"))

def get_system_config_path() -> Path:
    return get_config_dir() / CONFIG_FILE_NAME

def _parse_toml(path: Path):
    try:
        with open(path, "rb") as f:
            return tomli
    except tomli.TOMLDecodeError as e:
        raise ConfigError("Invalid TOML in {path}: {e}", config_file=str(path)) from e
    except (OSError, IOError) as e:
        raise ConfigError("Failed to read synapse_config file {path}: {e}", config_file=str(path)) from e 

def load_config(cwd: Path | None) -> Config:
    cwd = cwd or Path.cwd()
    
    system_path = get_system_config_path()
    
    if system_path.is_file():
        pass
    
    