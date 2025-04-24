from queue import Queue
import threading
import datetime
from pathlib import Path

# TODO: create an instance of this in RequestManager

# TODO: ensure ubuntu settings for deleting old log files work as expected


class Log:
    message: str
    date: str
    time: str


class Logger:

    def __init__(self):
        self.queue = Queue(maxsize=100)
        self.output_folder = Path("/var/log/shellydirigent/")
        self.background_task_started = False

        # check if outfolder exists and create it otherwise
        if not self.output_folder.is_dir():
            self.output_folder.mkdir()

        # start file writing thread
        if not self.background_task_started:
            self.background_task_started = True
            thread = threading.Thread(target=self.write_queue_to_file, daemon=True)
            thread.start()

        # TODO: how to abort this thread properly when server stops ???

    def put(self, message: str):

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
                except FileNotFoundError:
                    print(f"Error: Could not find the file {log_file_path}")
                except IOError:
                    print(f"Error: while reading the file {log_file_path}")

                last_filename = filename

            log_file.write(f"{log.date} {log.time} {log.message}")

            self.queue.task_done()
