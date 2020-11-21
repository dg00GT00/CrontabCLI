from os import environ, path

if __name__ == '__main__':
    # Puts this entry point script on the python path
    environ["PYTHONPATH"] = path.normpath("".join([__file__] + [path.sep + ".."] * 2))
