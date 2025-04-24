from queue import Queue
import threading
import datetime
from pathlib import Path

# TODO: create an instance of this in RequestManager

# TODO: error handling
#   - file / folder cannot be created

# TODO: ensure ubuntu settings for deleting old log files work as expected


class Log:
    message: str
    date: str
    time: str


class Logger:

    queue: Queue

    def __init__(self):
        self.queue = Queue(maxsize=100)
        self.output_folder = Path("/var/log/shellydirigent/")

        # check if outfolder exists and create it otherwise
        if not self.output_folder.is_dir():
            self.output_folder.mkdir()

        # TODO: start file writing thread
        # if not self.background_task_started:
        #     self.background_task_started = True
        #     thread = threading.Thread(target=self.loop, daemon=True)
        #     thread.start()

        # TODO: how to abort this thread properly when server stops ???

    def put(self, message: str):

        now = datetime.datetime.now()

        log = Log()
        # TODO: check for newline in message -> remove
        log.message = message

        # add date and time to line
        log.date = now.strftime("%Y-%m-%d")
        log.time = now.strftime("%H:%M:%S.%f")
        self.queue.put(log)

    def write_queue_to_file(self):

        # generate file name from current date
        filename: str = datetime.datetime.now().strftime("%Y_%m_%d.log")
        log_file_path = self.output_folder / filename

        try:
            # mode "a" appends to an existing file or creates a new one if not exists
            with open(log_file_path, "a", encoding="utf8") as file:
                log_file = file.read()
        except FileNotFoundError:
            print(f"Error: Could not find the file {log_file_path}")
        except IOError:
            print(f"Error: while reading the file {log_file_path}")

        while True:
            message = self.queue.get()

            # check if date matches the currently open file
            # if not -> switch file
            #       if file does not exist -> create it

            # TODO: write to file

            self.queue.task_done()
