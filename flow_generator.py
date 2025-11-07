
import json
from nlp_processor import process_command

def generate_flow(processed_command):
    """
    Generates a .flo file from the processed command using valid Automate blocks.
    """

    if processed_command["intent"] == "create_message_flow":
        flow = []

        # Initialize the combined inbox
        flow.append({
            "block": {
                "type": "variable_set",
                "variable": "combined_inbox",
                "value": "[]"
            }
        })

        # Trigger for incoming SMS messages
        if "sms" in processed_command["sources"]:
            flow.append({
                "block": {
                    "type": "sms_received",
                    "trigger": True,
                    "variable": "incoming_sms"
                }
            })
            flow.append({
                "block": {
                    "type": "array_add",
                    "array": "combined_inbox",
                    "value": "%incoming_sms"
                }
            })

        # Trigger for incoming Gmail messages (using a loop and unread count)
        if "gmail" in processed_command["sources"]:
            flow.append({
                "block": {
                    "type": "fork",
                    "child_uri": "flow:gmail_checker"
                }
            })

        # Placeholder for sorting and filtering logic
        flow.append({
            "block": {
                "type": "log_append",
                "message": "New message received. Inbox now contains {len(combined_inbox)} messages. Implement sorting and filtering logic here."
            }
        })

        return flow
    else:
        return None

if __name__ == '__main__':
    # This is a simplified representation of the gmail checking flow
    gmail_checker_flow = [
        {
            "block": {
                "label": "gmail_checker",
                "type": "gmail_unread_count",
                "variable": "unread_count"
            }
        },
        {
            "block": {
                "type": "expression_true",
                "expression": "{unread_count} > 0",
                "true_path": "flow:fetch_gmail"
            }
        },
        {
            "block": {
                "type": "delay",
                "duration": "60s"
            }
        }
    ]

    example_command = "I need a flow designed and created in the open flowchart editor that will combine all incoming text messages and emails into a single inbox that is separated by thread and ordered in chronological order received. Include a filter to regroup and organize by sender in chronological order received."
    processed_command = process_command(example_command)
    generated_flow = generate_flow(processed_command)

    if generated_flow:
        with open("generated_flow.flo", "w") as f:
            for item in generated_flow:
                for key, value in item.items():
                    f.write(f"{key}:\n")
                    for prop, val in value.items():
                        f.write(f"  {prop}: {val}\n")

        print("Flow generated successfully!")
    else:
        print("Could not generate flow for the given command.")
