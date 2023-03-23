# Quart Extension Repository Template
This repoistory is used as a template to build new Quart extensions
using VS Code, Dev Containers, and Poetry. 

The container is created and then there is a shell script which will 
look for a pyproject.toml file. If the file exists, the script will 
then run `poetry install`. If it does not exist it will tell you there
is no file. It is assumed that this file is it a the root of the project
directory. 

When first creating your project. Run `poetry init` to create your 
pyproject.toml file. Then rebuild the development container to install 
your required dependicies for your project.

It also has some common used directories and files as templates for the new extension. 
