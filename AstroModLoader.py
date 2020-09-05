import os
import sys
import numpy
import shutil
import json
import argparse
from terminaltables import SingleTable
import PySimpleGUI as sg

from PyPAKParser import PakParser
import cogs.AstroAPI as AstroAPI

# force STA mode so that PySimpleGUI is happy
import ctypes
ctypes.windll.ole32.CoInitialize(None)
import clr

# deal with binary loading in .exe
if hasattr(sys, "_MEIPASS"):
    sys.path.append(os.path.join(sys._MEIPASS, "dlls"))
else:
    sys.path.append("dlls")
clr.AddReference("AstroModIntegrator")
from AstroModIntegrator import ModIntegrator

MOD_LOADER_VERSION = "0.1"
class AstroModLoader():
    def __init__(self, gui):
        print("AstroModLoader v" + MOD_LOADER_VERSION)

        self.gui = gui
        sg.theme('Default1')

        # configure and store used paths
        self.basePath = os.path.join(
            os.getenv('LOCALAPPDATA'), "Astro")

        self.downloadPath = os.path.join(
            self.basePath, "Saved")
        if not os.path.exists(os.path.join(self.downloadPath, "Mods")):
            os.makedirs(os.path.join(self.downloadPath, "Mods"))
        self.downloadPath = os.path.join(self.downloadPath, "Mods")

        self.installPath = os.path.join(
            self.basePath, "Saved")
        if not os.path.exists(os.path.join(self.installPath, "Paks")):
            os.makedirs(os.path.join(self.installPath, "Paks"))
        self.installPath = os.path.join(self.installPath, "Paks")

        if not os.path.exists(os.path.join(self.downloadPath, "modconfig.json")):
            with open(os.path.join(self.downloadPath, "modconfig.json"), 'w') as f:
                f.write('{"mods":[]}')

        self.gamePath = ""

        print(f"Mod download folder: {self.downloadPath}")

        self.readModFiles()

        self.downloadUpdates()

        self.setGamePath()

        if self.gui:
            self.startGUI()
        else:
            self.startCli()

        print("Exiting...")

    # ------------------
    #! STARTUP FUNCTIONS
    # ------------------

    def readModFiles(self):
        self.modConfig = {}
        with open(os.path.join(self.downloadPath, "modconfig.json"), 'r') as f:
            self.modConfig = json.loads(f.read())

        if "gamePath" in self.modConfig:
            self.gamePath = self.modConfig["gamePath"]
        else:
            self.gamePath = ""

        # gather mod list (only files)
        print("Gathering mod data...")
        self.mods = numpy.unique(self.getPaksInPath(
            self.downloadPath) + self.getPaksInPath(self.installPath))

        self.mods = list(map(lambda m: {"filename": m}, self.mods))

        def readModData(mod):
            # check mod if it is installed
            mod["installed"] = os.path.isfile(
                os.path.join(self.installPath, mod["filename"]))

            # copy mods only install dir to download dir
            if not os.path.isfile(os.path.join(self.downloadPath, mod["filename"])):
                shutil.copyfile(os.path.join(
                    self.installPath, mod["filename"]), os.path.join(self.downloadPath, mod["filename"]))

            # read metadata
            mod["metadata"] = {}
            metadata = self.getMetadata(os.path.join(
                self.downloadPath, mod["filename"]))

            if "name" in metadata:
                mod["metadata"]["name"] = metadata["name"]
            else:
                mod["metadata"]["name"] = mod["filename"]

            if "mod_id" in metadata:
                mod["metadata"]["mod_id"] = metadata["mod_id"]
            else:
                mod["metadata"]["mod_id"] = mod["filename"].split("_")[
                    0].split("-")[1]

            if "author" in metadata:
                mod["metadata"]["author"] = metadata["author"]
            else:
                mod["metadata"]["author"] = "---"

            if "description" in metadata:
                mod["metadata"]["description"] = metadata["description"]
            else:
                mod["metadata"]["description"] = ""

            if "version" in metadata:
                mod["metadata"]["version"] = metadata["version"]
            else:
                if len(mod["filename"].split("_")[0].split("-")) == 3:
                    mod["metadata"]["version"] = mod["filename"].split("_")[
                        0].split("-")[2]
                else:
                    mod["metadata"]["version"] = "---"

            if "astro_build" in metadata:
                mod["metadata"]["astro_build"] = metadata["astro_build"]
            else:
                mod["metadata"]["astro_build"] = "1.0.0.0"

            if "sync" in metadata:
                mod["metadata"]["sync"] = metadata["sync"]
            else:
                mod["metadata"]["sync"] = "serverclient"
            if metadata == {}:
                mod["metadata"]["sync"] = "client"

            if "homepage" in metadata:
                mod["metadata"]["homepage"] = metadata["homepage"]
            else:
                mod["metadata"]["homepage"] = ""

            if "download" in metadata:
                mod["metadata"]["download"] = metadata["download"]
            else:
                mod["metadata"]["download"] = {}

            if "linked_actor_components" in metadata:
                mod["metadata"]["linked_actor_components"] = metadata["linked_actor_components"]
            else:
                mod["metadata"]["linked_actor_components"] = {}

            # read data from modconfig.json
            config = list(
                filter(lambda m: m["mod_id"] == mod["metadata"]["mod_id"], self.modConfig["mods"]))
            if len(config):
                config = config[0]
                if "update" in config:
                    mod["update"] = config["update"]
                else:
                    mod["update"] = True
            else:
                mod["update"] = True

            # read priority
            mod["metadata"]["priority"] = mod["filename"].split("_")[
                0].split("-")[0]

            return mod
        print("Parsing metadata...")
        self.mods = list(map(readModData, self.mods))

    def downloadUpdates(self):

        # TODO download updates

        print("Downloading updates (not implemented)")

    def updateModInstallation(self):
        # clear install path
        for pak in self.getPaksInPath(self.installPath):
            os.remove(os.path.join(self.installPath, pak))

        # mod integration with some checks
        if self.gamePath != "":
            # do mod integration
            os.mkdir(os.path.join(self.downloadPath, "temp_mods"))

            try:
                for mod in self.mods:
                    if not len(mod["metadata"]["linked_actor_components"]) == 0 and (mod["installed"]):
                        shutil.copyfile(os.path.join(
                            self.downloadPath, mod["filename"]), os.path.join(self.downloadPath, "temp_mods", mod["filename"]))

                ModIntegrator.IntegrateMods(os.path.join(self.downloadPath, "temp_mods"),
                    os.path.join(self.gamePath, R"Astro\Content\Paks"))

                shutil.copyfile(os.path.join(self.downloadPath, "temp_mods", "999-AstroModIntegrator_P.pak"),
                    os.path.join(self.installPath, "999-AstroModIntegrator_P.pak"))
            except Exception as err:
                print("Something went wrong during integration!")
                print(err)
            
            shutil.rmtree(os.path.join(self.downloadPath, "temp_mods"))

        # load all previously active mods back into mod path (with changes)
        for mod in self.mods:
            if mod["installed"]:
                shutil.copyfile(os.path.join(
                    self.downloadPath, mod["filename"]), os.path.join(self.installPath, mod["filename"]))

        # write modconfig.json
        config = []
        for mod in self.mods:
            config.append({
                "mod_id": mod["metadata"]["mod_id"],
                "update": mod["update"]
            })
        with open(os.path.join(self.downloadPath, "modconfig.json"), 'r+') as f:
            f.truncate(0)
        with open(os.path.join(self.downloadPath, "modconfig.json"), 'w') as f:
            f.write(json.dumps({"mods": config, "gamePath": self.gamePath}, indent=4))

    # --------------------
    #! INTERFACE FUNCTIONS
    # --------------------

    def displayHelp(self, full_args):
        if len(full_args) > 0:
            if full_args[0] == "exit":
                print("Usage: exit")
            elif full_args[0] == "activate" or full_args[0] == "enable":
                print("Usage: activate [mod ID]")
            elif full_args[0] == "deactivate" or full_args[0] == "disable":
                print("Usage: deactivate [mod ID]")
            elif full_args[0] == "update":
                print("Usage: update [mod ID] [y/n]")
            elif full_args[0] == "info":
                print("Usage: info [mod ID]")
            elif full_args[0] == "server":
                # TODO server mod downloading
                print("Unimplemented")
            elif full_args[0] == "list":
                print("Usage: list")
            elif full_args[0] == "help":
                print("Usage: help [command]")
            else:
                print("Unknown command")
        else:
            print("Commands: exit, activate, deactivate, update, info, (server,) list, help")

    def startCli(self):
        self.printModList = True
        while True:
            self.updateModInstallation()

            # list mods and commands
            if self.printModList:
                self.printModList = False
                tabelData = []
                tabelData.append(
                    ["Active", "Name", "Version", "Author", "Mod ID", "Update", "Sync"])

                for mod in self.mods:
                    tabelData.append([
                        mod["installed"],
                        mod["metadata"]["name"],
                        mod["metadata"]["version"],
                        mod["metadata"]["author"],
                        mod["metadata"]["mod_id"],
                        mod["update"],
                        mod["metadata"]["sync"]
                    ])

                table = SingleTable(tabelData, "Available Mods")
                print("")
                print(table.table)
                self.displayHelp([])

            full_args = input("> ").split(" ")
            cmd = full_args.pop(0)

            if cmd == "exit":
                break
            elif cmd == "activate" or cmd == "enable":
                mod = self.getInputMod(full_args)
                if mod is not None:
                    mod["installed"] = True
                    self.printModList = True
            elif cmd == "deactivate" or cmd == "disable":
                mod = self.getInputMod(full_args)
                if mod is not None:
                    mod["installed"] = False
                    self.printModList = True
            elif cmd == "update":
                mod = self.getInputMod(full_args)
                if mod is not None:
                    if len(full_args) > 1:
                        lower_param = full_args[1].lower()
                        mod["update"] = lower_param == "y" or lower_param == "true"
                    else:
                        lower_param = input("Should this mod be auto updated (Y/N)? ").lower()
                        mod["update"] = lower_param == "y" or lower_param == "true"
                    self.printModList = True
            elif cmd == "info":
                mod = self.getInputMod(full_args)
                if mod is not None:
                    print(json.dumps(mod, indent=4))
            elif cmd == "server":
                # TODO server mod downloading
                print("not implemented yet")
            elif cmd == "list":
                self.printModList = True
            elif cmd == "help":
                self.displayHelp(full_args)
            else:
                print("Unknown command, use help for help")

    def startGUI(self):
        print("gui go brrrrrrrr")

        # create header
        layout = [
            [sg.Text("Available Mods:")],
            [
                sg.Text("Active", size=(4, 1)),
                sg.Text("Modname", size=(25, 1)),
                sg.Text("Version", size=(5, 1)),
                sg.Text("Author", size=(15, 1)),
                sg.Text("Sync", size=(10, 1)),
                sg.Text("Auto update?", size=(10, 1))
            ]
        ]

        # create table
        # TODO add info button
        for mod in self.mods:
            layout.append([
                sg.Checkbox("", size=(
                    2, 1), default=mod["installed"], enable_events=True, key="install_" + mod["metadata"]["mod_id"]),
                sg.Text(mod["metadata"]["name"], size=(25, 1)),
                sg.Text(mod["metadata"]["version"], size=(5, 1)),
                sg.Text(mod["metadata"]["author"], size=(15, 1)),
                sg.Text(mod["metadata"]["sync"], size=(10, 1)),
                sg.Checkbox("", size=(
                    2, 1), default=mod["update"], enable_events=True, key="update_" + mod["metadata"]["mod_id"]),
            ])

        # create footer
        layout.append([
            sg.Text("Loaded mods.", size=(40, 1), key="-message-"),
        ])
        layout.append([sg.Button('Close')])

        # TODO server config

        window = sg.Window("AstroModLoader v" + MOD_LOADER_VERSION, layout)

        # Create the event loop
        while True:
            self.updateModInstallation()

            event, values = window.read()

            if event in (None, "Close"):
                break

            # listen for checkboxes
            if event.startswith("install_"):
                changing_mod = event.split("_")[1]
                self.getModRef(changing_mod)[
                    "installed"] = values[event]
                window["-message-"].update(
                    (f"Enabled" if values[event] else "Disabled") +
                    f" {changing_mod}")
            elif event.startswith("update_"):
                changing_mod = event.split("_")[1]
                self.getModRef(changing_mod)[
                    "update"] = values[event]
                window["-message-"].update(
                    (f"Enabled updating of" if values[event] else "Disabled updating of") +
                    f" {changing_mod}")
            else:
                print(f'Event: {event}')
                print(str(values))

            # TODO implement other buttons
        window.close()

    # -----------------
    #! HELPER FUNCTIONS
    # -----------------

    def getInputMod(self, full_args):
        mod = None
        if len(full_args) > 0:
            mod = self.getModRef(full_args[0])
        else:
            mod = self.getModRef(input("Mod ID? "))

        if mod is not None:
            return mod
        else:
            print("Failed to find a mod with that ID")
            return None

    def getModRef(self, mod_id):
        mod = None
        for m in self.mods:
            if m["metadata"]["mod_id"] == mod_id:
                mod = m
        if mod is not None:
            return mod
        else:
            return None

    def getPaksInPath(self, path):
        paks = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and os.path.splitext(os.path.join(path, f))[1] == ".pak" and f != "999-AstroModIntegrator_P.pak":
                paks.append(f)
        return paks

    def getMetadata(self, path):
        with open(path, "rb") as pakFile:
            PP = PakParser(pakFile)
            mdFile = "metadata.json"
            md = PP.List(mdFile)
            ppData = {}
            if mdFile in md:
                ppData = json.loads(PP.Unpack(mdFile).Data)
            return ppData

    def setGamePath(self):
        if self.gamePath != "" and not os.path.isdir(self.gamePath):
            self.gamePath = ""

        if self.gamePath == "":
            if self.gui:
                while True:
                    installPath = sg.PopupGetFolder("Choose game installation directory")
                    if installPath is None:
                        break
                    if installPath != "" and os.path.isdir(installPath):
                        self.gamePath = installPath
                        break
            else:
                print(
                    "No game path specified, mod integration won't be possible until one is specified in modconfig.json")

if __name__ == "__main__":
    try:
        os.system("title AstroModLoader v" + MOD_LOADER_VERSION)
    except:
        pass
    try:
        parser = argparse.ArgumentParser()

        parser.add_argument('--gui', dest='gui', action='store_true')
        parser.add_argument('--no-gui', dest='gui', action='store_false')
        parser.set_defaults(gui=True)

        args = parser.parse_args()

        AstroModLoader(args.gui)
    except KeyboardInterrupt:
        pass
    # except Exception as err:
     #   print("ERROR")
      #  print(err)
