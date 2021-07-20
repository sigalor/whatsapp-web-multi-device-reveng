# Inspecting the Web App

In order to be able to trace back function calls and their parameters we need ways to fiddle around with the inner workings of the website or Electron app.

## Editing Electron app JavaScript (with example)

One way to do this is to inject modified JavaScript into the WhatsApp Web Desktop Electron App

### Preparing the setup

Firstly, [download the WhatsApp Web App](https://www.whatsapp.com/download) and [download Debugtron](https://github.com/bytedance/debugtron/releases/tag/v0.5.0)

Debugtron allows us to `inspect element` on packaged Electron applications.

Before you continue, run `npm install -g asar` which will help us extracting and packaging JS content.

### Injecting JS into the app

`cd` into a new folder and then run `asar extract [WA]../app.asar .`. For macOS with standard paths, you would do `asar extract /Applications/WhatsApp.app/Contents/Resources/app.asar .`

You should now see all kinds of JS, CSS etc. files in that folder. Our point of interest is mainly the `bootstrap_main.123456789.js`.

After editing the file(s), we do the reverse operation to put the new files back into the `app.asar`. For this, you can run `asar pack . /Applications/WhatsApp.app/Contents/Resources/app.asar` on macOS, replace the path for Windows/Linux.

### Running the app with the debugger attached

Open `Debugtron` that we have previously installed. Select "WhatsApp" from the list (or add it manually if needed) and inspect the [page] session. This is like `inspect element` on the website, except that it's our custom code in there.

### Example

In the following example, we will make the app print to console when setting a profile status.

After extracting the JS as shown above, navigate to the `renderer.js` which seems to be the main point of interest here. Search for the declaration of the `setMyStatus` function (there are two of them for some reason). The code is minified and ugly to read but you will find something like

```
t.setMyStatus=function e(t){var a=arguments.length>1&&
...
```

Now, let's find out what the `t` variable actually is. Simply adding a `console.log("setStatus", t);` should give us some information, the line now should look like 

```
t.setMyStatus=function e(t){console.log("setStatus", t);var a=arguments.length>1&&
...
```

After running `asar pack` as shown above to put our new JS back into the app, we can now open the WhatsApp Electron app and inspect the frame as previously shown.

In the Electron app, set a status and, surprisingly, our print will show in the console:

`(anonymous) @ electron/js2c/renderer_init.js:83
renderer.js:100 setStatus Hello`

Now we know that `t` is simply a string containing the status message that we typed which means we need to go further down the line in order to find where the actual encoding/encryption etc. takes place.

Please keep in mind that this is merely an example to follow - seeing the content of the string can be achieved in many faster ways such as breakpointing + variable watching but being able to run our own code within the app can be very helpful for things such as verifying our own implementations in the "production" environment or making some functions expose some information to the console by default.
