from inference_engine import load_rules, run_expert_system

def main():
    rules = load_rules("knowledge_base/cpu.json")
    facts = {"cpu_usage": 95,
              "load_high": True}
    results = run_expert_system(facts,rules)
    for result in results:
        print("Категория:", result.category)
        print("Правило:", result.rule_name)
        print()
        print("Диагноз:", result.name)
        print("Уверенность:", result.confidence)
        print("Рекомендации:")
        for recommendation in result.recommendations:
            print("-", recommendation)

if __name__ == "__main__":
    main()