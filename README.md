<h3 align="center">AstroModLoader - Download and update Astroneer Mods</h3>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [What does it do?](#what-does-it-do)
- [TODO](#todo)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Building an EXE](#building-an-exe)
- [Contributing](#contributing)
<!-- [License](#license)
- [Contact](#contact)-->

## Overview

This tool is manages your Astronner Mods in UE4 pak file form.

## What does it do?

1. Updates your mods
2. Downloads mods for one dedicated server

## TODO

1. auto update mods
2. mod integration
3. get server mods

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps or check the [Latest Release](https://github.com/konsti219/AstroModLoader/releases/latest) for a download of the executable.

### Prerequisites

- Python 3.8
- pip / pipenv

### Installation

1. Clone the AstroModLoader repository

```sh
git clone https://github.com/konsti219/AstroModLoader.git
```

2. Install python modules using pip or pipenv

```sh
pip install -r requirements.txt
```

```sh
pipenv install
```

<br />

<!-- USAGE EXAMPLES -->

## Usage

Run the mod loader using the following command

```sh
pipenv run python AstroModLoader.py
```

### Building an EXE

1. If you want to turn this project into an executable, make sure to install pyinstaller using one of the following methods
<!--

```sh
pip install pyinstaller
```

```sh
pipenv install -d
```

2. Run pyinstaller with the all-in-one flag

```sh
pyinstaller AstroLauncher.py -F --add-data "assets;./assets" --icon=assets/astrolauncherlogo.ico
```

or -->
just run the BuildEXE.py which automatically cleans up afterwards

```sh
python BuildEXE.py
```

<!--
1. Move the executable (in the new `dist` folder) to the directory of your choice. (If you want you can now delete the `dist` and `build` folders, as well as the `.spec` file)
2. Run AstroLauncher.exe

```sh
AstroLauncher.exe -p "steamapps\common\ASTRONEER Dedicated Server"
```-->

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
