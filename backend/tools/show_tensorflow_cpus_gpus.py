from lib import util_lib


def main():
    print(util_lib.get_available_gpus())
    print(util_lib.get_available_cpus())

if __name__ == "__main__":
    main()
