(function () {
    // Only run on authenticated pages (navbar is only rendered when logged in)
    const activeDevNav = document.getElementById('active-device-nav-item');
    if (!activeDevNav) return;

    let retryDelay = 2000;
    let source;

    function connect() {
        source = new EventSource('/iotcore/events/');

        source.onopen = function () {
            retryDelay = 2000;
        };

        source.onmessage = function (e) {
            try {
                const event = JSON.parse(e.data);
                if (event.type === 'stat') handleStat(event);
                else if (event.type === 'heartbeat') handleHeartbeat(event);
                else if (event.type === 'active_count') handleActiveCount(event);
            } catch (_) {}
        };

        source.onerror = function () {
            source.close();
            setTimeout(connect, retryDelay);
            retryDelay = Math.min(retryDelay * 2, 30000);
        };
    }

    function handleStat(event) {
        const tbody = document.querySelector(`tbody[data-action-id="${event.action_id}"]`);
        if (!tbody) return;

        const row = document.createElement('tr');

        const tsCell = document.createElement('td');
        tsCell.textContent = new Date(event.timestamp).toLocaleString();
        row.appendChild(tsCell);

        for (const value of Object.values(event.data)) {
            const td = document.createElement('td');
            td.textContent = value;
            row.appendChild(td);
        }

        tbody.insertBefore(row, tbody.firstChild);

        while (tbody.rows.length > 10) {
            tbody.deleteRow(tbody.rows.length - 1);
        }
    }

    function handleHeartbeat(event) {
        const dot = document.querySelector(`.device-status-dot[data-device-id="${event.device_id}"]`);
        if (!dot) return;
        dot.classList.toggle('online', event.online === true);
        dot.classList.toggle('offline', event.online === false);
    }

    function handleActiveCount(event) {
        const link = activeDevNav.querySelector('a');
        if (link) {
            link.textContent = `${event.count} Active`;
        }
    }

    connect();
})();
