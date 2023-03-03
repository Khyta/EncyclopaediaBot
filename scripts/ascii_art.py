# Import pyfiglet module
import pyfiglet

# Define some Python code as a string
code = "WikiBot"

# Convert the code into ASCII art using the 'slant' font
art = pyfiglet.figlet_format(code, font='slant')

# Print the ASCII art to the console
print(art)

# Open a file in write mode
file = open('ascii_art.txt', 'w')

# Write the ASCII art to the file
file.write(art)

# Close the file
file.close()