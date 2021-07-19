
# Inspecting the Web App

In order to be able to trace back function calls and their parameters we need a way to push arbritary code into the website/electron web app.

One way to do this is to inject modified JavaScript into the WhatsApp Web Desktop Electron App

### Preparing the setup

Firstly, [download the WhatsApp Web App](https://www.whatsapp.com/download) and [download Debugtron](https://github.com/bytedance/debugtron/releases/tag/v0.5.0)

Debugtron allows us to `inspect element` on packaged Electron applications.

Run `npm install -g asar` which will help us extracting and packaging JS content.

### Injecting JS into the app

`cd` into a new folder and then run `asar extract [WA]../app.asar .`. For macOS with standard paths, you would do  `asar extract /Applications/WhatsApp.app/Contents/Resources/app.asar .`

You should now see all kinds of JS, CSS etc. files in that folder. Our point of interest is mainly the `bootstrap_main.123456789.js`. 

After editing the file(s), we do the reverse operation to put the new files back into the `app.asar`. For this, you can run `asar pack . /Applications/WhatsApp.app/Contents/Resources/app.asar` on macOS, replace the path for Windows/Linux.

### Running the app with the debugger attached

Open `Debugtron` that we have previously installed. Select "WhatsApp" from the list (or add it manually if needed) and inspect the [page] session. This is like `inspect element` on the website, except that it's our custom code in there.

### Goals

We can hopefully automate the whole process somehow, however the most important thing to get going right now is to make our `console.log()` calls show up in the debugger. We need to find a way to somehow escape the context or make a logger expose itself to it. Feel free to discuss if you have ideas on how to go about that.
