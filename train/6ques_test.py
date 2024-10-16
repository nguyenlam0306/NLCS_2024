import main as m
import json
import os
import unittest


class CalQuizTest(unittest.TestCase):

    def test_quiz_1_01(self):
        grader = m.Grader()
        jsonData = grader.grade('', False, False, 1.0)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'], ['A', 'C', 'A', 'C', 'A', 'E'])
        self.assertEqual(data['version']['bubbled'], ['-'])
        self.assertEqual(data['id']['bubbled'], ['0', '0', '2', '1', '0', '5', '5', '4', '8'])


if __name__ == '__main__':
        suite = unittest.TestLoader().loadTestsFromTestCase(CalQuizTest)
        unittest.TextTestRunner(verbosity=2).run(suite)