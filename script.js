//=============JS code for the html exam page====================================================================

//=============Global variables====================================================================
let legal_alarm = false; // Flag to check if all questions are answered

//=============Functions====================================================================
// Blocks the exam submission until all questions are answered
function validateForm() {
    // Get all fieldsets (each representing a question)
    var questions = document.getElementsByTagName('fieldset'); 
    // Loop through each question
    for (var i = 0; i < questions.length; i++) { 
        // Get all input elements (answers) within the question
        var inputs = questions[i].getElementsByTagName('input'); 
        var textareas = questions[i].getElementsByTagName('textarea'); // Get textareas for open questions
        var answered = false; // Flag to check if the question is answered

        // Check if any input (radio/checkbox) is checked
        for (var j = 0; j < inputs.length; j++) { 
            if (inputs[j].checked) { 
                answered = true; 
                break; 
            }
        }

        // If not answered by input, check if any textarea is filled
        if (!answered && textareas.length > 0) {
            for (var t = 0; t < textareas.length; t++) {
                if (textareas[t].value.trim() !== "") {
                    answered = true;
                    break;
                }
            }
        }

        if (!answered) { // If the question is not answered
            legal_alarm = true; // Set the legal alarm flag
            alert(window.i18n?.t('answer_all_questions_exam') || 'Please answer all questions before submitting the exam.'); 
            return false; // Prevent form submission
        }
    }

    send_values(); // Call the function to send form values to the server
    return true; // Allow form submission
}
//=================================================================================
// Sends the values to the server. 
// All these values should be manually excluded from the question list
function send_values() {  
    // Set the hidden input field for minutes  
    document.getElementById('minutes_input').value = document.getElementById('minutes').innerHTML; 
    // Set the hidden input field for seconds
    document.getElementById('seconds_input').value = document.getElementById('seconds').innerHTML; 

}

//=================================================================================
// Function to load the exam in two steps:
// 1. Show a notification to the student
// 2. Load the exam after the student submits the notification
function loadExam() {
    // Hide the notification element
    document.getElementById('notification').style.display = 'none'; 
    // Show the exam form
    document.getElementById('exam-form').style.display = 'block'; 

    send_exam_start_notification(); // Send a notification to the server
    startTimer(); // Start the timer
}

//=================================================================================
// Timer functionality to display the time spent on the exam
var timer; // Variable to store the timer interval
var totalSeconds = 0; // Counter for total seconds elapsed

function startTimer() {
    timer = setInterval(setTime, 1000); // Call the setTime function every second
}

function setTime() {
    ++totalSeconds; // Increment the total seconds counter
    // Update the seconds display (modulo 60 for seconds)
    document.getElementById("seconds").innerHTML = pad(totalSeconds % 60); 
    // Update the minutes display (total seconds divided by 60)
    document.getElementById("minutes").innerHTML = pad(parseInt(totalSeconds / 60)); 
}

function pad(val) {
    // Function to add a leading zero to single-digit numbers
    var valString = val + ""; // Convert the value to a string
    if (valString.length < 2) { // If the string length is less than 2
        return "0" + valString; // Add a leading zero
    } else {
        return valString; // Return the value as is
    }
}

//=================================================================================
// Function to play a beep sound for a specified duration
function beep(duration = 2000) {
    let ctx = new AudioContext(), // Create a new audio context
        osc = ctx.createOscillator(); // Create an oscillator for generating sound
    osc.connect(ctx.destination); // Connect the oscillator to the audio output
    osc.start(); // Start the oscillator
    setTimeout(() => osc.stop(), duration); // Stop the oscillator after the specified duration
}

//=================================================================================
// Send an exam start notification to the server
function send_exam_start_notification() {
    // Use the navigator.sendBeacon method to send a notification to the server
    navigator.sendBeacon('/exam-started', JSON.stringify({
        message: "exam-started",
        timestamp: new Date().toISOString() // Add a timestamp for the event
    }));
}

//=================================================================================
// Function to send a notification when the user tries to cheat or refresh the page
function send_cheating_notification () {
    // Use the navigator.sendBeacon method to send a notification to the server
    navigator.sendBeacon('/notify-refresh', JSON.stringify({
        message: "/notify-refresh",
        timestamp: new Date().toISOString() // Add a timestamp for the event
    }));
}

//=================================================================================
// Prevent the user from using DevTools and certain key combinations
//  !!!!!!!!!! to be continued !!!!!!!!!!!
document.addEventListener("keydown", function(event) {
    // Check for F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U, Ctrl+A, and Ctrl+C
    if (
        event.key === "F12" || // Check if the F12 key is pressed
        (event.ctrlKey && event.shiftKey && (event.key === "I" || event.key === "J")) || // Check for Ctrl+Shift+I or Ctrl+Shift+J
        (event.ctrlKey && event.key === "u") || // Check for Ctrl+u
        (event.ctrlKey && event.key === "U") || // Check for Ctrl+u
        (event.ctrlKey && event.key === "a") || // Check for Ctrl+a
        (event.ctrlKey && event.key === "A") || // Check for Ctrl+A
        (event.ctrlKey && event.key === "c") || // Check for Ctrl+c
        (event.ctrlKey && event.key === "C")  // Check for Ctrl+C
    ) {
        event.preventDefault(); // Prevent the default action
        alert(window.i18n?.t('action_disabled_exam') || 'This action is disabled during the exam!'); // Show an alert to the user
    }
});

// Prevent the user from right-clicking (to disable DevTools)
document.addEventListener("contextmenu", function(event) {
    event.preventDefault(); // Prevent the default context menu
    alert(window.i18n?.t('rightclick_disabled_exam') || 'Right-click is disabled during the exam!'); // Show an alert to the user
});


//=================================================================================
// Event triggered when the page is refreshed or closed
window.addEventListener("beforeunload", function () {
    send_cheating_notification(); // Send a notification to the server
});
//=================================================================================
// Event triggered when the page loses focus
// Prevent the user from switching tabs
window.onblur = function() {
    if (legal_alarm === false) { // do Not consider the "fill all questions" alarm
    send_cheating_notification(); // Send a notification to the server
    }
    legal_alarm = false; // Reset the legal alarm flag
    beep(2000); // Play a beep sound for 2 seconds
};
//=================================================================================
// Periodically check if onblur is working
setInterval(() => {
    if (window.onblur === false || window.onblur === null) {
        send_cheating_notification(); // Send a notification to the server
    }
}, 5000);
//=================================================================================

