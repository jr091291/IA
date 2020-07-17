import yaml

__config = None

def config(path: str):
    try:
        global __config
    
        if not __config:
            with open(path) as file:
               __config = yaml.load(file, Loader=yaml.FullLoader)

        return __config

    except:
        print("Something went wrong when reading to the file {}".format(path))
