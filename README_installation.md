### Prerequisites

### Python Environment

cmake installation
https://apt.kitware.com/

Remove old cmake 3.10.2 
```
sudo apt remove --purge cmake
hash -r
```

Install new cmake 
```
sudo apt-get update
sudo apt-get install gpg wget
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ bionic main' | sudo tee /etc/apt/sources.list.d/kitware.list >/dev/null
sudo rm /usr/share/keyrings/kitware-archive-keyring.gpg
sudo apt-get install kitware-archive-keyring
echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ bionic-rc main' | sudo tee -a /etc/apt/sources.list.d/kitware.list >/dev/null
sudo apt-get install cmake
```


Clone Repo

```
git clone git@github.com:hlrs-vis/multi-object-multi-camera-tracker.git
cd multi-object-multi-camera-tracker/
```

Install Python 3.7

```
sudo apt-get install python3.7
sudo apt-get install python3.7-dev
apt-get install python3.7-venv
```


Sync submodules
```
git submodule sync
```

Init submodules 
```
git submodule update --init --recursive
```



Create Python virtual environment
```
python3.7 -m venv venv
```

Activate the environment inside the setup shell
```
source venv/bin/activate
```

install current pip and all required Python packages
```
pip install --upgrade pip
----pip install -r requirements.txt
```