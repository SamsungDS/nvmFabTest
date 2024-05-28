"""
Device Library.

Library for maintaing device related objects. Provides 
abstraction to the device layer.
"""
from lib.applib.libnvme_lib import Libnvme
from lib.applib.nvme_cli_lib import NVMeCLILib
from lib.cmdlib.commands_lib import NVMeCommandLib


class Controller():
    """
    Represents a controller object that interacts with a device using different applications.

    Args:
        dev_name (str): The name of the device.
        app_name (str): The name of the application to be used for interaction.

    Attributes:
        cmdlib: An instance of the NVMeCommandLib class.
        dev_name (str): The name of the device.
        app_name (str): The name of the application.
        app: An instance of the application class based on the provided app_name.
    """

    def __init__(self, dev_name, app_name) -> None:
        """ Constructor """
        self.cmdlib = NVMeCommandLib(dev_name, app_name)
        self.dev_name = dev_name
        self.app_name = app_name
        if app_name.lower() == "nvme-cli":
            self.app = NVMeCLILib(dev_name)
        elif app_name.lower() == "libnvme":
            self.app = Libnvme(dev_name)
        else:
            print("Error : ", app_name, app_name.lower)


class DeviceConfig:
    """
    Encapsulating the configuration details of a device in one object.

    Attributes:
        device (str): The device name.
        application (str): The application name.
    """

    def __init__(self, device, application) -> None:
        """ Parametrized Constructor """
        self.device = device
        self.application = application


class ConnectDetails:
    """
    Encapsulating the connection details for a device in one object.

    Attributes:
        transport (str): The transport protocol used for the connection.
        address (str): The IP address of the device.
        svcid (str): The port SVCID for the connection.
        index (int): The index if multiple devices in the same port.
    """

    def __init__(self, tr='', addr='', svc='', index=0) -> None:
        """ Constructor """
        self.transport = tr
        self.address = addr
        self.svcid = svc
        self.index = index