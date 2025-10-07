# load a specific section or load the entire yaml config file
def load_config(config_path: str, section: str | None = None) -> dict:
    import yaml
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config.get(section, config) if section else config
