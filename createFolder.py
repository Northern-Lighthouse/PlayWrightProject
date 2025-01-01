import os

def create_folder_and_file():
    folder_name = input("Enter the name of the folder and text file: ")
    os.makedirs(folder_name, exist_ok=True)

    with open(os.path.join(folder_name, folder_name + '.txt'), 'w') as f:
        text = input("Enter the text you want to write to the file: ")
        f.write(text)

    another_folder = input("Would you like to create another folder? (yes/no): ")
    if another_folder.lower() == 'yes':
        create_folder_and_file()

create_folder_and_file()