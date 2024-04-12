import json


def get_dev_from_subsys(response, nqn):
    js = json.loads(response)

    try:
        for subsystem in js["Subsystems"]:
            if nqn == subsystem['NQN'].strip():
                subsys_name = subsystem['Name'].strip()
                dev_path = f"/dev/nvme{subsys_name[-1]}"
                return 0, dev_path
        return 1, "NQN not found in the given response"
    
    except json.JSONDecodeError as e:
        return 2, "Response is not in json format"
    
    except KeyError as e:
        return 3, f"JSON does not have required keys as per list-subsys format: {str(e)}"

def parse_for_already_connected(response, connect_details, nqn):
    js = json.loads(response)

    tr = connect_details["transport"]
    addr = connect_details["addr"] 
    svc = connect_details["svcid"]

    try:
        for subsystem in js["Subsystems"]:
            if nqn == subsystem['NQN'].strip():
                if subsystem['Paths'][0]["Transport"]==tr:
                    if subsystem['Paths'][0]["Address"]==f"traddr={addr} trsvcid={svc}":
                        subsys_name = subsystem['Name'].strip()
                        dev_path = f"/dev/nvme{subsys_name[-1]}"

                        return 0, True, dev_path
        return 0, False, "NQN not found in the given response"
    
    except json.JSONDecodeError as e:
        return 2, "Response is not in json format"
    
    except KeyError as e:
        return 3, f"JSON does not have required keys as per list-subsys format: {str(e)}"
