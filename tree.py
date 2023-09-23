import os

def list_files(startpath, output_file, ignore_paths=None):
    if ignore_paths is None:
        ignore_paths = []

    for root, dirs, files in os.walk(startpath):
        # Check if the current directory should be ignored
        if any(ignore in root for ignore in ignore_paths):
            continue

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        output_file.write(f'{indent}{os.path.basename(root)}/\n')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            output_file.write(f'{subindent}{f}\n')

if __name__ == '__main__':
    startpath = '.'  # Start from the current directory
    ignore = ['dimzvirtual', 'bin', 'lib', 'include', 'node_modules']
    
    with open('directory_tree.txt', 'w') as f:
        list_files(startpath, f, ignore_paths=ignore)
