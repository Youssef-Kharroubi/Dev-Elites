# Setting up the Environement 
### First we should update our system 
```
sudo apt update
``` 
### Second we need git 
```
sudo apt install -y git
```
## Then we clone our Project

### We need to install docker 
```
sudo apt install -y docker.io
```
### Start docker 
```
sudo systemctl start docker
sudo systemctl enable docker
```
### we need to add the system user to the docker group
```
sudo usermod -aG docker $USER
```
#### Verify docker is installed
```
docker --version 
```
You should see something like this as a result ```Docker version 24.0.6```
## Since our project is going to work on images and according to our resources, we need to install NVIDIA Container Toolkit
```
sudo apt install -y nvidia-driver-535  # Adjust version for resource type 
```
```
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
```
### Next we are going to configure docker to use NVIDIA runtime 
```
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```
#### let's test our configuration
```
docker run --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```
# We shouldn't forget the datasets
``` 
cp -r /path/to/dataset ~/ocr_project/dataset
```
### Navigate to dockerfile and build the image
```
docker build -t ocr-image:v1 .
```
### Run docker container 
```
docker run --gpus all -it -v ~/ocr_project/backend:/app/backend -v ~/ocr_project/dataset:/app/dataset ocr-image:v1
```
