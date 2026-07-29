import json, sys
sys.path.append(r'G:\Antigravity_Server\Bot_Scripts')
from model_switcher import _cdp_eval

js = """
(async function() {
    var modelBtn = Array.from(document.querySelectorAll('button')).find(function(b) {
        var t = (b.innerText || '').trim();
        return b.className.includes('h-7') && (t.includes('Gemini') || t.includes('Flash') || t.includes('Pro') || t.includes('Claude') || t.includes('GPT') || t.includes('Sonnet') || t.includes('Thinking'));
    });
    if (!modelBtn) return JSON.stringify({error: 'NO_MODEL_BTN'});
    
    var currentModel = modelBtn.innerText.trim();
    modelBtn.click();
    await new Promise(r => setTimeout(r, 500));
    
    var items = Array.from(document.querySelectorAll('div, button, span, li')).filter(function(el) {
        if (el.closest('.prose') || el.closest('div.leading-relaxed') || el.closest('[contenteditable="true"]')) return false;
        if (el === modelBtn || modelBtn.contains(el)) return false;
        var t = (el.innerText || el.textContent || '').trim();
        return t.length > 2 && t.length < 50 && (t.includes('Gemini') || t.includes('Claude') || t.includes('GPT') || t.includes('Flash') || t.includes('Pro') || t.includes('Sonnet') || t.includes('Thinking') || t.includes('Opus') || t.includes('o1') || t.includes('o3') || t.includes('DeepSeek'));
    });
    
    var names = Array.from(new Set(items.map(function(i){ return (i.innerText || '').trim(); })));
    document.body.click();
    return JSON.stringify({current: currentModel, available: names});
})()
"""

val = _cdp_eval(js, await_promise=True)
print("DOM_AVAILABLE_MODELS:", val)
