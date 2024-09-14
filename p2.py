import subprocess
import xml.etree.ElementTree as ET
import difflib

def compare_files(xml_file, xlm_file):
    with open(xml_file, 'r') as f1, open(xlm_file, 'r') as f2:
        f1_content = f1.readlines()
        f2_content = f2.readlines()

    diff = difflib.unified_diff(f1_content, f2_content, lineterm='')

    differences = list(diff)
    if len(differences) == 0:
        return "Files are equal"
    else:
        return "\n".join(differences)

def get_des(command):
    try:
        # Execute the command with '--help'
        process = subprocess.Popen([command, '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()

        if process.returncode != 0:
            # Handling the case where the command fails
            return f"Error occurred: {error.strip()}"

        # Returning only the first three lines of the output as the description
        return '\n'.join(output.strip().split('\n')[:3])

    except Exception as e:
        # Handle any exceptions that occur
        return f"An exception occurred: {str(e)}"


def get_description(command):
    try:
        # Execute the command with '--help'
        process = subprocess.Popen([command, '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()

        if process.returncode != 0:
            # Handling the case where the command fails
            return f"Error occurred: {error.strip()}"

        # Returning only the first three lines of the output as the description
        return '\n'.join(output.strip().split('\n')[:3])

    except Exception as e:
        # Handle any exceptions that occur
        return f"An exception occurred: {str(e)}"


def get_version(command):
    try:
        # Attempt to get version information using common version flags
        version_flags = ['--version', '-v', '-V']

        for flag in version_flags:
            process = subprocess.run([command, flag], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # If the command executed successfully, return the first line of the output
            if process.returncode == 0:
                return process.stdout.strip().split('\n')[0]

        # If none of the flags worked, return an informative message
        return "Version information not available or command does not support version flags."

    except Exception as e:
        # Handle any exceptions that occur
        return f"An exception occurred: {str(e)}"


def get_example(command):
    try:
        examples = {
            "touch": "touch example.txt",
            "ls": "ls -l",
            "cat": "cat file.txt",
            "echo": "echo 'Hello World'",
            "head": "head -n 1 /etc/passwd",
            "tail": "tail -n 1 /etc/passwd",
            "date": "date",
            "cut": "echo 'sample text' | cut -f1 -d ' '",
            "sed": "echo 'sample time' | sed 's/time/TIME/'",
            "tr": "echo 'hello' | tr 'lo' 'LO'",
            "pwd": "pwd",
            "wc": "echo 'hello world' | wc",
            "sort": "echo -e '3\n1\n2' | sort"
        }

        if command not in examples:
            return "No example available for this command."

        example_command = examples[command]
        # Run the example command with a timeout
        output = subprocess.run(example_command, shell=True, capture_output=True, text=True, timeout=5)

        if output.returncode == 0:
            return f"EXAMPLE for {command}\n\t{example_command}\n{output.stdout}"
        else:
            return f"Error running example for {command}\n\t{example_command}\n{output.stderr}"

    except subprocess.TimeoutExpired:
        return "A command timed out."
    except Exception as e:
        return f"An exception occurred: {str(e)}"

def get_related(command):
    try:
        # Use 'compgen -c' to find commands with similar names
        related_command_output = subprocess.check_output(f'compgen -c {command}', shell=True,executable='/bin/bash').decode('utf-8')

        # Filter the list to remove the command itself and any empty lines
        related_commands = [cmd for cmd in related_command_output.split('\n') if cmd and cmd != self.command]

        return '\n'.join(related_commands) if related_commands else "No related commands available"

    except subprocess.CalledProcessError:
        return "Failed to fetch related commands using 'compgen -c'."
    except Exception as e:
        return f"An exception occurred: {str(e)}"


def create_xml_file(command, description, version, example, related):
    root = ET.Element("Command", name=command)

    ET.SubElement(root, "Description").text = description
    ET.SubElement(root, "Version").text = version
    ET.SubElement(root, "Example").text = example
    ET.SubElement(root, "Related").text = related

    tree = ET.ElementTree(root)
    xml_content = ET.tostring(root, encoding='unicode')  # Convert the XML content to a string

    # Debugging: Print the content that will be written to the files
    print(f"Content for {command}:")

    # Write the content to both files
    with open(f"{command}.xml", "w") as f:
        f.write(xml_content)
    with open(f"{command}_test.xlm", "w") as f:
        f.write(xml_content)

def read_commands_from_file(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]


def main():
    # Path to the file containing the list of commands
    commands_file_path = ".venv/list_of_commands.txt"
    commands = read_commands_from_file(commands_file_path)

    for command in commands:
        description = get_description(command)
        version = get_version(command)
        example = get_example(command)
        related = get_related(command)

        # Create a test XML file for each command
        create_xml_file(command, description, version, example, related)

        # Compare the original XML file with the test XML file
        original_file = f"{command}.xml"
        test_file = f"{command}_test.xlm"
        comparison_result = compare_files(original_file, test_file)

        # Print only the equality or difference status
        if comparison_result == "Files are equal":
            print(f"{command}: Files are equal.")
        else:
            print(f"{command}: Files are different.")

if __name__ == "__main__":
    main()