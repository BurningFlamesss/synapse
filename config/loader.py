from pathlib import Path
from typing import Any
from platformdirs import user_config_dir
import tomli
from config.config import Config
from utils.errors import ConfigError
import logging

logger = logging.getLogger(__name__)
CONFIG_FILE_NAME = "synapse_config.toml"
SYNAPSE_MD_FILE = "SYNAPSE.MD"

def get_config_dir() -> Path:
    return Path(user_config_dir("synapse"))

def get_system_config_path() -> Path:
    return get_config_dir() / CONFIG_FILE_NAME

def _parse_toml(path: Path):
    try:
        with open(path, "rb") as f:
            return tomli.load(f)
    except tomli.TOMLDecodeError as e:
        raise ConfigError("Invalid TOML in {path}: {e}", config_file=str(path)) from e
    except (OSError, IOError) as e:
        raise ConfigError("Failed to read synapse_config file {path}: {e}", config_file=str(path)) from e 
    
def _get_project_config(cwd: Path) -> Path | None:
    current = cwd.resolve()
    synapse_dir = current / ".synapse"
    
    if synapse_dir.is_dir():
        config_file = synapse_dir / CONFIG_FILE_NAME
        if config_file.is_file():
            return config_file
        
    return None
    
def _get_synapse_md_files(cwd: Path) -> Path | None:
    current = cwd.resolve()
    
    if current.is_dir():
        synapse_md_file = current / SYNAPSE_MD_FILE
        if synapse_md_file.is_file():
            content = synapse_md_file.read_text(encoding="utf-8")
            return content
        
    return None

def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value
            
    return result

def load_config(cwd: Path | None) -> Config:
    cwd = cwd or Path.cwd()
    
    system_path = get_system_config_path()
    
    config_dict: dict[str, Any] = {}
    
    if system_path.is_file():
        try:
            config_dict = _parse_toml(system_path)
        except ConfigError:
            logger.warning(f"Skipping the invalid system config: {system_path}")
    
    project_path = _get_project_config(cwd)
    
    if project_path:
        try:
            project_config_dict = _parse_toml(project_path)
            config_dict = _merge_dicts(config_dict, project_config_dict)
        except:
            logger.warning(f"Skipping the invalid system config: {system_path}")
            
    if "cwd" not in config_dict:
        config_dict["cwd"] = cwd
        
    if "developer_instructions" not in config_dict:
        synapse_md_content = _get_synapse_md_files(cwd)
        if synapse_md_content:
            config_dict["developer_instructions"] = synapse_md_content
            
    try:
        config = Config(**config_dict)
    except Exception as e:
        raise ConfigError(f"Invalid configuration: {e}") from e
    
    return config