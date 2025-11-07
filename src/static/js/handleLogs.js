$(document).ready(function () {
    function getLogData() {
        $.ajax({
            url: '/logs',
            type: 'GET',
            success: function (data) {
                data.reverse()
                createLogs(data.splice(0, 30));
            },
            error: function (error) {
                console.log(error)
                return []
            }
        })
    }

    function createLogs(logData) {
        const logContainer = document.getElementById('logContainer');
        logContainer.innerHTML = '';
        logData.forEach(log => {
            logContainer.innerHTML += `
            <div class="d-flex justify-content-between w-100">
                <div class="d-flex gap-2">
                    <div class="">${new Date(log.event_time).toLocaleString()}</div>
                    <div class="d-flex flex-row">
                        <div class="fw-bolder mb-2 me-2 text-primary">${log.parent}                    
                        </div>
                        <div>${log.event_data}</div>
                    </div>
                </div>
            </div>
        `;
        });
    }

    getLogData();
    
    setInterval(function () {
        getLogData()
    }, 10000);
});