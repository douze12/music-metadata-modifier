import unittest

import sys 
import os
sys.path.append(os.path.abspath("."))
from load_tree_test import LoadTreeTestCase
from select_node_test import SelectNodeTestCase
from cancel_modifs_test import CancelModifsTestCase
from broadcast_test import BroadcastTestCase
from save_test import SaveTestCase
        

if __name__ == '__main__':
    test_classes_to_run = [LoadTreeTestCase, SelectNodeTestCase, CancelModifsTestCase, 
                    BroadcastTestCase, SaveTestCase]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)

