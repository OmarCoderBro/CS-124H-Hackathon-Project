fetch('/config')
    .then(response => response.json())
    .then(config => {
        const times = ["12:00AM", "1:00AM", "2:00AM", "3:00AM", "4:00AM", "5:00AM", "6:00AM", 
            "7:00AM", "8:00AM", "9:00AM", "10:00AM", "11:00AM", "12:00PM", "1:00PM", 
            "2:00PM", "4:00PM", "5:00PM", "6:00PM", "7:00PM", "8:00PM", "9:00PM", "10:00PM", "11:00PM"];

        const selectstarttime = document.getElementById("selectstarttime");
        const selectendtime = document.getElementById("selectendtime");

        selectstarttime.innerHTML = '';
        selectendtime.innerHTML = '';

        times.forEach(time => {
            const startOption = document.createElement("option");
            const endOption = document.createElement("option");
            startOption.text = time;
            endOption.text = time;
            selectstarttime.appendChild(startOption);
            selectendtime.appendChild(endOption);
        });
});

// When user selects times, update the config
document.getElementById("requestschedulebutton").addEventListener("click", function() {
    const starttime = document.getElementById("selectstarttime").value;
    const endtime = document.getElementById("selectendtime").value;
    
    const start_hour = convertTimeToHour(starttime);
    const end_hour = convertTimeToHour(endtime);

    fetch('/update_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            start_hour: start_hour,
            end_hour: end_hour
        })
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = '/calendar';
    });
});

function convertTimeToHour(timeStr) {
    // Split the time string into time and period (AM/PM)
    const [timeComponent, period] = timeStr.split(/(?=[AP]M)/);
    let [hours] = timeComponent.split(':').map(Number);
    
    // Handle PM times
    if (period === 'PM') {
        if (hours !== 12) {
            hours += 12;
        }
    } 
    // Handle AM times
    else if (period === 'AM') {
        if (hours === 12) {
            hours = 0;
        }
    }
    
    return hours;
}