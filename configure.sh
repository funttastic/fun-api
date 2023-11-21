#!/bin/bash

cd resources/configuration
cp production.example.yml production.yml

# Define a variable to store the password
password=""

# Define a variable to store the attempt count
attempt_count=1

# Prompt the user for the password
while [ -z "$password" ] || [ ${#password} -lt 4 ]; do
  # Clear the screen
  clear

  # If the attempt is greater than 1, show the counter
  if [ $attempt_count -gt 1 ]; then
    echo
    echo "Enter a password with at least 4 characters [Tentative #$attempt_count] Try again:"
  else
    echo
    echo "Enter a password with at least 4 characters:"
  fi

  read -s -p " " password

  # Increment the counter
  attempt_count=$((attempt_count + 1))
done

# Export the environment variable
export GATEWAY_PASSPHRASE=$password

# Confirm the operation with the user
read -p "Confirm exporting the password? (y/n) " response

# If the user responds yes, proceed with the export
if [[ $response == "y" ]]; then
  # Ask the user if they want to add the export line to .bashrc or .zshrc
  read -p "Do you want to add the export line to .bashrc or .zshrc? (y/n) " export_to_rc

  # If the user responds yes, add the export line to the configuration file of the interpreter
  if [[ $export_to_rc == "y" ]]; then
    shell=${SHELL##*/}

    # Check which shell the user is using
    case $shell in
      bash)
        file=".bashrc"
        ;;
      zsh)
        file=".zshrc"
        ;;
      fish)
        file=".config/fish/config.fish"
        ;;
      elvish)
        file=".config/elvish/init.elvish"
        ;;
      powershell)
        file=".profile"
        ;;
      *)
        echo "Shell not supported."
        exit 1
        ;;
    esac

    # Add the export line to the end of the file
    echo "" >> "$HOME/$file"
    echo "export GATEWAY_PASSPHRASE=\"$password\"" >> "$HOME/$file"
    echo "" >> "$HOME/$file"
  fi

  echo
  echo "Password exported successfully!"
fi
