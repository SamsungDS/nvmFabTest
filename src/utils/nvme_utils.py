""" Generic utilities used in the framework. """
import json

def get_dev_from_subsys(response, nqn):
    """
    Retrieves the device path associated with a given NQN from the response.

    Args:
        response (str): The response string in JSON format.
        nqn (str): The NQN (NVMe Qualified Name) to search for.

    Returns:
        Tuple[int, str]: A tuple containing the status code and the device path/error.
    """
    
    js = json.loads(response)
    js = js[0]
    try:
        
        for subsystem in js["Subsystems"]:
            if nqn == subsystem['NQN'].strip():
                subsys_name = subsystem['Name'].strip()
                dev_path = f"/dev/nvme{subsys_name[-1]}"
                return 0, dev_path
        return 1, "NQN not found in the given response"

    except json.JSONDecodeError as e:
        return 2, "Response is not in JSON format"

    except KeyError as e:
        return 3, f"JSON does not have required keys as per list-subsys format: {str(e)}"


def parse_for_already_connected(response, connect_details, nqn):
    """
    Parses the given response to check if the NQN is already connected using the provided connect details.

    Args:
        response (str): The response to parse, expected to be in JSON format.
        connect_details (dict): A dictionary containing the transport, address, and service ID to match against.
        nqn (str): The NQN (NVMe Qualified Name) to check for.

    Returns:
        Tuple[int, bool, str]: A tuple containing the following values:
            - int: The status code. 0 indicates success, 2 indicates a JSON decoding error, and 3 indicates missing keys in the JSON.
            - bool: True if the NQN is already connected using the provided connect details, False otherwise.
            - str: The device path (/dev/nvmeX) if the NQN is already connected, or an error message if not found.

    """
    
    js = json.loads(response)
    if len(js)==0:
        return 0, False, "NQN not found in the given response"
    js = js[0]
    tr = connect_details["transport"]
    addr = connect_details["addr"]
    svc = connect_details["svcid"]

    try:
        for subsystem in js["Subsystems"]:
            if nqn == subsystem['NQN'].strip():
                path = subsystem['Paths'][0]
                check = path["Transport"] == tr
                check = check and path["Address"].split(',')[0]==f"traddr={addr}"
                check = check and path["Address"].split(',')[1]==f"trsvcid={svc}"

                if check:
                    dev_name = path['Name'].strip()
                    dev_path = f"/dev/{dev_name}"
                    return 0, True, dev_path
                
        return 0, False, "NQN not found in the given response"

    except json.JSONDecodeError as e:
        return 2, False,"Response is not in json format"

    except KeyError as e:
        return 3, False,f"JSON does not have required keys as per list-subsys format: {str(e)}"
