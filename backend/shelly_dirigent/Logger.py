from queue import Queue
import threading

# TODO: create an instance of this in RequestManager

# TODO: error handling
#   - file / folder cannot be created


class Logger:

    queue: Queue

    def __init__(self):
        self.queue = Queue(maxsize=100)
        self.output_folder = "/var/log/shellydirigent/"

        # TODO: check if outfolder exists and create it otherwise

        # TODO: start file writing thread
        # if not self.background_task_started:
        #     self.background_task_started = True
        #     thread = threading.Thread(target=self.loop, daemon=True)
        #     thread.start()

        # TODO: how to abort this thread properly when server stops ???

    def put(self, message: str):

        # TODO: add date and time

        self.queue.put(message)

    def write_queue_to_file(self):

        # generate file name from current date

        # check if this file already exists
        #   if yes -> resume that file
        #   else -> create new file

        # open a file for writing

        while True:
            message = self.queue.get()

            # check if date matches the currently open file
            # if not -> switch file
            #       if file does not exist -> create it

            # TODO: write to file

            self.queue.task_done()
