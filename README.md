# ghfetch
A nice way to display CLI user / organization / repo info inspired in [Neofetch](https://github.com/dylanaraps/neofetch)

ghfetch is a CLI information tool written in `Python >=3.11` that displays info about any user/org/repo you pass as argument.

Upon execution, the script displays on the terminal relevant information, like the profile picture, public repos, stars, followers, etc.

## Installation

### Package manager

**Arch Linux:**
```sh
yay -S ghfetch

**PIP:**
```sh
pip install ghfetch-pip
```
```

### Manual installation
```sh
git clone https://github.com/ghfetch/ghfetch.git
cd ghfetch
pip3 install -i requirements.txt
```

**Optional:** add as a linux command
```sh
cp main.py /usr/bin/ghfetch
chmod +x /usr/bin/ghfetch
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
ghfetch confugiradores
```

**Repo:**
```sh
ghfetch torvalds/linux
ghfetch ghfetch/ghfetch
```


## To-do's 📋

### Code 💻

- [ ] Private API key for access to private repositories

### Package upload 📦

- [X] Yay
- [ ] Apt
- [X] Pip
- [ ] Snap
- [ ] DNF/Yum
- [ ] Brew
- [ ] Windows
- [ ] Zypper
- [ ] DPKG

### Wishlist 🥺
- [ ] Pacman


## People 👨‍💻
This project was developed with ❤️ by [Nullgaro](https://github.com/nullgaro) and [Icutum](https://github.com/icutum).