import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'bin' / 'run-round-claude.py'
spec = importlib.util.spec_from_file_location('claude_runner', path)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class ClaudeRunnerTests(unittest.TestCase):
    def test_only_successful_structured_output_is_admitted(self):
        result = {'type': 'result', 'subtype': 'success', 'is_error': False,
                  'session_id': 'session', 'structured_output': {'verdict': 'ready'}}
        self.assertEqual(runner.extract_result(result), {'verdict': 'ready'})
        for changed in ({'is_error': True}, {'subtype': 'error_max_turns'},
                        {'structured_output': None}, {'session_id': ''}):
            with self.assertRaises(ValueError): runner.extract_result(result | changed)

    def test_read_only_tools_and_explicit_resume(self):
        args = runner.command('claude.exe', '{}', 'high', 'old-session')
        self.assertEqual(args[0], 'claude.exe')
        self.assertEqual(args[args.index('--tools') + 1], 'Read,Grep,Glob')
        self.assertEqual(args[args.index('--resume') + 1], 'old-session')
        self.assertIn('--strict-mcp-config', args)
        self.assertNotIn('--dangerously-skip-permissions', args)
        self.assertNotIn('--resume', runner.command('claude.exe', '{}', 'medium'))
