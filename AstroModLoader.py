import os

from cogs.AstroModPak import PakParser
import cogs.AstroAPI as AstroAPI


class AstroModLoader():

    def __init__(self):
        print("Astro mod loader v0.1")

        self.downloadPath = os.getcwd()
        if not os.path.exists(os.path.join(self.downloadPath, "mods")):
            os.makedirs(os.path.join(self.downloadPath, "mods"))
        self.downloadPath = os.path.join(self.downloadPath, "mods")

        self.modPath = os.path.join(
            os.getenv('LOCALAPPDATA'), "Astro", "Saved")
        if not os.path.exists(os.path.join(self.modPath, "Paks")):
            os.makedirs(os.path.join(self.modPath, "Paks"))
        self.modPath = os.path.join(self.modPath, "Paks")

        print(self.modPath)

        self.installedMods = [
            f for f in os.listdir(self.modPath) if os.path.isfile(os.path.join(self.modPath, f))]

        for modName in self.installedMods:
            print(modName)

            PP = PakParser(os.path.join(self.modPath, modName))
            print(PP.data)


if __name__ == "__main__":
    try:
        os.system("title AstroLauncher - Unofficial Dedicated Server Launcher")
    except:
        pass
    try:
        AstroModLoader()
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print("ERROR")
        print(err)
