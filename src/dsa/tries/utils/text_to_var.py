def text_to_var(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    output = open(filename.split('.')[0] + '.mjs', 'w')

    for line in lines:
        output.write(f'"{line.strip()}",')
    

if __name__ == '__main__':
    filename = input('Enter the name of the file: ')
    text_to_var(filename)