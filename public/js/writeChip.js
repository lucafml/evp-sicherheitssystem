async function writeChip(username, password) {
    try {
        const response = await fetch('http://localhost:5000/write-chip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Ein Fehler ist aufgetreten');
        }
        
        alert(data.message);
    } catch (error) {
        alert('Fehler: ' + error.message);
    }
}
