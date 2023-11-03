document.addEventListener('DOMContentLoaded', function () {
    const chatAndGraphArea = document.getElementById('chat-and-graph-area');

    window.sendQuestion = function () {
        const userQuestion = document.getElementById('user-input').value;
        console.log("User Question: ", userQuestion);

        fetch('/api/economics_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ input: userQuestion }),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Backend Response: ", JSON.stringify(data, null, 4));

            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'user-message';
            userMessageDiv.textContent = `You: ${userQuestion}`;
            chatAndGraphArea.appendChild(userMessageDiv);

            if (data.message.includes("CODE:")) {
                const fredCodeMatch = data.message.match(/CODE: (\w+)/);
                if (fredCodeMatch) {
                    const fredCode = fredCodeMatch[1];
                    fetchFREDDataAndGraph(fredCode);
                }
            }

            if (data.message) {
                const botMessageDiv = document.createElement('div');
                botMessageDiv.className = 'bot-message';
                botMessageDiv.textContent = `EconWizard: ${data.message}`;
                chatAndGraphArea.appendChild(botMessageDiv);

                chatAndGraphArea.scrollTop = chatAndGraphArea.scrollHeight;
                
            } else {
                const errorMessageDiv = document.createElement('div');
                errorMessageDiv.className = 'bot-message';
                errorMessageDiv.textContent = 'EconWizard: An error occurred or the message is missing in the response.';
                chatAndGraphArea.appendChild(errorMessageDiv);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'bot-message';
            errorDiv.textContent = 'EconWizard: An error occurred while sending the question.';
            chatAndGraphArea.appendChild(errorDiv);
        });
    };

    function fetchFREDDataAndGraph(fredCode) {
        console.log(`Fetching data for FRED code: ${fredCode}`);
        fetch(`/api/get_fred_code?code=${encodeURIComponent(fredCode)}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Data found') {
                console.log(`Data found for FRED code: ${fredCode}`, data);
                updateGraph(data.data);
            } else {
                console.error(`No data found for FRED code: ${fredCode}`, data);
                throw new Error(`No data found for FRED code: ${fredCode}`);
            }
        })
        .catch(error => {
            console.error('Error fetching FRED data:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'bot-message';
            errorDiv.textContent = `EconWizard: Error fetching data for FRED code: ${fredCode}`;
            chatAndGraphArea.appendChild(errorDiv);
        });
    }

    function updateGraph(data) {
        console.log(`Updating graph with data for code: ${data.code}`);
        fetch('/update_graph', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.plot_div) {
                console.log(`Graph updated for code: ${data.code}`);
                const graphDiv = document.createElement('div');
                graphDiv.innerHTML = data.plot_div;
                chatAndGraphArea.appendChild(graphDiv);
            } else {
                console.error(`No graph data found for the provided data:`, data);
                throw new Error(`No graph data found for the provided data.`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'bot-message';
            errorDiv.textContent = `EconWizard: ${error.message}`;
            chatAndGraphArea.appendChild(errorDiv);
        });
    }
});
