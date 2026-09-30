system_state = {
    "cpu": {},
    "memory": {},
    "disk": {},
    "network": {},
    "services": {},
    "web": {},

    "diagnoses": []
}


def update_diagnoses(category, results):

    system_state["diagnoses"] = [
        item for item in system_state["diagnoses"]
        if item.category != category
    ]

    system_state["diagnoses"].extend(results)