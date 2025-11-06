document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll('.iot_action_btns')
    buttons.forEach((button) => {
        button.addEventListener('click', async (e) => {
            console.log('Button clicked:', button.id);
            e.preventDefault();

            const csrftoken = getCookie('csrftoken');
            if (!csrftoken) {
                alert('CSRF token missing-refresh page.');
                return;
            }

            const orriginalButtonMessage = button.innerHTML;
            button.disabled = true;
            button.classList.add('loading');
            const textSpan = button.querySelector('.btn-text');
            textSpan.style.opacity = '0.5';

            button.innerHTML = `
                <span class="spinner-wrapper">
                    <span class="spinner-border text-light" role="status" aria-hidden="true"></span>
                </span>
                <span class="btn-text" style="opacity: 0.5;">${textSpan.textContent}</span>    
            `;

            try {
                const response = await fetch(`http://127.0.0.1:8000/iotcore/toggle/${button.id}`,
                    {
                        method: 'post',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        },
                    });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP ${response.status}: ${errorData.message || 'Unknown error'}`);
                }

                const data = await response.json();

                button.classList.remove('loading');
                button.classList.add('success');
                button.innerHTML = `
                <span class="btn-text">${data.device_action_status ? 'OFF' : 'ON'}</span>
                `;

                setTimeout(() => {
                    button.classList.remove('success');
                    button.disabled = false;
                }, 600);

                console.log('Success', data);

            } catch (error) {
                button.classList.remove('loading');
                button.classList.add('failure');
                button.innerHTML = orriginalButtonMessage;

                setTimeout(() => {
                    button.classList.remove('failure');
                    button.disabled = false;
                }, 500);

                console.error('Toggle failure:', error);
                //alert(`Device unresponsive or error: ${error.message}`);
            }
        });
    });

    // Get CSRF token from websites cookies as Django stores them there
    // Basic string manipulation to locate CSRF token and extract it
    function getCookie(name) {
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
});