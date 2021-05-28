import os
import time


def execute(file_path):
    """
    Invoke the system handler to open the given file.

    Args:
        file_path (str): The path for the file to be executed
    """
    os.startfile(file_path)


def wait(interval):
    """
    Wait / Sleep for a given interval.

    Args:
        interval (int): Interval in milliseconds

    """
    time.sleep(interval/1000.0)


# TODO: Check with Gabriel about this command.
#  Why use Windows+R + Command instead of exec?
startRun = execute
sleep = wait
