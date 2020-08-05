import os
import numpy
import shutil
import json

from PyPAKParser import PakParser
import cogs.AstroAPI as AstroAPI


class AstroModLoader():

    def __init__(self):
        print("Astro mod loader v0.1")

        # configure and store used paths
        self.downloadPath = os.getcwd()
        if not os.path.exists(os.path.join(self.downloadPath, "mods")):
            os.makedirs(os.path.join(self.downloadPath, "mods"))
        self.downloadPath = os.path.join(self.downloadPath, "mods")

        self.installPath = os.path.join(
            os.getenv('LOCALAPPDATA'), "Astro", "Saved")
        if not os.path.exists(os.path.join(self.installPath, "Paks")):
            os.makedirs(os.path.join(self.installPath, "Paks"))
        self.installPath = os.path.join(self.installPath, "Paks")
        # print("mod path: " + self.installPath)

        # gather mod list (only files)
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
            print(self.getMetadata(os.path.join(
                self.downloadPath, mod["filename"])))

            """
            {
                "name": "Coordinate GUI",
                "mod_id": "CoordinateGUI",
                "author": "ExampleModder123",
                "description": "Adds a coordinate display that toggles with the F3 key.",
                "version": "0.1.0",
                "astro_build": "1.13.129.0",
                "priority": "000",
                "sync": "client",
                "homepage": "https://example.com",
                "download": {
                    "type": "github_repository",
                    "repository": "examplemodder123/CoordinateGUI"
                },
                "linked_actor_components": {
                    "/Game/Globals/PlayControllerInstance": [
                        "/Game/Globals/ModdedCGUIActorComponent"
                    ]
                }
            }"""

            return mod
        self.mods = list(map(readModData, self.mods))

        print(self.mods)

        # TODO download updates

        # refresh {
        # TODO clear install path

        # TODO load all previously active mods back into mod path (with changes)

        # TODO do mod integration
        # }

        # TODO start cli for moving mods and server config, do refresh

    def getPaksInPath(self, path):
        paks = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and os.path.splitext(os.path.join(path, f))[1] == ".pak":
                paks.append(f)
        return paks

    def getMetadata(self, path):
        PP = PakParser(path)
        metadataFile = [
            x.Data for x in PP.records if x.fileName == "metadata.json"]

        if len(metadataFile) > 0:
            return json.loads(metadataFile[0])
        else:
            return {}


if __name__ == "__main__":
    try:
        os.system("title AstroLauncher - Unofficial Dedicated Server Launcher")
    except:
        pass
    try:
        AstroModLoader()
    except KeyboardInterrupt:
        pass
    # except Exception as err:
     #   print("ERROR")
      #  print(err)
