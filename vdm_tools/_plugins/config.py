from dataclasses import dataclass


@dataclass
class PluginConfig:
    name: str
    creator: str
    runtime: str
    description: str
    alias: str = ""
