from dataclasses import dataclass


@dataclass
class Condition:
    parameter: str
    operator: str
    value: str | int | float | bool


@dataclass
class Rule:
    id: int
    category: str
    name: str
    conditions: list[Condition]
    diagnosis: str
    recommendations: list[str]


@dataclass
class Diagnosis:
    category: str
    rule_name: str
    name: str
    confidence: str
    recommendations: list[str]