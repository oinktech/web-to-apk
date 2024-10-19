document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Unknown error occurred');
            });
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'app-release-unsigned.apk';
        document.body.appendChild(a);
        a.click();
        a.remove();
    })
    .catch(err => {
        document.getElementById('error').innerText = err.message;
    });
});
