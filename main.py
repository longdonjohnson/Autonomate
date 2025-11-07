
import json
from nlp_processor import process_command
from flow_generator import generate_flow
from interaction_handler import handle_interaction

def main():
    """
    The main function for the Autonomate application.
    """

    # Get the user's command
    command = input("Please enter your command: ")

    # Process the command
    processed_command = process_command(command)

    # Handle any ambiguity
    clarification_question = handle_interaction(processed_command)
    while clarification_question:
        print(clarification_question)
        command = input("Please provide more information: ")
        # In a real application, we would update the processed_command
        # with the new information. For now, we'll just re-process the
        # original command with the added context.
        processed_command = process_command(command)
        clarification_question = handle_interaction(processed_command)

    # Generate the flow
    generated_flow = generate_flow(processed_command)

    # Save the flow to a file
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

if __name__ == '__main__':
    main()
