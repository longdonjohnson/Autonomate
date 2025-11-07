
import json
import re

def process_command(command):
    """
    Processes the user's command to extract the intent and entities using regex.
    """
    intent = "unknown"
    sources = []
    actions = []

    # Regex to identify sources
    if re.search(r'text messages|sms', command, re.I):
        sources.append("sms")
    if re.search(r'emails|gmail', command, re.I):
        sources.append("gmail")

    # Regex to identify actions and their parameters
    if re.search(r'combine|merge', command, re.I):
        actions.append({"name": "combine"})

    sort_matches = re.findall(r'(sort|order) by (sender|date|time)', command, re.I)
    for match in sort_matches:
        actions.append({"name": "sort", "by": match[1]})

    filter_matches = re.findall(r'(filter|group) by (sender|date|time)', command, re.I)
    for match in filter_matches:
        actions.append({"name": "filter", "by": match[1]})


    # Determine intent
    if sources and actions:
        intent = "create_message_flow"

    return {
        "intent": intent,
        "sources": sources,
        "actions": actions,
        "original_command": command
    }

if __name__ == '__main__':
    example_command = "I need a flow that will combine all incoming text messages and emails, then sort by date, sort by sender, and filter by sender."
    processed_command = process_command(example_command)
    print(json.dumps(processed_command, indent=4))
