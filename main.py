
import json
from nlp_processor import process_command
from flow_generator import generate_flow

def main():
    """
    The main function for the Autonomate application.
    """

    # Get the user's command
    command = input("Please enter your command: ")

    # Process the command
    processed_command = process_command(command)

    # Handle any ambiguity
    # ... (interaction handling logic will be added here later)

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
