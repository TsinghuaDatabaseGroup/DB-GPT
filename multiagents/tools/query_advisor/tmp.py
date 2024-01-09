
def remove_lines_with_prefix(filename, prefix):

    new_lines = ""

    with open(filename, 'r') as file:
        lines = file.readlines()
    
    modified_lines = []
    for line in lines:
        modified_lines.append(line)
        if line.startswith(prefix):
            modified_lines.append(new_lines)
            
    with open("new_"+filename, 'w') as file:
        file.writelines(modified_lines)

if __name__ == "__main__":
    input_file = "api.py"  # Change this to the name of your input file
    prefix_to_remove = "def "
    
    remove_lines_with_prefix(input_file, prefix_to_remove)