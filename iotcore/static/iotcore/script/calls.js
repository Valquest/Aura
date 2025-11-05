document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll('.iot_action_btns')
    buttons.forEach((button) => {
        button.addEventListener('click', async (e) => {
            e.preventDefault;

            const getCookie = (name) => {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length +1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            };

            const csrftoken = getCookie('csrftoken');

            const response = await fetch(`http://127.0.0.1:8000/iotcore/toggle/${button.id}`,
                {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                });
            
            if (!response.ok) {
                throw new Error(`Http error! Status: ${request.status}`);
            }

            const data = await response.json();
            console.log("Toggle response:", data);

            if (data.status === 'success') {
                    button.textContent = data.message.includes('successfully') ? 'OFF' : 'ON';
                    console.log("Success: Device toggled");

            const currentText = button.textContent.trim();
            if (currentText === "ON") {
                button.textContent = "OFF";
            } else {
                button.textContent = "ON";
            }
        }})
    })
})