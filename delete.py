import os
import shutil

# Specify the directory to delete files from
dir_path = 'processed'

# Check if the directory exists
if os.path.exists(dir_path):
    # Iterate over all the files in the directory
    for filename in os.listdir(dir_path):
        # Create the full file path
        file_path = os.path.join(dir_path, filename)
        
        # Check if it's a file or a directory
        if os.path.isfile(file_path) or os.path.islink(file_path):
            # If it's a file or a link, delete it
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            # If it's a directory, delete it and all its contents
            shutil.rmtree(file_path)
else:
    print(f'The directory {dir_path} does not exist')