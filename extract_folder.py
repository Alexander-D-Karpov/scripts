import os
import sys


def structure_directory_content(input_dir, output_file=None, extensions=None):
    """
    This function goes through the input directory recursively and structures
    all the file contents into one output file based on the given extensions.

    :param input_dir: The input directory to search for files.
    :param output_file: The output file where the content will be structured.
                        If None, 'data.txt' or 'data.<extension>' will be used.
    :param extensions: A list of file extensions to include. If None, all files are included.
    """
    if extensions:
        extensions = [ext.strip() for ext in extensions.split(",") if ext.strip() != ""]
        # If only one extension is given and no output file is specified, use 'data.<extension>'
        if not output_file and len(extensions) == 1:
            output_file = f"data.{extensions[0]}"
    else:
        extensions = None

    # If no output file is specified, default to 'data.txt'
    if not output_file:
        output_file = "data.txt"

    with open(output_file, "w") as outfile:
        for root, dirs, files in os.walk(input_dir):
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
