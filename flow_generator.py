
import json
from nlp_processor import process_command

def generate_flow(processed_command):
    """
    Generates a .flo file from the processed command using the correct syntax.
    """

    if processed_command["intent"] == "create_message_flow":
        flow = []

        # Initialize the combined inbox and filtered inbox
        flow.extend([
            {
                "block": {
                    "type": "set_variable",
                    "variable": "combined_inbox",
                    "value": "[]"
                }
            },
            {
                "block": {
                    "type": "set_variable",
                    "variable": "filtered_inbox",
                    "value": "[]"
                }
            }
        ])


        # Trigger for incoming SMS messages
        if "sms" in processed_command["sources"]:
            flow.append({
                "block": {
                    "type": "receive_sms",
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
            flow.extend([
                {
                    "block": {
                        "type": "gmail_unread_count",
                        "variable": "unread_count"
                    }
                },
                {
                    "block": {
                        "type": "for_each",
                        "container": "0..%unread_count",
                        "member": "i"
                    }
                },
                {
                    "block": {
                        "type": "array_add",
                        "array": "combined_inbox",
                        "value": "%gmail_message[i]" # Placeholder for actual message
                    }
                }
            ])


        # Single-flow bubble sort implementation
        flow.extend([
            {
                "block": {
                    "type": "set_variable",
                    "variable": "n",
                    "value": "len(combined_inbox)"
                }
            },
            {
                "block": {
                    "type": "for_each",
                    "container": "0..%n-1",
                    "member": "i",
                }
            },
            {
                "block": {
                    "type": "for_each",
                    "container": "0..%n-%i-1",
                    "member": "j",
                }
            },
            {
                "block": {
                    "type": "conditional",
                    "condition": "%combined_inbox[j].timestamp > %combined_inbox[j+1].timestamp",
                }
            },
            {
                "block": {
                    "type": "set_variable",
                    "variable": "temp",
                    "value": "%combined_inbox[j]"
                }
            },
            {
                "block": {
                    "type": "array_set",
                    "array": "combined_inbox",
                    "index": "%j",
                    "value": "%combined_inbox[j+1]"
                }
            },
            {
                "block": {
                    "type": "array_set",
                    "array": "combined_inbox",
                    "index": "%j+1",
                    "value": "%temp"
                }
            }
        ])

        # Filtering logic
        flow.extend([
            {
                "block": {
                    "type": "for_each",
                    "container": "combined_inbox",
                    "member": "message"
                }
            },
            {
                "block": {
                    "type": "conditional",
                    "condition": "%message.sender == %filter_sender" # filter_sender would be an input
                }
            },
            {
                "block": {
                    "type": "array_add",
                    "array": "filtered_inbox",
                    "value": "%message"
                }
            }
        ])


        return flow
    else:
        return None

if __name__ == '__main__':
    example_command = "I need a flow that will combine all incoming text messages and emails, then sort by date and filter by sender."
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
        "Could not generate flow for the given command."
