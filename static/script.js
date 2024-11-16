const times = ['12:00AM', '1:00AM', '2:00AM', '3:00AM', '4:00AM', '5:00AM', '6:00AM',
    '7:00AM', '8:00AM', '9:00AM', '10:00AM', '11:00AM', '12:00PM', '1:00PM', '2:00PM',
    '3:00PM', '4:00PM', '5:00PM', '6:00PM', '7:00PM', '8:00PM', '9:00PM',
    '10:00PM', '11:00PM']

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