#!/bin/bash

generate_password() {
    local length=$1
    local charset="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+[]{}|;:',.<>/?"
    local password=""
    local charset_length=${#charset}
    local max_random=$((32768 - 32768 % charset_length))

    for ((i = 0; i < length; i++)); do
        while (( (random_index=RANDOM) >= max_random )); do :; done
        random_index=$((random_index % charset_length))
        password="${password}${charset:$random_index:1}"
    done

    echo "$password"
}

echo
echo
echo "===============  CREATE A NEW KUJIRA HB CLIENT INSTANCE ==============="
echo
echo
echo "ℹ️  Press [ENTER] for default values:"
echo

if [ ! "$DEBUG" == "" ]
then
	docker stop temp-kujira-hb-client
	docker rm temp-kujira-hb-client
	docker rmi temp-kujira-hb-client
	docker commit kujira-hb-client temp-kujira-hb-client
fi

CUSTOMIZE=$1

DOCKER_INSTALLED=0

# Customize the Client image to be used?
if [ "$CUSTOMIZE" == "--customize" ]
then
  RESPONSE="$IMAGE_NAME"
  if [ "$RESPONSE" == "" ]
  then
    read -p "   Enter Kujira HB Client image you want to use (default = \"kujira-hb-client\") >>> " RESPONSE
  fi
  if [ "$RESPONSE" == "" ]
  then
    IMAGE_NAME="kujira-hb-client"
  else
    IMAGE_NAME="$RESPONSE"
  fi

  # Specify a Kujira HB Client version?
  RESPONSE="$TAG"
  if [ "$RESPONSE" == "" ]
  then
    read -p "   Enter Kujira HB Client version you want to use [latest/development] (default = \"latest\") >>> " TAG
  fi
  if [ "$RESPONSE" == "" ]
  then
    TAG="latest"
  else
    TAG=$RESPONSE
  fi

  # Create a new Client image?
  RESPONSE="$BUILD_CACHE"
  if [ "$RESPONSE" == "" ]
  then
    read -p "   Do you want to use an existing Kujira HB Client image (\"y/N\") >>> " RESPONSE
  fi
  if [[ "$RESPONSE" == "N" || "$RESPONSE" == "n" || "$RESPONSE" == "" ]]
  then
    echo "   A new image will be created..."
    BUILD_CACHE="--no-cache"
  else
    BUILD_CACHE=""
  fi

  # Create a new Client instance?
  RESPONSE="$INSTANCE_NAME"
  if [ "$RESPONSE" == "" ]
  then
    read -p "   Enter a name for your new Kujira HB Client instance (default = \"kujira-hb-client\") >>> " RESPONSE
  fi
  if [ "$RESPONSE" == "" ]
  then
    INSTANCE_NAME="kujira-hb-client"
  else
    INSTANCE_NAME=$RESPONSE
  fi

  # Prompt the user for the password to encrypt the certificates
  while true; do
      read -s -p "   Enter a password to encrypt the certificates with at least 4 characters >>> " GATEWAY_PASSPHRASE
      if [ -z "$GATEWAY_PASSPHRASE" ] || [ ${#GATEWAY_PASSPHRASE} -lt 4 ]; then
          echo
          echo "   Weak password, please try again."
      else
          echo
          break
      fi
  done

  # Location to save files?
  RESPONSE="$FOLDER"
  if [ "$RESPONSE" == "" ]
  then
    FOLDER_SUFFIX="shared"
    read -p "   Enter a folder name where your Kujira HB Client files will be saved (default = \"$FOLDER_SUFFIX\") >>> " RESPONSE
  fi
  if [ "$RESPONSE" == "" ]
  then
    FOLDER=$PWD/$FOLDER_SUFFIX
  elif [[ ${RESPONSE::1} != "/" ]]; then
    FOLDER=$PWD/$RESPONSE
  else
    FOLDER=$RESPONSE
  fi
else
  RANDOM_PASSPHRASE=$(generate_password 32)

	if [ ! "$DEBUG" == "" ]
	then
		IMAGE_NAME="temp-kujira-hb-client"
		TAG="latest"
		BUILD_CACHE="--no-cache"
		INSTANCE_NAME="temp-kujira-hb-client"
		FOLDER_SUFFIX="shared"
		FOLDER=$PWD/$FOLDER_SUFFIX
		ENTRYPOINT="--entrypoint=/bin/bash"
	else
		IMAGE_NAME="kujira-hb-client"
		TAG="latest"
		BUILD_CACHE="--no-cache"
		INSTANCE_NAME="kujira-hb-client"
		FOLDER_SUFFIX="shared"
		FOLDER=$PWD/$FOLDER_SUFFIX
	fi
fi

RESOURCES_FOLDER="$FOLDER/kujira/client/resources"
# CERTS_FOLDER="$FOLDER/common/certificates"

echo
echo "ℹ️  Confirm below if the instance and its folders are correct:"
echo
printf "%30s %5s\n" "Instance name:" "$INSTANCE_NAME"
printf "%30s %5s\n" "Version:" "kujira-hb-client/kujira-hb-client:$TAG"
echo
printf "%30s %5s\n" "Main folder:" "├── $FOLDER"
printf "%30s %5s\n" "Resources files:" "├── $RESOURCES_FOLDER"
# printf "%30s %5s\n" "Certificates files:" "├── $CERTS_FOLDER"
echo

prompt_proceed () {
  RESPONSE=""
  read -p "   Do you want to proceed? [Y/n] >>> " RESPONSE
  if [[ "$RESPONSE" == "Y" || "$RESPONSE" == "y" || "$RESPONSE" == "" ]]
  then
    PROCEED="Y"
  fi
}

# Execute docker commands
create_instance () {
  echo
  echo "Creating kujira-hb-client instance..."
  echo
  # 1) Create main folder for your new instance
  mkdir -p $FOLDER
  # 2) Create subfolders for kujira-hb-client files
  mkdir -p $RESOURCES_FOLDER
  # mkdir -p $CERTS_FOLDER

  # 3) Set required permissions to save kujira-hb-client password the first time
  # chmod a+rw $CONF_FOLDER

  # 4) Install Docker if necessary

  # Detecting the architecture
  ARCHITECTURE="$(uname -m)"

  # Function to check if Docker is installed
  check_docker_installed() {
      if [ -x "$(command -v docker)" ]; then
          echo "Docker is already installed. Skipping installation."
          DOCKER_INSTALLED=1
          return 1
      else
          return 0
      fi
  }

  # Detecting the operating system and setting up Docker installation
  case $(uname | tr '[:upper:]' '[:lower:]') in
      linux*)
          OS="Linux"
          # Check if Docker is installed
          if check_docker_installed; then
              # Installation for Debian-based distributions (like Ubuntu)
              if [ -f /etc/debian_version ]; then
                  # Update and install prerequisites
                  sudo apt-get update
                  sudo apt-get install -y ca-certificates curl gnupg
                  sudo install -m 0755 -d /etc/apt/keyrings

                  # Add Docker's official GPG key
                  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
                  sudo chmod a+r /etc/apt/keyrings/docker.gpg

                  # Set up the stable repository
                  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME")" stable | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

                  # Install Docker Engine
                  sudo apt-get update
                  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
              elif [ -f /etc/redhat-release ]; then
                  # Installation for Red Hat-based distributions (like CentOS)
                  sudo yum install -y yum-utils
                  sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                  sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
              else
                  echo "Unsupported Linux distribution"
                  exit 1
              fi
          fi
          ;;
      darwin*)
          # Installation of Docker for macOS
          OS="MacOSX"
          if check_docker_installed; then
              curl -L "https://download.docker.com/mac/stable/Docker.dmg" -o /tmp/Docker.dmg
              hdiutil attach /tmp/Docker.dmg
              cp -R /Volumes/Docker/Docker.app /Applications
              hdiutil detach /Volumes/Docker
          fi
          ;;
      msys*|cygwin*|mingw*)
          # Installation of Docker for Windows (assuming in an environment like Git Bash)
          OS="Windows"
          if check_docker_installed; then
              echo "To install Docker on Windows, please download and install manually from: https://hub.docker.com/editions/community/docker-ce-desktop-windows/"
          fi
          ;;
      *)
          echo "Unrecognized operating system"
          exit 1
          ;;
  esac

  echo "Operating System: $OS"
  echo "Architecture: $ARCHITECTURE"

  sudo groupadd docker
  sudo usermod -aG docker $USER
  sudo chmod 666 /var/run/docker.sock
  sudo systemctl restart docker

  # 5) Create a new image for kujira-hb-client
  BUILT=true
  if [ ! "$BUILD_CACHE" == "" ]
  then
    BUILT=$(DOCKER_BUILDKIT=1 docker build --build-arg RANDOM_PASSPHRASE=$RANDOM_PASSPHRASE $BUILD_CACHE -t $IMAGE_NAME -f ./docker/Dockerfile .)
  fi

  # $BUILT && docker volume create resources

  # 5) Launch a new gateway instance of kujira-hb-client
  # USER=$(whoami)
  # GROUP=$(id -gn)
  $BUILT \
  && docker run \
    -it \
    --log-opt max-size=10m \
    --log-opt max-file=5 \
    --name $INSTANCE_NAME \
    --network host \
    -v $RESOURCES_FOLDER:/root/app/resources \
    --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
    -e RESOURCES_FOLDER="/root/app/resources" \
    -e GATEWAY_PASSPHRASE=$GATEWAY_PASSPHRASE \
    $ENTRYPOINT \
    $IMAGE_NAME:$TAG
}

if [ ! "$DOCKER_INSTALLED" == 0 ]
  then
  echo "Resources volume was created"
  $BUILT && docker volume create resources
fi

if [ "$CUSTOMIZE" == "--customize" ]
then
  prompt_proceed
  if [[ "$PROCEED" == "Y" || "$PROCEED" == "y" ]]
  then
   create_instance
  else
   echo "   Aborted"
   echo
  fi
else
  create_instance
fi
