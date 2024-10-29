const slideHorizontally = (id) => {
    element = document.getElementById(id);
    element.style.left = {
        '-100%': '0%',
        '0%': '-100%'
    }[element.style.left];
    console.log('slided');
}