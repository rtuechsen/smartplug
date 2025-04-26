from queue import Queue
import threading
import datetime
from pathlib import Path


# TODO: ensure ubuntu settings for deleting old log files work as expected
# TODO: make sure to set correct time(-zone) and date for ubuntu system / AD-server


class Log:
    message: str
    date: str
    time: str


class Logger:

    _instance = None
    queue: Queue
    output_folder: Path

    def __new__(cls):

        # https://python-patterns.guide/gang-of-four/singleton/

        if cls._instance is None:
            print("Creating the object")
            cls._instance = super(Logger, cls).__new__(cls)

            # need to do initialization here because __init__() would be called every time an instance is requested

            cls._instance.queue = Queue(maxsize=100)
            cls._instance.output_folder = Path("/var/log/shellydirigent/")

            # check if outfolder exists and create it otherwise
            if not cls._instance.output_folder.is_dir():
                cls._instance.output_folder.mkdir()

            # start file writing thread
            thread = threading.Thread(
                target=cls._instance.write_queue_to_file, daemon=True
            )
            thread.start()
            # TODO: how to abort this thread properly when server stops ???

        return cls._instance

    def log(self, message: str):

        # TODO: add note about newlines in docstring

        now = datetime.datetime.now()

        log = Log()
        # remove newlines
        log.message = message.replace("\n", "")

        # add date and time to line
        log.date = now.strftime("%Y-%m-%d")
        log.time = now.strftime("%H:%M:%S.%f")
        self.queue.put(log)

    def write_queue_to_file(self):

        last_filename = None
        log_file = None

        while True:
            log: Log = self.queue.get()

            filename: str = log.date.replace("-", "_") + ".log"

            # check if the currently open log file is matches the log date
            if filename != last_filename:

                # file is not open currently

                # close open file if exists
                if log_file:
                    log_file.close()

                # TODO: what if file writing for error logging itself fails ???

                # open the new file
                log_file_path = self.output_folder / filename
                try:
                    log_file = open(log_file_path, mode="a", encoding="UTF-8")
                    # setting the variable here will make the logger try to open the file again (and again)
                    last_filename = filename
                except FileNotFoundError:
                    print(f"Error: Could not find the file {log_file_path}")
                    return
                except IOError:
                    print(f"Error: while reading the file {log_file_path}")
                    return

            log_str: str = f"{log.date} {log.time} {log.message}\n"
            # TODO: should one really wait until message arrives in queue before printing ???
            print(log_str)
            log_file.write(log_str)

            # better to write to file immediatly so that logs don't get lost if something happens
            log_file.flush()

            self.queue.task_done()
