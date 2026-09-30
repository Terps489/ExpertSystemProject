import json

from models import Condition, Rule, Diagnosis


def load_rules(path: str) -> list[Rule]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    rules = []
    for item in data:
        conditions = []

        for condition in item["conditions"]:
            conditions.append(
                Condition(
                    condition["parameter"],
                    condition["operator"],
                    condition["value"]
                )
            )
        rules.append(Rule(item["id"],item["category"],item["name"],conditions,item["diagnosis"],item["recommendations"]))
    return rules


def compare(value: str | int | float | bool, operator: str, expected: str | int | float | bool):
    if operator == "==":
        return value == expected
    if operator == ">":
        return value > expected
    if operator == "<":
        return value < expected
    return False


def check_rule(rule: Rule, facts: dict) -> bool:
    for condition in rule.conditions:
        parameter = condition.parameter
        operator = condition.operator
        expected = condition.value
        if parameter not in facts:
            return False
        if not compare(facts[parameter],operator,expected):
            return False

    return True


def run_expert_system(facts: dict, rules: list[Rule]) -> list[Diagnosis]:
    results = []
    for rule in rules:
        if check_rule(rule, facts):
            results.append(Diagnosis(rule.category, rule.name, rule.diagnosis, "Высокая", rule.recommendations))
    return results