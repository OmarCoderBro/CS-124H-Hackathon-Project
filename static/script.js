fetch('/config')
    .then(response => response.json())
    .then(config => {
        const START_HOUR = config.START_HOUR;
        const END_HOUR = config.END_HOUR;

        // Generate times array based on configured hours
        const times = [];
        for (let hour = START_HOUR; hour <= END_HOUR; hour++) {
            const timeStr = hour < 12 ? 
                `${hour}:00AM` : 
                `${hour === 12 ? 12 : hour-12}:00PM`;
            times.push(timeStr);
        }

        const selectstarttime = document.getElementById("selectstarttime");
        const selectendtime = document.getElementById("selectendtime");

        times.forEach(time => {
            const option = document.createElement("option");
            option.text = time;
            selectendtime.appendChild(option);
        });

        times.forEach(time => {
            const option = document.createElement("option");
            option.text = time;
            selectstarttime.appendChild(option);
        });
    });