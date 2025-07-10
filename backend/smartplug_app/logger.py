"""Contains classes for logging events and errors."""

from queue import Queue, Full
import threading
import datetime
from pathlib import Path


class Log:
    """A pure data class that groups properties of a log."""

    def __init__(self):
        """Constructor for the class."""

        ## The message of the log.
        self.message: str

        ## The date when the log was created. Should be in format YYYY-MM-DD.
        self.date: str

        ## The time of day when the log was created. Should be in format
        ## HH:MM:SS.mmmmmm.\ 'm' stands for the fractional part the seconds.
        self.time: str


class Logger:
    """A class for logging events and errors both to file and to the console.

    This class is implemented as a singleton as it is possibly used by
    multiple threads. Logging using this class should be thread safe.
    Because the class is a singleton its attributes are all class
    attributes.

    TODO: add comment about 90% full -> discard

    Log files are stored in '/var/log/smartplug_app/' with a file per
    day. The linux tool 'logroate' is used in this project to switch the
    log file and remove old log files regularly.
    """

    ## The (only) instance of this class.
    _instance: "Logger" = None

    ## The maximal size of the queue.
    QUEUE_MAX_SIZE: int = 100

    ## A thread safe queue that stores the logs.\ The size of the queue is set
    ## arbitrarily to 100.
    _log_queue: Queue = Queue(maxsize=QUEUE_MAX_SIZE)

    ## The output folder of log files. Set fixed to
    ## '/var/log/smartplug_app/'.
    _output_folder: Path = Path("/var/log/smartplug_app/")

    ## The path of the active log file.
    _log_file_path: Path = _output_folder / "smartplug_app.log"

    def __new__(cls):
        """Creates an instance of the class.

        Implements the singleton pattern taken from this tutorial:
        https://python-patterns.guide/gang-of-four/singleton/
        """

        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)

            # We need to do the initializations here because __init__() would
            # be called every time an instance is requested.

            # check if outfolder exists and create it otherwise
            if not cls._instance._output_folder.is_dir():
                cls._instance._output_folder.mkdir()

            # start file writing thread
            thread = threading.Thread(
                target=cls._instance._write_queue_to_file, daemon=True
            )
            thread.start()

        return cls._instance

    def info(
        self,
        message: str,
        client_ip_address: str = None,
        username: str = None,
        date_time: datetime.datetime = None,
    ) -> None:
        """Takes a message and logs it with the INFO prefix. Removes newlines
        from the message.

        @param message The message to be logged.

        @param client_ip_address The IP address of the client making the
        request.

        @param username The username of the user making the request.

        @param date_time The date and time when the error occured.
        """

        self._log("INFO: " + message, client_ip_address, username, date_time)

    def warn(
        self,
        message: str,
        client_ip_address: str = None,
        username: str = None,
        date_time: datetime.datetime = None,
    ) -> None:
        """Takes a message and logs it with the WARNING prefix. Removes
        newlines from the message.

        @param message The message to be logged.

        @param client_ip_address The IP address of the client making the
        request.

        @param username The username of the user making the request.

        @param date_time The date and time when the error occured.
        """

        self._log(
            "WARNING: " + message, client_ip_address, username, date_time
        )

    def error(
        self,
        message: str,
        client_ip_address: str = None,
        username: str = None,
        date_time: datetime.datetime = None,
    ) -> None:
        """Takes a message and logs it with the ERROR prefix. Removes newlines
        from the message.

        @param message The message to be logged.

        @param client_ip_address The IP address of the client making the
        request.

        @param username The username of the user making the request.

        @param date_time The date and time when the error occured.
        """

        self._log("ERROR: " + message, client_ip_address, username, date_time)

    def _log(
        self,
        message: str,
        client_ip_address: str = None,
        username: str = None,
        date_time: datetime.datetime = None,
    ) -> None:
        """Takes a message, adds current time and date to it and adds it as a
        Log to the log_queue.

        @param message The message to be logged.

        @param client_ip_address The IP address of the client making the
        request.

        @param username The username of the user making the request.

        @param date_time The date and time when the error occured.
        """

        if date_time is None:
            now = datetime.datetime.now()
        else:
            now = date_time

        log = Log()
        message += f" (client ip: {client_ip_address}, username: {username})"
        # remove newlines
        log.message = message.replace("\n", "")

        # add date and time to line
        log.date = now.strftime("%Y-%m-%d")
        log.time = now.strftime("%H:%M:%S.%f")

        try:
            if Logger._log_queue.qsize() >= Logger.QUEUE_MAX_SIZE * 0.9:
                log.message = (
                    f"ERROR: The logging queue has nearly reached its maximum"
                    f"size of {Logger.QUEUE_MAX_SIZE}, incomming logs cannot"
                    f"be logged and will be discarded."
                )

            Logger._log_queue.put(log)

        except Full:
            pass

    def _write_queue_to_file(self) -> None:
        """Function for the worker thread to write logs to file.

        Takes incoming logs from the log_queue and writes them to the
        log file.
        """

        try:
            with open(
                Logger._log_file_path, mode="a", encoding="UTF-8"
            ) as log_file:

                while True:

                    log: Log = Logger._log_queue.get()
                    log_str: str = f"{log.date} {log.time} {log.message}\n"

                    # log to console
                    print(log_str)
                    # log to file
                    log_file.write(log_str)

                    # better to write to file immediatly so that logs don't get
                    # lost if something happens
                    log_file.flush()

                    Logger._log_queue.task_done()

        except FileNotFoundError:
            # these errors are printed to console directly as logging obviously
            # does not work properly
            print(
                f"ERROR: Could not find the log file {Logger._log_file_path}. "
                "Logging will not work until this issue is fixed and the "
                "server is restarted."
            )
            # end the logging process, but keep the server running as this is
            # not a fatal error
            return
        except IOError:
            # these errors are printed to console directly as logging obviously
            # does not work properly
            print(
                f"ERROR: While reading the log file {Logger._log_file_path}. "
                "Logging will not work until this issue is fixed and the "
                "server is restarted."
            )
            # end the logging process, but keep the server running as this is
            # not a fatal error
            return
