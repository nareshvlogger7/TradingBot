document.getElementById('nextBtn').addEventListener('click', function() {
    document.getElementById('step1').style.display = 'none';
    document.getElementById('step2').style.display = 'block';
});

document.getElementById('backBtn').addEventListener('click', function() {
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2').style.display = 'none';
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Collect input values
    const username = document.getElementById('username').value;
    const apiKey = document.getElementById('apiKey').value;
    const token = document.getElementById('token').value;
    const stopLoss = document.getElementById('stopLoss').value;
    const profit = document.getElementById('profit').value;

    // Prepare data for API call
    const data = {
        username: username,
        apiKey: apiKey,
        token: token,
        stopLoss: stopLoss,
        profit: profit
    };

    // Send data to the server using fetch
    fetch('/start_trading', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        // Handle success or error response
        if (data.status === "success") {
            alert("Order placed successfully! Order ID: " + data.order_id);
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
        alert("An error occurred: " + error.message);
    });
});
