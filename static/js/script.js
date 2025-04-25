document.querySelector('#user-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the form from submitting normally

    // Get email and action values
    const email = document.querySelector('#email').value;
    const action = document.querySelector('#action').value;

    // Prepare data to send to Flask backend
    const data = {
        email: email,
        action: action
    };

    // Send the data to Flask using fetch API
    fetch('/manage-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Display the server's response
        document.querySelector('#response-message').textContent = data.message;
    })
    .catch(error => {
        console.error('Error:', error);
        document.querySelector('#response-message').textContent = 'An error occurred.';
    });
});

