import signal

import etcd
import gevent
from api import Api
from engine import Engine
from agent import Agent
from models.manager import VolumeManager, MachineManager
from utils import Service

from config import config


class Cobalt(Service):
    def __init__(self):
        signal.signal(signal.SIGINT, self.handler)
        signal.signal(signal.SIGQUIT, self.handler)

        self.etcd = self._create_etcd(config['etcd'])
        self.volume_manager = self._create_volume_manager(self.etcd)
        self.machine_manager = self._create_machine_manager(self.etcd)
        self.config = config

        services = {
            'engine': Engine(self.etcd, self.volume_manager, self.machine_manager, self.config['engine']),
            'api': Api(self.volume_manager, self.config['api']),
            'agent': Agent(self.machine_manager, self.volume_manager, self.config['agent'])
        }

        self.services = {}

        context_services = self.config['services'] if isinstance(self.config['services'], list) else [self.config['services']]
        for service in context_services:
            if service in services:
                self.services[service] = services.get(service)

    def stop(self):
        for _, service in self.services.items():
            service.stop()

    def start(self):
        routines = []
        for _, service in self.services.items():
            routines += service.start()

        gevent.joinall(routines)

    def handler(self, signum, frame):
        print('Stopping..')
        self.stop()

    @staticmethod
    def _create_etcd(context):
        return etcd.Client(**context)

    @staticmethod
    def _create_volume_manager(etcd):
        return VolumeManager(etcd)

    @staticmethod
    def _create_machine_manager(etcd):
        return MachineManager(etcd)


cobalt = Cobalt()
