"""Contains classes for logging events and errors."""

from queue import Queue
import threading
import datetime
from pathlib import Path
from io import TextIOWrapper


# TODO: ensure ubuntu settings for deleting old log files work as expected
# TODO: make sure to set correct time(-zone) and date for ubuntu system / AD-server


class Log:
    """A pure data class that groups properties of a log."""

    def __init__(self):
        """Constructor for the class."""

        ## The message of the log.
        self.message: str

        ## The date when the log was created. Should be in format YYYY-MM-DD.
        self.date: str

        ## The time of day when the log was created. Should be in format HH:MM:SS.mmmmmm. 'm' stands for the fractional part the seconds.
        self.time: str


class Logger:
    """A class for logging events and errors both to file and to the console.

    This class is implemented as a singleton as it is possibly used by multiple threads. Logging using this class should be thread safe.
    Because the class is a singleton its attributes are all class attributes.

    Log files are stored in '/var/log/shellydirigent/' with a file per day.
    TODO: add note about linux removing files from /var/log/ regularly.
    """

    # Note: type hint needs to be in quotes as the class is not defined yet.
    ## The (only) instance of this class.
    _instance: "Logger" = None

    ## A thread safe queue that stores the logs.
    _log_queue: Queue

    ## The output folder of log files. Set fixed to '/var/log/shellydirigent/'.
    _output_folder: Path = Path("/var/log/shellydirigent/")

    def __new__(cls):
        """Creates an instance of the class.

        Implements the singleton pattern taken from this tutorial: https://python-patterns.guide/gang-of-four/singleton/
        """

        if cls._instance is None:
            print("Creating the object")
            cls._instance = super(Logger, cls).__new__(cls)

            # We need to do the initializations here because __init__() would be called every time an instance is requested.

            # The size of the queue is set arbitrarily to 100.
            cls._instance._log_queue = Queue(maxsize=100)

            # check if outfolder exists and create it otherwise
            if not cls._instance._output_folder.is_dir():
                cls._instance._output_folder.mkdir()

            # start file writing thread
            thread = threading.Thread(
                target=cls._instance._write_queue_to_file, daemon=True
            )
            thread.start()

        return cls._instance

    def info(self, message: str) -> None:
        """Takes a message and logs it with the INFO prefix. Removes newlines from the message.

        @param message The message to be logged.
        """

        self._log("INFO: " + message)

    def warn(self, message: str) -> None:
        """Takes a message and logs it with the WARNING prefix. Removes newlines from the message.

        @param message The message to be logged."""

        self._log("WARNING: " + message)

    def error(self, message: str) -> None:
        """Takes a message and logs it with the ERROR prefix. Removes newlines from the message.

        @param message The message to be logged."""

        self._log("ERROR: " + message)

    def _log(self, message: str) -> None:
        """Takes a message, adds current time and date to it and adds it as a Log to the log_queue.

        @param message The message to be logged."""

        now = datetime.datetime.now()

        log = Log()
        # remove newlines
        log.message = message.replace("\n", "")

        # add date and time to line
        log.date = now.strftime("%Y-%m-%d")
        log.time = now.strftime("%H:%M:%S.%f")

        self._log_queue.put(log)

    def _write_queue_to_file(self) -> None:
        """Function for the worker thread. Takes incoming logs from the log_queue and writes them to a log file."""

        last_filename: str = None
        log_file: TextIOWrapper = None

        while True:
            log: Log = self._log_queue.get()

            filename: str = log.date.replace("-", "_") + ".log"

            # check if the currently open log file is matches the log date
            if filename != last_filename:

                # file is not open currently

                # close open file if exists
                if log_file:
                    log_file.close()

                # open the new file
                log_file_path: Path = self._output_folder / filename
                try:
                    log_file = open(log_file_path, mode="a", encoding="UTF-8")
                    # setting the variable here will make the logger try to open the file again (and again)
                    last_filename = filename
                except FileNotFoundError:
                    # these errors are printed to console directly as logging obviously does not work properly
                    print(
                        f"ERROR: Could not find the log file {log_file_path}. Logging will not work until this issue is fixed and the server is restarted."
                    )
                    # end the logging process, but keep the server running as this is not a fatal error
                    return
                except IOError:
                    # these errors are printed to console directly as logging obviously does not work properly
                    print(
                        f"ERROR: While reading the log file {log_file_path}. Logging will not work until this issue is fixed and the server is restarted."
                    )
                    # end the logging process, but keep the server running as this is not a fatal error
                    return

            log_str: str = f"{log.date} {log.time} {log.message}\n"

            print(log_str)
            log_file.write(log_str)

            # better to write to file immediatly so that logs don't get lost if something happens
            log_file.flush()

            self._log_queue.task_done()
