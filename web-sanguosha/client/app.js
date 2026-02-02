document.getElementById('start-game').addEventListener('click', () => {
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    overlay.style.zIndex = '1000';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.innerHTML = '<h1 style="color: white">Loading... Please wait</h1>';

    document.body.appendChild(overlay);

    setTimeout(() => {
        overlay.innerHTML = '<h1 style="color: white">⚔️ Welcome to 三国杀! ⚔️</h1>';
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 2000);
    }, 3000);
});