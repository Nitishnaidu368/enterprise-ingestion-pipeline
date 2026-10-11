from dataclasses import dataclass


MetadataValue = str | int | float | bool


@dataclass(frozen=True, slots=True)
class Document:
    id: str
    content: str
    metadata: dict[str, MetadataValue]

