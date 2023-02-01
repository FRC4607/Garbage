import fabric
import time

if __name__ == "__main__":
    currentlyConnnected = False
    teamIp = input("Enter your RoboRIO's IP: ")
    while True:
        try:
            with fabric.Connection(host=teamIp, user="lvuser", connect_kwargs={"password": ""}) as c:
                if not currentlyConnnected:
                    print("Connected.")
                    currentlyConnnected = True
                    files = c.run("ls *.wpilog").stdout.split('\n')
                    del files[-1]
                    for i, file in enumerate(files):
                        print(f"Getting {file}, {i+1}/{len(files)}")
                        c.get(file, local="./archive/logs/")
                        c.run(f"rm {file}")
                else:
                    print("Connected, but files already downloaded. Sleeping.")
                time.sleep(5)
        except:
            if currentlyConnnected:
                print("Disconnected/Error. Waiting for connection.")
                currentlyConnnected = False
            time.sleep(5)