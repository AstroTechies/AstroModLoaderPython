<h3 align="center">AstroModLoader - Manage, integrate and update Astroneer Mods</h3>

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

This tool is manages your Astronner Mods in UE4 pak file form.<br />
Thanks to atenfyr for making the mod integrator part.

## What does it do?

1. Allows you to manage your mods
2. Takes care of mod integration
3. Updates your mods
4. Downloads mods for one dedicated server

## TODO

- get server mods
- button for more info on one mod
- show all available versions

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps or check the [Latest Release](https://github.com/AstroTechies/AstroModLoader/releases/latest) for a download of the executable.

### Prerequisites

- Python 3.8
- pip / pipenv

### Installation

1. Clone the AstroModLoader repository

```sh
git clone https://github.com/AstroTechies/AstroModLoader.git
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

1. If you want to turn this project into an executable, make sure to install pyinstaller and run

```sh
python BuildEXE.py
```

2. Move the executable (in the new `dist` folder) to the directory of your choice. (If you want you can now delete the `dist` and `build` folders, as well as the `.spec` file)
3. Run AstroModLoader.exe

```sh
./AstroModLoader.exe [--no-gui]
```

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
