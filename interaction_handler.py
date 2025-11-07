
import json

def handle_interaction(processed_command):
    """
    Handles the interaction with the user to clarify ambiguous commands.
    """

    if processed_command.get("ambiguous"):
        missing_info = processed_command.get("missing_information")
        if missing_info == "destination":
            return "I can send a message, but I need to know who to send it to. Could you please provide a recipient?"
        else:
            return "I'm not sure how to proceed. Could you please provide more information?"
    else:
        return None

if __name__ == '__main__':
    # Simulate an ambiguous command from the NLP processor
    ambiguous_command = {
        "intent": "send_message",
        "ambiguous": True,
        "missing_information": "destination"
    }

    clarification_question = handle_interaction(ambiguous_command)
    print(clarification_question)
