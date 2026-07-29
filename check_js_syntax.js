const fs = require('fs');
const path = 'G:\\Github TriWahyu45\\GamepadPiano\\index.html';
try {
    const content = fs.readFileSync(path, 'utf8');
    const scriptMatch = content.match(/<script>([\s\S]*?)<\/script>/);
    if (scriptMatch) {
        new Function(scriptMatch[1]);
        console.log("JS Syntax OK");
    } else {
        console.log("No script tag found");
    }
} catch (e) {
    console.error("JS Syntax ERROR:", e.message);
}
