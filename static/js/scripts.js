function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar.style.left === '-250px') {
        sidebar.style.left = '0';
    } else {
        sidebar.style.left = '-250px';
    }
}

document.querySelector('.upload-area').addEventListener('click', () => {
    document.getElementById('fileInput').click();
});

function dropHandler(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;
    processFiles(files);
}

function dragOverHandler(event) {
    event.preventDefault();
}

function processFiles(files) {
    // Add code to handle file processing and sending to the server
}
