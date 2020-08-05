import os
import numpy

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

        # gather mod list
        self.mods = numpy.unique(self.getPaksInPath(
            self.downloadPath) + self.getPaksInPath(self.installPath))

        self.mods = list(map(lambda m: {"filename": m}, self.mods))

        print(self.mods)
        # TODO check each mod where it is present
        for mod in self.mods:
            pass

        # TODO read all data into a dict

        # TODO copy mods only in path to download path

        # TODO clear mod path

        # TODO download updates

        # refresh {
        # TODO load all previously active mods back into mod path

        # TODO do mod integration
        # }

        # TODO start cli for moving mods and server config, do refresh

        # self.installedMods =

        """print(self.installedMods)

        for modName in self.installedMods:
            print(modName)

            PP = PakParser(os.path.join(self.installPath, modName))
            try:
                PP = PakParser(os.path.join(self.installPath, modName))
                metadataFile = [
                    x.Data for x in PP.records if x.fileName == "metadata.json"]
                ppData = ""
                if len(metadataFile) > 0:
                    ppData = metadataFile[0]
                print(ppData)
            except:
                pass"""

    def getPaksInPath(self, path):
        paks = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and os.path.splitext(os.path.join(path, f))[1] == ".pak":
                paks.append(f)

        return paks


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
