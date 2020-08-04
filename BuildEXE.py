import PyInstaller.__main__
import os
import shutil


# pyinstaller AstroLauncher.py -F --add-data "assets/*;." --icon=assets/astrolauncherlogo.ico

PyInstaller.__main__.run([
    '--name=%s' % "AstroModLoader",
    '--onefile',
    #'--add-data=%s' % "assets;./assets",
    #'--icon=%s' % "assets/astrolauncherlogo.ico",
    'AstroModLoader.py'
])

shutil.rmtree("build")
os.remove("AstroModLoader.spec")
