# ghfetch
![preview](https://github.com/ghfetch/ghfetch/assets/90156486/9123b705-348b-491e-860c-f894b416ff5c)


> The previous video has as examples the commands:
>
> * `ghfetch ghfetch` - (An organization)
> * `ghfetch icutum` - (A user)
> * `ghfetch nullgaro` - (A user)
> * `ghfetch torvalds/linux` - (A repo)

## Description
A nice way to display CLI user / organization / repo info inspired in [Neofetch](https://github.com/dylanaraps/neofetch)

ghfetch is a CLI information tool written in `Python >= 3.5` that displays info about any user/org/repo you pass as argument.

Upon execution, the script displays on the terminal relevant information, like the profile picture, public repos, stars, followers, etc.

Additionally, in this project, we've used Github Actions to be able to create a new release each time we merge to main, thanks to this, the build for AUR is easier.

## Installation

### Package manager

**apt:**</br>
Firstly you have to add the repository with "add-apt-repository":
```sh
add-apt-repository "deb https://ppa.launchpadcontent.net/ghfetch/ghfetch/ubuntu/ mantic main"
apt-get update
```
If you don't have "add-apt-repository", you can install it with: 
```sh
apt-get install software-properties-common python3-launchpadlib
```
And then you can install **ghfetch**
```sh
apt-get install ghfetch
```

**Arch Linux:**</br>
Use your favorite AUR helper, i.e:
```sh
yay -Syu ghfetch
```

**Snap:**
```sh
snap install ghfetch
```

**PIP:**
```sh
pip install --upgrade pip
pip install ghfetch-pip
```
> For troubleshooting see [here](https://github.com/ghfetch/ghfetch#troubleshooting-%EF%B8%8F).

### Manual installation
```sh
git clone https://github.com/ghfetch/ghfetch.git
cd ghfetch
pip install .
```

## Usage
```sh
ghfetch <user or organization>
```

```sh
ghfetch <user>/<repo>
```

### Example usage

**User:**
```sh
ghfetch nullgaro
ghfetch icutum
```

**Organization:**
```sh
ghfetch ghfetch
ghfetch confugiradores
```

**Repo:**README.md
```sh
ghfetch torvalds/linux
ghfetch ghfetch/ghfetch
```

## To-do's 📋

### Code 💻

- [ ] Private API key for access to private repositories

### Package upload 📦

- [X] Yay
- [X] Apt
- [X] Pip
- [X] Snap
- [ ] DNF/Yum
- [ ] Brew
- [ ] Windows
- [ ] Zypper
- [ ] DPKG

### Wishlist 🥺
- [ ] Pacman

## Troubleshooting 🛠️
### Warn: `WARNING: The scripts ghfetch-pip is installed in '/home/USERNAME/.local/bin' which is not on PATH.`

If you are installing ghfetch using PIP, and you get a similar warning to this:</br>
![path_warn_preview](https://github.com/ghfetch/ghfetch/assets/90156486/11501fd4-9d46-4880-ae8d-2f750ccd8574)


The solution is to add `export PATH=/home/user/.local/bin:$PATH` to your .bashrc, where `/home/user/.local/bin` would be the path that the warning is telling you, and reboot.

### Updating ghfetch using yay doesn't update it

This issue happens because the yay's cache is interfering with the update. The solution is to clear the cache of yay with `yay -Sc --aur`.

### When adding the repository to apt gets some pythonic error

![python_error](https://github.com/ghfetch/ghfetch/assets/90156486/f2694b45-a51f-4b5b-aa91-b43b8bc54782)

This issue happens because `apt-add-repository` is missing `python3-launchpadlib`. The solution is to install it with `apt-get install python3-launchpadlib`.

## People 👨‍💻
This project was developed with ❤️ by [Nullgaro](https://github.com/nullgaro) and [Icutum](https://github.com/icutum).

[![Nullgaro](https://avatars.githubusercontent.com/nullgaro?size=40)](https://github.com/nullgaro)[![Mariolo](https://avatars.githubusercontent.com/icutum?size=40)](https://github.com/icutum)

## Support ❤️
If you find our ghfetch script helpful and want to contribute to its development and maintenance, consider buying us a coffee! ☕</br> Your support means a lot!</br></br>
[![shield](https://img.shields.io/badge/buymeacoffee-donate-yellow)](https://bmc.link/ghfetch)
