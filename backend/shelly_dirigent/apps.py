
import threading
import time
import json
import random
import hashlib
import warnings
from pathlib import Path
from functools import reduce
from django.apps import AppConfig
from django_eventstream import send_event
from rest_framework.exceptions import ValidationError


class TreeItem:
    label: str
    id: str


class TreeItemDevice(TreeItem):
    deviceId: str
    isOn: bool
    isAvailable: bool
    # some variables in the device tree do not match the naming convention, but match the naming of this data across the project, e.g. REST API, frontend
    
    def to_dict(self) -> dict:
        return {'label':self.label,'id':self.id,'isOn':self.isOn,'isAvailable':self.isAvailable}


class TreeItemGroup(TreeItem):
    children: 'list[TreeItemDevice|TreeItemGroup]'
    
    def to_dict(self) -> dict:
        children_dict: list[dict] = []
        children_isOn: list[bool] = []
        children_isAvailable: list[bool] = []

        for child in self.children:
            child_dict = child.to_dict()
            children_dict.append(child_dict)
            children_isOn.append(child_dict['isOn'])
            children_isAvailable.append(child_dict['isAvailable'])

        def combine_bools(a: bool, b: bool) -> bool | None:
            if a is True and b is True:
                return True
            elif a is False and b is False:
                return False
            else:
                return None

        if len(children_isOn) != 0:
            # no initial value passed because needed behavior cannot be achieved using reduce
            isOn: bool = reduce(combine_bools, children_isOn)
        else:
            isOn: bool = None

        if len(children_isAvailable) != 0:
            isAvailable: bool = reduce(combine_bools, children_isAvailable)
        else:
            isAvailable: bool = None

        return {'label':self.label,'id':self.id,'isOn':isOn,'isAvailable':isAvailable,'children':children_dict}


# TODO: better name for class
class InternalApp(AppConfig):
    
    name: str = 'shelly_dirigent'   # TODO: consider renaming as well
    background_task_started: bool = False
    device_tree: list[TreeItemDevice|TreeItemGroup]
    device_tree_mutex = threading.Lock()
    id_to_tree_item_mapping: dict[str,TreeItem] = {}
    device_id_to_tree_item_mapping: dict[str,TreeItem] = {}
    
    def ready(self):
        print('\n\n -> Starting internal app ...\n\n')
        
        self.load_labor_config()

        if not self.background_task_started:
            self.background_task_started = True
            thread = threading.Thread(target=self.loop, daemon=True)
            thread.start()


    def loop(self) -> None:
        while True:
            print('\n\n -> Running background task ...\n\n')

            # TODO: remove, used for debugging only
            # self.change_device_tree_randomly()

            send_event('labor_config', 'message', self.get_device_tree_dicts())
            time.sleep(3)


    def load_labor_config(self) -> list[TreeItemDevice|TreeItemGroup]:

        LABOR_CONFIG_FILE_PATH : str = './labor-config.json'

        lab_config_path = Path(__file__).parent.parent.parent / LABOR_CONFIG_FILE_PATH

        try:
            with open(lab_config_path, 'r', encoding='utf8') as file:
                lab_config_json_string = file.read()
        except FileNotFoundError:
            print(f'Error: Could not find the file {lab_config_path}')
        except IOError:
            print(f'Error: while reading the file {lab_config_path}')

        try:
            lab_config_python_obj = json.loads(lab_config_json_string)
        except ValueError as e:
            print(f'Error: Could not parse JSON {lab_config_json_string} because {e}')

        with self.device_tree_mutex:
            self.device_tree = self.object_list_to_tree_item_list(lab_config_python_obj)

        # TODO: get values (isOn, ...) from devices

        # TODO: remove, used for debugging only
        random.seed(42)     # make the changes reproducible
        self.change_device_tree_randomly(len(self.device_id_to_tree_item_mapping.keys())*2)


    def object_list_to_tree_item_list(self, object_list: list[dict]) -> list[TreeItem]:
        
        return list(map(self.object_to_tree_item, object_list))
    
    
    def object_to_tree_item(self, obj: dict) -> TreeItem:
        
        if len(obj.keys()) != 2:
            raise RuntimeError(f'Error: object {obj} has not exactly two keys!')
        if 'label' not in obj.keys():
            raise RuntimeError(f'Error: object {obj} is missing \'label\'!')
        
        if 'deviceId' in obj.keys():
            if obj['deviceId'] in self.device_id_to_tree_item_mapping:
                raise RuntimeError(f'Error: deviceId of {obj} is not unique!')
            tree_item = TreeItemDevice()
            tree_item.deviceId = obj['deviceId']
            tree_item.isOn = False
            tree_item.isAvailable = False
            self.device_id_to_tree_item_mapping[tree_item.deviceId] = tree_item
            

        elif 'children' in obj.keys():
            tree_item = TreeItemGroup()
            tree_item.children = self.object_list_to_tree_item_list(obj['children'])
            if len(tree_item.children) == 0:
                warnings.warn(f'Warning: object {obj} is a group without children!')

        else:
            raise RuntimeError(f'Error: object {obj} is missing both \'deviceId\' and \'children\'!')
        
        tree_item.label = obj['label']
        
        # use (cryptographic) hash of label for id in order to keep the same id across runs
        hash_source: str = tree_item.label
        tree_item.id = hashlib.sha256(str.encode(hash_source)).hexdigest()
        while tree_item.id in self.id_to_tree_item_mapping:
            hash_source += '0'
            tree_item.id = hashlib.sha256(str.encode(hash_source)).hexdigest()
        
        self.id_to_tree_item_mapping[tree_item.id] = tree_item

        return tree_item


    # TODO: remove, used for debugging only
    def change_device_tree_randomly(self, number_of_changes=1) -> None:

        for _ in range(number_of_changes):

            device_id: str = random.choice(list(self.device_id_to_tree_item_mapping.keys()))
            tree_item: TreeItemDevice = self.device_id_to_tree_item_mapping[device_id]

            toggle_availability: bool = random.choice([True, False])

            with self.device_tree_mutex:
                
                if toggle_availability:
                    tree_item.isAvailable = not tree_item.isAvailable
                else:
                    tree_item.isOn = not tree_item.isOn


    def get_device_tree_dicts(self) -> list[dict]:

        device_tree_dict: list[dict] = []

        with self.device_tree_mutex:
            for tree_item in self.device_tree:
                tree_item_dict = tree_item.to_dict()
                device_tree_dict.append(tree_item_dict)

        return device_tree_dict
    

    def switch(self, id: str, isOn: bool) -> None:
        
        def switch_recursive(id: str, isOn: bool):

            if id not in self.id_to_tree_item_mapping:
                raise ValidationError(detail=f'Specified id {id} does not exist.')

            tree_item = self.id_to_tree_item_mapping[id]
            
            if isinstance( tree_item, TreeItemDevice):
                tree_item.isOn = isOn
            elif isinstance( tree_item, TreeItemGroup):
                for child in tree_item.children:
                    switch_recursive(child.id, isOn)
            else:
                raise RuntimeError(f'Error: object {tree_item} has unexpected type {type(tree_item)}!')
        
        with self.device_tree_mutex:
            switch_recursive(id, isOn)



