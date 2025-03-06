import os
import sys
import pathspec

def read_gitignore(input_dir):
    """
    Reads the .gitignore file in the input directory and returns a pathspec object.
    """
    # Default patterns to always ignore
    default_patterns = [
        "migrations/*.py",  # Ignore Django migration files
        "node_modules/",    # Ignore node_modules directory
    ]
    
    gitignore_path = os.path.join(input_dir, ".gitignore")
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, "r") as gitignore_file:
            patterns = default_patterns + list(gitignore_file)
            return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    else:
        return pathspec.PathSpec.from_lines("gitwildmatch", default_patterns)

def should_ignore_path(path, gitignore_spec):
    """
    Additional check for paths that should be ignored.
    """
    # Check if the path contains node_modules or migrations directory
    if "node_modules" in path.split(os.sep) or \
       ("migrations" in path.split(os.sep) and path.endswith(".py")):
        return True
    return gitignore_spec.match_file(path)

def structure_directory_content(input_dir, output_file=None, extensions=None):
    """
    This function goes through the input directory recursively and structures
    all the file contents into one output file based on the given extensions.
    :param input_dir: The input directory to search for files.
    :param output_file: The output file where the content will be structured.
                        If None, 'data.txt' or 'data.<extension>' will be used.
    :param extensions: A list of file extensions to include. If None, all files are included.
    """
    gitignore_spec = read_gitignore(input_dir)

    if extensions:
        extensions = [ext.strip() for ext in extensions.split(",") if ext.strip() != ""]
        if not output_file and len(extensions) == 1:
            output_file = f"data.{extensions[0]}"
    else:
        extensions = None

    if not output_file:
        output_file = "data.txt"

    with open(output_file, "w") as outfile:
        for root, dirs, files in os.walk(input_dir):
            # Filter files and directories using the enhanced ignore check
            files = [
                f for f in files
                if not should_ignore_path(os.path.join(root, str(f)), gitignore_spec)
            ]
            
            # Filter directories in-place
            dirs[:] = [
                d for d in dirs
                if not should_ignore_path(os.path.join(root, str(d)), gitignore_spec)
            ]

            for file in files:
                if extensions is None or any(
                    file.endswith(f".{ext}") for ext in extensions
                ):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as infile:
                            data = infile.read()
                            outfile.write(
                                f"# {os.path.relpath(file_path, input_dir)}\n"
                            )
                            outfile.write(data)
                            outfile.write("\n\n")
                    except UnicodeDecodeError:
                        continue

if __name__ == "__main__":
    if len(sys.argv) == 1:
        input_directory = input("directory path: ")
        output_filename = input("output file name (optional): ")
        file_extensions = input("file extensions separated by commas (optional): ")
        structure_directory_content(
            input_directory,
            output_filename if output_filename else None,
            file_extensions if file_extensions else None,
        )
    else:
        input_directory = sys.argv[1] if len(sys.argv) > 1 else "."
        output_filename = sys.argv[2] if len(sys.argv) > 2 else None
        file_extensions = sys.argv[3] if len(sys.argv) > 3 else None
        structure_directory_content(input_directory, output_filename, file_extensions)
