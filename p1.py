import subprocess
import xml.etree.ElementTree as ET

class CommandManual:
    def __init__(self, command):
        self.command = command

    def get_description(self):
        try:
            # Execute the command with '--help'
            process = subprocess.Popen([self.command, '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()

            if process.returncode != 0:
                # Handling the case where the command fails
                return f"Error occurred: {error.strip()}"

            # Returning only the first three lines of the output as the description
            return '\n'.join(output.strip().split('\n')[:3])

        except Exception as e:
            # Handle any exceptions that occur
            return f"An exception occurred: {str(e)}"

    def get_version(self):
        try:
            # Attempt to get version information using common version flags
            version_flags = ['--version', '-v', '-V']

            for flag in version_flags:
                process = subprocess.run([self.command, flag], stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

                # If the command executed successfully, return the first line of the output
                if process.returncode == 0:
                    return process.stdout.strip().split('\n')[0]

            # If none of the flags worked, return an informative message
            return "Version information not available or command does not support version flags."

        except Exception as e:
            # Handle any exceptions that occur
            return f"An exception occurred: {str(e)}"

    def get_example(self):
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

            if self.command not in examples:
                return "No example available for this command."

            example_command = examples[self.command]
            # Run the example command with a timeout
            output = subprocess.run(example_command, shell=True, capture_output=True, text=True, timeout=5)

            if output.returncode == 0:
                return f"EXAMPLE for {self.command}\n\t{example_command}\n{output.stdout}"
            else:
                return f"Error running example for {self.command}\n\t{example_command}\n{output.stderr}"

        except subprocess.TimeoutExpired:
            return "A command timed out."
        except Exception as e:
            return f"An exception occurred: {str(e)}"

    def get_related(self):
        try:
            # Use 'compgen -c' to find commands with similar names
            related_command_output = subprocess.check_output(f'compgen -c {self.command}', shell=True, executable='/bin/bash').decode('utf-8')

            return related_command_output

        except subprocess.CalledProcessError:
            return "Failed to fetch related commands using 'compgen -c'."
        except Exception as e:
            return f"An exception occurred: {str(e)}"

    def get_documentation_link(self):
        try:
            doc_command_output = subprocess.check_output(f'{self.command} --help | grep -A 2 "Full documentation"',shell=True,executable='/bin/bash').decode('utf-8')

            # Filter the list to remove any empty lines
            doc_commands = [cmd for cmd in doc_command_output.split('\n') if cmd and cmd != self.command]

            return '\n'.join(doc_commands) if doc_commands else "No documentation for command available"

        except subprocess.CalledProcessError:
            return "Failed to fetch documentation commands."
        except Exception as e:
            return f"An exception occurred: {str(e)}"

    def get_syntax(self):
        try:
            syntax_command_output = subprocess.check_output(f'man {self.command} | grep -A 2 SYNOPSIS',shell=True,executable='/bin/bash').decode('utf-8')

            return syntax_command_output.strip()

        except subprocess.CalledProcessError:
            return "Failed to fetch syntax commands."
        except Exception as e:
            return f"An exception occurred: {str(e)}"

    def create_xml_file(self):
        description = self.get_description()
        version = self.get_version()
        example = self.get_example()
        related = self.get_related()
        syntax = self.get_syntax()
        documentation_link = self.get_documentation_link()

        root = ET.Element("Command", name=self.command)

        ET.SubElement(root, "Description").text = description
        ET.SubElement(root, "Version").text = version
        ET.SubElement(root, "Example").text = example
        ET.SubElement(root, "Related").text = related
        ET.SubElement(root, 'Syntax').text = syntax
        ET.SubElement(root, "DocumentationLink").text = documentation_link

        tree = ET.ElementTree(root)
        tree.write(f"{self.command}.xml")



class CommandManualGenerator:
    def __init__(self, commands_file_path):
        with open(commands_file_path, 'r') as file:
            self.commands = [line.strip() for line in file.readlines()]

    def generate_manuals(self):
        for command in self.commands:
            try:
                manual = CommandManual(command)
                xml_content = XmlSerializer(manual).serialize()
                with open(f"{command}.xml", "w") as f:
                    f.write(xml_content)
                print(f"Manual generated for command: {command}")
            except Exception as e:
                print(f"Failed to generate manual for command '{command}': {e}")


class XmlSerializer:
    def __init__(self, command_manual):
        self.command_manual = command_manual

    def serialize(self):
        root = ET.Element("Command", name=self.command_manual.command)

        ET.SubElement(root, "Description").text = self.command_manual.get_description()
        ET.SubElement(root, "Version").text = self.command_manual.get_version()
        ET.SubElement(root, "Example").text = self.command_manual.get_example()
        ET.SubElement(root, "Related").text = self.command_manual.get_related()
        ET.SubElement(root, 'Syntax').text = self.command_manual.get_syntax()
        ET.SubElement(root, "DocumentationLink").text = self.command_manual.get_documentation_link()

        return ET.tostring(root, encoding='unicode')


class CommandRecommender:
    def __init__(self):
        self.commands_db = {
        "touch": {
            "functionality": "create a new file",
            "related_commands": ["mkdir", "rm", "nano"]
        },
        "ls": {
            "functionality": "list directory contents",
            "related_commands": ["cd", "pwd"]
        },
        "cat": {
            "functionality": "Display Contents",
            "related_commands": ["less", "head", "tail"]
        },
        "echo": {
            "functionality": "print",
            "related_commands": ["printf", "read"]
        },
        "head": {
            "functionality": "top content",
            "related_commands": ["tail", "less", "more"]
        },
        "tail": {
            "functionality": "bottom content",
            "related_commands": ["head", "less", "more"]
        },
        "date": {
            "functionality": "show Date",
            "related_commands": ["cal", "clock", "uptime"]
        },
        "cut": {
            "functionality": "Extract Text",
            "related_commands": ["awk", "grep", "sed"]
        },
        "sed": {
            "functionality": "Stream Edit",
            "related_commands": ["awk", "grep", "tr"]
        },
        "tr": {
            "functionality": "Translate Characters",
            "related_commands": ["sed", "awk", "grep"]
        },
        "pwd": {
            "functionality": "Print Directory",
            "related_commands": ["cd", "ls", "mkdir"]
        },
        "wc": {
            "functionality": "Word Count",
            "related_commands": ["cat", "sort", "uniq"]
        },
        "sort": {
            "functionality": "Sort Data",
            "related_commands": ["uniq", "awk", "grep"]
        }
    }

    def recommend_commands(self, command):
        command_info = self.commands_db.get(command, None)
        if command_info:
            recommendations = "You may also be interested in:\n"
            for related_command in command_info["related_commands"]:
                recommendations += f"- {related_command}\n"
            return recommendations
        return "No related commands found.\n"


class CommandManager:
    def __init__(self, commands):
        self.commands = commands
        self.recommender = CommandRecommender()  # Assuming you have a CommandRecommender class

    def display_command(self, command):
        try:
            tree = ET.parse(f"{command}.xml")
            root = tree.getroot()

            print(f"Details for command '{command}':")
            for child in root:
                print(f"{child.tag}: {child.text}")
            print("\n")
        except FileNotFoundError:
            print(f"Please try again, No manual entry found for command '{command}'.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def list_commands(self):
        print("List of available commands:")
        print(", ".join(self.commands))

    def recommend_commands(self, command):
        print(self.recommender.recommend_commands(command))


def main():
    # Path to the file containing the list of commands
    commands_file_path = ".venv/list_of_commands.txt"
    command_generator = CommandManualGenerator(commands_file_path)
    command_generator.generate_manuals()

    # Initialize CommandManager with the list of commands
    command_manager = CommandManager(command_generator.commands)

    while True:
        user_input = input("Do you want to see the list of all commands? (yes/no): ").strip().lower()
        if user_input in ['yes', 'y']:
            command_manager.list_commands()

            cmd_input = input("Enter a command to view its details or 'exit' to quit: ").strip().lower()
            if cmd_input == 'exit':
                print("thank you :) ")
                break
            if cmd_input in command_manager.commands:
                command_manager.display_command(cmd_input)

                show_recommend = input("Would you like to see related command recommendations? (yes/no): ").strip().lower()
                if show_recommend in ['yes', 'y']:
                    command_manager.recommend_commands(cmd_input)
                elif show_recommend in ['no', 'n']:
                    print("Thank you")
                else:
                    print("Invalid input! Please enter 'yes' or 'no'.")
            else:
                print("Command not found. Please try again.")
        elif user_input in ['no', 'n']:
            print("Thank you, come again.")
            break
        else:
            print("Invalid input! Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()

