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
    console.log("End time is " + endtime);
});

const clickSound = new Audio('../static/mouseclick.mp3');

  // Add event listener to the button
document.getElementById('tryoutbutton').addEventListener('click', () => {
    clickSound.play(); // Play the sound
});
document.getElementById('transporttotimesbutton').addEventListener('click', () => {
    clickSound.play(); // Play the sound
});
document.getElementById('requestschedulebutton').addEventListener('click', () => {
    clickSound.play(); // Play the sound
});

