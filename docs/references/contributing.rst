Contributing
============

.. _dev:

============
Contributing
============

Quart-Mongo is developed on github. If you would like to contribute to the project, you 
can open an `issue <https://github.com/Quart-Addons/quart-mongo/issues>`_ on github. 

Your contribution would be greatly appreciated!

Developing Locally:
-------------------

.. image:: ../_static/vscode-docker.png
   :width: 350px
   :alt: VS Code + Docker
   :align: center

Quart-Mongo utilizes VSCode's `devcontainer <https://code.visualstudio.com/docs/devcontainers/containers>`_ feature. 
This feature makes the tools/environment very simple as you will develop in a Docker container that has already been 
configured for the project.

.. note::
    The `devcontainer.json` file is setup to use docker compose. This is because the development environment will
    run a MongoDB docker container for testing the extension.  

Here are the steps:

1. Clone the repository and open it with `Visual Code Studio <https://code.visualstudio.com/>`_.
2. Make sure that the `Remote-Containers <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers>`_ (`ms-vscode-remote.remote-containers`) extension is installed.
3. Run the `Remote-Container: Reopen in Container` command (press `Ctrl`+`Shift`+`P` and
   then type the command).
4. After the setup script completes, the environment is ready. You can start the local
   development.