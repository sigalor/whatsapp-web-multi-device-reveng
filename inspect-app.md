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

## Modifying website JavaScript (with example)

Thanks to RuuN, we also have a way to overwrite functions on the website at runtime. For this, you can paste and run the following code in Chrome's console:

```
if (!window.mR) {
    const moduleRaid = function () {
      moduleRaid.mID  = Math.random().toString(36).substring(7);
      moduleRaid.mObj = {};

      fillModuleArray = function() {
        (window.webpackChunkbuild || window.webpackChunkwhatsapp_web_client).push([
          [moduleRaid.mID], {}, function(e) {
            Object.keys(e.m).forEach(function(mod) {
              moduleRaid.mObj[mod] = e(mod);
            })
          }
        ]);
      }

      fillModuleArray();

      get = function get (id) {
        return moduleRaid.mObj[id]
      }

      findModule = function findModule (query) {
        results = [];
        modules = Object.keys(moduleRaid.mObj);

        modules.forEach(function(mKey) {
          mod = moduleRaid.mObj[mKey];

          if (typeof mod !== 'undefined') {
            if (typeof query === 'string') {
              if (typeof mod.default === 'object') {
                for (key in mod.default) {
                  if (key == query) results.push(mod);
                }
              }

              for (key in mod) {
                if (key == query) results.push(mod);
              }
            } else if (typeof query === 'function') { 
              if (query(mod)) {
                results.push(mod);
              }
            } else {
              throw new TypeError('findModule can only find via string and function, ' + (typeof query) + ' was passed');
            }

          }
        })

        return results;
      }

      return {
        modules: moduleRaid.mObj,
        constructors: moduleRaid.cArr,
        findModule: findModule,
        get: get
      }
    }

    window.mR = moduleRaid();   
}


if (!window.decodeStanza) {
    window.decodeStanza = (window.mR.findModule('decodeStanza')[0]).decodeStanza;
    window.encodeStanza = (window.mR.findModule('encodeStanza')[0]).encodeStanza;
}


(window.mR.findModule('decodeStanza')[0]).decodeStanza = async (e, t) => {
    const result = await window.decodeStanza(e, t);

    console.log('decodeStanza', e, t, "->", result);
    return result;
}


(window.mR.findModule('encodeStanza')[0]).encodeStanza = (...args) => {
    const result = window.encodeStanza(...args);

    console.log('encodeStanza', args, "->", result);
    return result;
}
```

It overwrites existing methods to run the "original" code of these methods and adds arbitrary code on top of that so we can log parameters being passed as well as what they actually return.
