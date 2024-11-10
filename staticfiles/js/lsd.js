const _g = {true: ' bg-red', false: ' bg-green'}
const _p = {true: 'r', false: 'w'}
const _s = { 
    true: 'w-100 block p m-t-b-4 brd-green brd-l-bar-green clr-green',
    false: 'w-100 block p m-t-b-4 brd-red brd-l-bar-red clr-red'
}
const _m = _ => document.getElementById(_).play();
let _ = -1; let _b = -1;
const ___ = (__) => {
    ++_; 
    if (!_) {
        _m(_p[v[__.id]]);
        __.className = _s[v[__.id]] + _g[v[__.id]];
        [...__.parentElement.children].forEach(child => {
            if (__.id != child.id && v[child.id]) 
                 child.className = _s[v[child.id]]; 
        });
        document.getElementById('c-f').style.display = 'block';
    }
}
const buddhirKhela = __ => {
    ++_b; if (!_b) fetch(`/amar-onek-buddhi/${__.id}`);
}
