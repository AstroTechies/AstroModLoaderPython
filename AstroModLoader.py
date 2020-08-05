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
                mod["metadata"]["author"] = ""

            if "description" in metadata:
                mod["metadata"]["description"] = metadata["description"]
            else:
                mod["metadata"]["description"] = ""

            if "version" in metadata:
                mod["metadata"]["version"] = metadata["version"]
            else:
                mod["metadata"]["version"] = "1.0.0"

            if "astro_build" in metadata:
                mod["metadata"]["astro_build"] = metadata["astro_build"]
            else:
                mod["metadata"]["astro_build"] = "1.13.129.0"

            if "priority" in metadata:
                mod["metadata"]["priority"] = metadata["priority"]
            else:
                mod["metadata"]["priority"] = mod["filename"].split("_")[
                    0].split("-")[0]

            if "sync" in metadata:
                mod["metadata"]["sync"] = metadata["sync"]
            else:
                mod["metadata"]["sync"] = "serverclient"

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
                mod["metadata"]["linked_actor_components"] = []

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
