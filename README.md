# Discord-AI
Discord automated reply to 
* Supported Gemini AI & Openrouter AI

# Preparation 
Get Your Gemini API Key : https://aistudio.google.com/apikey

* Login with your google accounts
* Create API Key
* Copy API Key

Get Your Openrouter AI Key : https://openrouter.ai/
* Login with your google accounts
* Create API Key
* Copy API Key

# Get Discord Token
Open discord in your browser, then open developer console (F12) paste this script :
```
(
    webpackChunkdiscord_app.push(
        [
            [''],
            {},
            e => {
                m=[];
                for(let c in e.c)
                    m.push(e.c[c])
            }
        ]
    ),
    m
).find(
    m => m?.exports?.default?.getToken !== void 0
).exports.default.getToken()
```
