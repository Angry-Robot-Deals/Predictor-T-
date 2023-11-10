from unittest import main
import unittest


class TestBot(unittest.TestCase):
    def test_load_data(self):
        # Write your test case for the load_data function here
        # df = load_data()
        pass

    def test_load_data_remote(self):
        # Write your test case for the load_data_remote function here
        pass

    def test_get_environment(self):
        # Write your test case for the get_environment function here
        # data = load_data_ram()
        # env = Environment(data=data, reward='profit', remote=False)
        pass

    def test_get_agent(self):
        # Write your test case for the get_agent function here
        pass

    def test_train(self):
        # Write your test case for the train function here
        pass

    def test_test(self):
        # Write your test case for the test function here
        pass

    def test_demo(self):
        # Write your test case for the demo function here
        pass

    def test_print_stats(self):
        pass

    def test_plots(self):
        # plot1 = plot_conf_interval(name='test 1', cum_returns=[0.1, 0.2, 0.3, 0.4, 0.5])
        # plot2 = plot_multiple_conf_interval(name='test 1', cum_returns=[0.1, 0.2, 0.3, 0.4, 0.5])
        pass

    def test_print_stats(self):
        # from prettytable import PrettyTable as PrettyTable
        # table = PrettyTable()
        # stats = print_stats('test', [1, 2, 3, 4, 5], table)
        # print(stats)
        pass


if __name__ == "__main__":
    unittest.main()
