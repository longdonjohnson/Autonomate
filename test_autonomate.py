
import unittest
import json
from nlp_processor import process_command
from flow_generator import generate_flow

class TestAutonomate(unittest.TestCase):

    def test_nlp_processor_simple(self):
        """
        Tests that the NLP processor can parse a simple command.
        """
        command = "Combine SMS and Gmail."
        processed = process_command(command)
        self.assertEqual(processed['intent'], 'create_message_flow')
        self.assertIn('sms', processed['sources'])
        self.assertIn('gmail', processed['sources'])
        self.assertTrue(any(action['name'] == 'combine' for action in processed['actions']))

    def test_nlp_processor_complex(self):
        """
        Tests that the NLP processor can parse a complex command with multiple sorting and filtering criteria.
        """
        command = "I need a flow that will combine all incoming text messages and emails, then sort by date, sort by sender, and filter by sender."
        processed = process_command(command)
        self.assertEqual(processed['intent'], 'create_message_flow')
        self.assertIn('sms', processed['sources'])
        self.assertIn('gmail', processed['sources'])

        sort_actions = [action for action in processed['actions'] if action['name'] == 'sort']
        self.assertEqual(len(sort_actions), 2)
        self.assertIn('date', [action['by'] for action in sort_actions])
        self.assertIn('sender', [action['by'] for action in sort_actions])

        filter_action = next((action for action in processed['actions'] if action['name'] == 'filter'), None)
        self.assertIsNotNone(filter_action)
        self.assertEqual(filter_action['by'], 'sender')


    def test_flow_generator_syntax(self):
        """
        Tests that the flow generator uses the correct syntax.
        """
        processed_command = {
            "intent": "create_message_flow",
            "sources": ["sms", "gmail"],
            "actions": [{"name": "combine"}, {"name": "sort", "by": "date"}]
        }
        generated_flow = generate_flow(processed_command)
        self.assertIsInstance(generated_flow, list)
        self.assertGreater(len(generated_flow), 0)

        # Check for correct block types and variable syntax
        for item in generated_flow:
            self.assertIn("block", item)
            block = item["block"]
            self.assertNotEqual(block["type"], "variable_set") # Should be set_variable
            if "value" in block and isinstance(block["value"], str):
                self.assertNotIn("{", block["value"])
                self.assertNotIn("}", block["value"])
            if "condition" in block and isinstance(block["condition"], str):
                self.assertNotIn("{", block["condition"])
                self.assertNotIn("}", block["condition"])


if __name__ == '__main__':
    unittest.main()
