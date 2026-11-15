from dataclasses import dataclass


@dataclass
class Record:
    command: str
    platform: str
    description: str
    example_task: str
    example_command: str
    source_url: str