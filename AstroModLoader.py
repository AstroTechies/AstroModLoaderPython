import os
import sys
import numpy
import shutil
import json
import argparse
from terminaltables import SingleTable
from pprint import pprint
import PySimpleGUI as sg

from PyPAKParser import PakParser
import cogs.AstroAPI as AstroAPI

# force STA mode so that PySimpleGUI is happy
import ctypes
ctypes.windll.ole32.CoInitialize(None)
import clr

# deal with binary loading in .exe
# pylint: disable=no-member
# pylint: disable=import-error
if hasattr(sys, "_MEIPASS"):
    sys.path.append(os.path.join(sys._MEIPASS, "dlls"))
else:
    sys.path.append("dlls")
clr.AddReference("AstroModIntegrator")
from AstroModIntegrator import ModIntegrator

MOD_LOADER_VERSION = "0.1"
class AstroModLoader():
    def __init__(self, gui, serverMode, updateOnly):
        print("AstroModLoader v" + MOD_LOADER_VERSION)

        self.gui = gui
        sg.theme('Default1')

        self.serverMode = serverMode
        self.updateOnly = updateOnly
        self.readonly = False

        # configure and store used paths
        self.basePath = os.getenv('LOCALAPPDATA') if not self.serverMode else os.getcwd()

        self.downloadPath = os.path.join(
            self.basePath, "Astro", "Saved")
        if not os.path.exists(os.path.join(self.downloadPath, "Mods")):
            os.makedirs(os.path.join(self.downloadPath, "Mods"))
        self.downloadPath = os.path.join(self.downloadPath, "Mods")

        self.installPath = os.path.join(
            self.basePath, "Astro", "Saved")
        if not os.path.exists(os.path.join(self.installPath, "Paks")):
            os.makedirs(os.path.join(self.installPath, "Paks"))
        self.installPath = os.path.join(self.installPath, "Paks")

        if not os.path.exists(os.path.join(self.downloadPath, "modconfig.json")):
            with open(os.path.join(self.downloadPath, "modconfig.json"), 'w') as f:
                f.write('{"mods":[]}')

        self.gamePath = "" if not self.serverMode else os.getcwd()

        print(f"Mod download folder: {self.downloadPath}")

        self.readModFiles()

        self.downloadUpdates()

        self.setGamePath()

        if not self.updateOnly:
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

        # gather mod list (only files)
        modFilenames = numpy.unique(self.getPaksInPath(

            self.downloadPath) + self.getPaksInPath(self.installPath))

        print("Parsing metadata...")
        self.mods = {}
        for modFilename in modFilenames:

            # copy mods files only install dir to download dir
            if not os.path.isfile(os.path.join(self.downloadPath, modFilename)):
                shutil.copyfile(os.path.join(
                    self.installPath, modFilename), os.path.join(self.downloadPath, modFilename))

            # read metadata
            metadata = self.getMetadata(os.path.join(
                self.downloadPath, modFilename))

            # get mod_id
            mod_id = ""
            if "mod_id" in metadata:
                mod_id = metadata["mod_id"]
            else:
                mod_id = modFilename.split("_")[0].split("-")[1]

            # check if it's the first instance
            if not mod_id in self.mods:
                self.mods[mod_id] = {"mod_id": mod_id}

            # field name, default
            dataFields = (
                ("name", modFilename),
                ("author", "---"),
                ("description", ""),
                ("astro_build", "1.0.0.0"),
                ("sync", "serverclient"),
                ("homepage", ""),
                ("download", {}),
                ("linked_actor_components", {})
            )
            for dataField in dataFields:
                if dataField[0] in metadata:
                    self.mods[mod_id][dataField[0]] = metadata[dataField[0]]
                else:
                    self.mods[mod_id][dataField[0]] = dataField[1]

            # sync special case
            if metadata == {}:
                self.mods[mod_id]["sync"] = "client"

            # read priority
            self.mods[mod_id]["priority"] = modFilename.split("_")[0].split("-")[0]

            # versions
            version = ""
            if "version" in metadata:
                version = metadata["version"]
            else:
                version = self.getVersionFromFilename(modFilename)

            if not "versions" in self.mods[mod_id]:
                self.mods[mod_id]["versions"] = {}

            self.mods[mod_id]["versions"][version] = { "filename": modFilename }
            
            # check if mod is installed
            if os.path.isfile(os.path.join(self.installPath, modFilename)):
                self.mods[mod_id]["installed_version"] = version   
                
            # read data from modconfig.json
            if mod_id in self.modConfig["mods"]:
                self.mods[mod_id]["update"] = self.modConfig["mods"][mod_id]["update"]
            else:
                self.mods[mod_id]["update"] = False

        # check which version is active
        for mod_id in self.mods:
            self.mods[mod_id]["installed"] = "installed_version" in self.mods[mod_id]
            if not self.mods[mod_id]["installed"]:
                self.mods[mod_id]["installed_version"] = sorted(list(self.mods[mod_id]["versions"].keys()))[-1]
        
        # pprint(self.mods)

    def downloadUpdates(self):

        # TODO download updates

        print("Downloading updates (not implemented)")

    def updateReadonly(self):
        if not self.readonly:
            try:
                targetPath = os.path.join(self.installPath, "999-AstroModIntegrator_P.pak")
                if not os.path.isfile(targetPath):
                    return
                f = open(targetPath, "a")
                f.close()
            except IOError:
                self.readonly = True

    def updateModInstallation(self):
        if self.readonly:
            return

        # clear install path
        try:
            for pak in self.getPaksInPath(self.installPath):
                os.remove(os.path.join(self.installPath, pak))
        except PermissionError:
            self.readonly = True
            return

        # mod integration with some checks
        if self.gamePath != "":
            # do mod integration
            os.mkdir(os.path.join(self.downloadPath, "temp_mods"))

            try:
                for mod_id in self.mods:
                    filename = self.mods[mod_id]["versions"][
                        self.mods[mod_id]["installed_version"
                    ]]["filename"]
                    if not len(self.mods[mod_id]["linked_actor_components"]) == 0 and (self.mods[mod_id]["installed"]):
                        shutil.copyfile(os.path.join(self.downloadPath, filename), os.path.join(self.downloadPath, "temp_mods", filename))

                ModIntegrator.IntegrateMods(os.path.join(self.downloadPath, "temp_mods"),
                    os.path.join(self.gamePath, R"Astro\Content\Paks"))

                shutil.copyfile(os.path.join(self.downloadPath, "temp_mods", "999-AstroModIntegrator_P.pak"),
                    os.path.join(self.installPath, "999-AstroModIntegrator_P.pak"))
            except Exception as err:
                print("Something went wrong during integration!")
                print(err)
            
            shutil.rmtree(os.path.join(self.downloadPath, "temp_mods"))

        # load all previously active mods back into mod path (with changes)
        for mod_id in self.mods:
            filename = self.mods[mod_id]["versions"][
                self.mods[mod_id]["installed_version"
            ]]["filename"]
            if self.mods[mod_id]["installed"]:
                shutil.copyfile(os.path.join(
                    self.downloadPath, filename), os.path.join(self.installPath, filename))

        # write modconfig.json
        config = {}
        for mod_id in self.mods:
            config[mod_id] = {
                "update": self.mods[mod_id]["update"]
            }
        with open(os.path.join(self.downloadPath, "modconfig.json"), 'r+') as f:
            f.truncate(0)
        with open(os.path.join(self.downloadPath, "modconfig.json"), 'w') as f:
            f.write(json.dumps({"mods": config, "game_path": self.gamePath}, indent=4))

    # --------------------
    #! INTERFACE FUNCTIONS
    # --------------------

    def displayHelp(self, full_args):
        if len(full_args) > 0:
            if full_args[0] == "exit":
                print("Usage: exit")
            elif full_args[0] == "activate" or full_args[0] == "enable":
                print("Usage: enable [mod ID]")
            elif full_args[0] == "deactivate" or full_args[0] == "disable":
                print("Usage: disable [mod ID]")
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
            print("Commands: exit, enable, disable, update, info, (server,) list, help")

    def startCli(self):
        self.printModList = True
        self.updateReadonly()
        while True:
            self.updateModInstallation()
            
            # list mods and commands
            if self.printModList:
                self.printModList = False
                tabelData = []
                tabelData.append(
                    ["Active", "Name", "Version", "Author", "Mod ID", "Update", "Sync"])
                
                for mod_id in self.mods:
                    tabelData.append([
                        self.mods[mod_id]["installed"],
                        self.mods[mod_id]["name"],
                        self.mods[mod_id]["installed_version"],
                        self.mods[mod_id]["author"],
                        mod_id,
                        self.mods[mod_id]["update"],
                        self.mods[mod_id]["sync"]
                    ])

                table = SingleTable(tabelData, "Available Mods")
                print("")
                print(table.table)
                self.displayHelp([])

            full_args = input("> ").split(" ")
            cmd = full_args.pop(0)

            self.updateReadonly()
            if cmd == "exit":
                break
            elif cmd == "activate" or cmd == "enable":
                if self.readonly:
                    print("You cannot modify mods in readonly mode.")
                else:
                    mod_id = self.getInputMod(full_args)
                    if mod_id is not None:
                        self.mods[mod_id]["installed"] = True
                        self.printModList = True
            elif cmd == "deactivate" or cmd == "disable":
                if self.readonly:
                    print("You cannot modify mods in readonly mode.")
                else:
                    mod_id = self.getInputMod(full_args)
                    if mod_id is not None:
                        self.mods[mod_id]["installed"] = False
                        self.printModList = True
            elif cmd == "update":
                if self.readonly:
                    print("You cannot modify mods in readonly mode.")
                else:
                    mod_id = self.getInputMod(full_args)
                    if mod_id is not None:
                        if len(full_args) > 1:
                            lower_param = full_args[1].lower()
                            self.mods[mod_id]["update"] = lower_param == "y" or lower_param == "true"
                        else:
                            lower_param = input("Should this mod be auto updated (Y/N)? ").lower()
                            self.mods[mod_id]["update"] = lower_param == "y" or lower_param == "true"
                        self.printModList = True
            elif cmd == "info":
                mod_id = self.getInputMod(full_args)
                if mod_id is not None:
                    print(json.dumps(self.mods[mod_id], indent=4))
            elif cmd == "server":
                if self.readonly:
                    print("You cannot modify mods in readonly mode.")
                else:               
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

        checkboxes = []

        # create table
        # TODO add info button
        for mod_id in self.mods:
            cbA = sg.Checkbox("", size=(2, 1), default=self.mods[mod_id]["installed"], enable_events=True, key="install_" + mod_id)
            cbB = sg.Checkbox("", size=(2, 1), default=self.mods[mod_id]["update"], enable_events=True, key="update_" + mod_id)
            layout.append([
                cbA,
                sg.Text(self.mods[mod_id]["name"], size=(25, 1)),
                sg.Text(self.mods[mod_id]["installed_version"], size=(5, 1)),
                sg.Text(self.mods[mod_id]["author"], size=(15, 1)),
                sg.Text(self.mods[mod_id]["sync"], size=(10, 1)),
                cbB
            ])
            checkboxes.append([mod_id, cbA, cbB])

        # create footer
        layout.append([
            sg.Text("Loaded mods.", size=(40, 1), key="-message-"),
        ])
        layout.append([sg.Button('Close')])

        # TODO server config

        window = sg.Window("AstroModLoader v" + MOD_LOADER_VERSION, layout)
        window.finalize()

        # Create the event loop
        self.updateReadonly()
        while True:
            self.updateModInstallation()
            if self.readonly:
                for cb in checkboxes:
                    cb[1].Update(value=self.mods[cb[0]]["installed"], disabled=True)
                    cb[2].Update(value=self.mods[cb[0]]["update"], disabled=True)
                checkboxes = [] # a restart of the loader is required to undo readonly mode
            event, values = window.read()
            
            if event in (None, "Close"):
                break

            # listen for checkboxes
            self.updateReadonly()
            if not self.readonly:
                if event.startswith("install_"):
                    changing_mod = event.split("_")[1]
                    self.mods[changing_mod]["installed"] = values[event]
                    
                    window["-message-"].update(
                        (f"Enabled" if values[event] else "Disabled") +
                        f" {changing_mod}")
                elif event.startswith("update_"):
                    changing_mod = event.split("_")[1]
                    self.mods[changing_mod]["update"] = values[event]

                    window["-message-"].update(
                        (f"Enabled updating of" if values[event] else "Disabled updating of") +
                        f" {changing_mod}")
                else:
                    print(f'Event: {event}')
                    print(str(values))

            # TODO implement other buttons, like one for ore info
        window.close()

    # -----------------
    #! HELPER FUNCTIONS
    # -----------------

    def getInputMod(self, full_args):
        mod_id = None
        if len(full_args) > 0:
            mod_id = full_args[0]
        else:
            mod_id = input("Mod ID? ")

        if mod_id in self.mods:
            return mod_id
        else:
            print("Failed to find a mod with that ID")
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

    def getVersionFromFilename(self, filename):
        if len(filename.split("_")[0].split("-")) == 3:
            return filename.split("_")[0].split("-")[2]
        else:
            return "---"

    def setGamePath(self):
        if self.gamePath == "" and "game_path" in self.modConfig:
            self.gamePath = self.modConfig["game_path"]
            
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

        parser.add_argument('--server', dest='server', action='store_true')
        parser.set_defaults(server=False)

        parser.add_argument('--update', dest='update', action='store_true')
        parser.set_defaults(update=False)

        args = parser.parse_args()

        AstroModLoader(args.gui, args.server, args.update)
    except KeyboardInterrupt:
        pass
    # except Exception as err:
     #   print("ERROR")
      #  print(err)
