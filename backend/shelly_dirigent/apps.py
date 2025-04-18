
from django.apps import AppConfig
import threading
import time
import json
from pathlib import Path
from django_eventstream import send_event


class TreeItem:
    label: str


class TreeItemDevice(TreeItem):
    deviceId: str


class TreeItemGroup(TreeItem):
    children: 'list[TreeItemDevice|TreeItemGroup]'


# TODO: better name for class
class InternalApp(AppConfig):
    
    name: str = "shelly_dirigent"
    background_task_started: bool = False
    
    def ready(self):
        print("\n\n -> Starting internal app ...\n\n")
        
        self.load_labor_config()

        if not self.background_task_started:
            self.background_task_started = True
            thread = threading.Thread(target=self.loop, daemon=True)
            thread.start()


    def loop(self):
        while True:
            print('\n\n -> Running background task ...\n\n')
            send_event("labor_config", "message", {"text": "hello world"})
            time.sleep(5)


    def load_labor_config(self) -> list[TreeItemDevice|TreeItemGroup]:

        LABOR_CONFIG_FILE_PATH : str = './labor-config.json'

        path = Path(__file__).parent.parent.parent / LABOR_CONFIG_FILE_PATH

        with open(path, "r", encoding="utf8") as file:
            json_string = file.read()

        try:
            python_obj = json.loads(json_string)
        except ValueError as e:
            print("Error:", e)

        tree_item_list = self.object_list_to_tree_item_list(python_obj)

        print(tree_item_list)



    def object_list_to_tree_item_list(self, object_list: list[dict]):
        
        return list(map(self.object_to_tree_item, object_list))
    
    
    def object_to_tree_item(self, obj: dict):
        
        if len(obj.keys()) != 2:
            raise RuntimeError(f'Error: object {obj} has not exactly two keys!')
        if 'label' not in obj.keys():
            raise RuntimeError(f'Error: object {obj} is missing \'label\'!')
        
        if 'deviceId' in obj.keys():
            tree_item = TreeItemDevice()
            tree_item.label = obj['label']
            tree_item.deviceId = obj['deviceId']

        elif 'children' in obj.keys():
            tree_item = TreeItemGroup()
            tree_item.label = obj['label']
            tree_item.children = self.object_list_to_tree_item_list(obj['children'])

        else:
            raise RuntimeError(f'Error: object {obj} is missing both \'deviceId\' and \'children\'!')
        
        return tree_item

