
import unittest
import json
from nlp_processor import process_command
from flow_generator import generate_flow

class TestAutonomate(unittest.TestCase):

    def test_nlp_processor(self):
        """
        Tests that the NLP processor returns the correct structured output.
        """
        command = "I need a flow designed and created in the open flowchart editor that will combine all incoming text messages and emails into a single inbox that is separated by thread and ordered in chronological order received. Include a filter to regroup and organize by sender in chronological order received."
        expected_output = {
            "intent": "create_message_flow",
            "sources": ["sms", "gmail"],
            "actions": [
                {
                    "name": "combine",
                    "output": "combined_inbox"
                },
                {
                    "name": "organize",
                    "criteria": [
                        {"by": "thread"},
                        {"by": "chronological_order"}
                    ]
                },
                {
                    "name": "filter",
                    "criteria": [
                        {"by": "sender"},
                        {"by": "chronological_order"}
                    ]
                }
            ]
        }
        self.assertEqual(process_command(command), expected_output)

    def test_flow_generator(self):
        """
        Tests that the flow generator creates a flow with the correct structure.
        """
        processed_command = {
            "intent": "create_message_flow",
            "sources": ["sms", "gmail"],
        }
        generated_flow = generate_flow(processed_command)
        self.assertIsInstance(generated_flow, list)
        self.assertGreater(len(generated_flow), 0)
        # Check for some of the expected blocks
        block_types = [item["block"]["type"] for item in generated_flow]
        self.assertIn("variable_set", block_types)
        self.assertIn("sms_received", block_types)
        self.assertIn("array_add", block_types)
        self.assertIn("fork", block_types)
        self.assertIn("log_append", block_types)

if __name__ == '__main__':
    unittest.main()
