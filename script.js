//=============JS code for the html exam page====================================================================

//=============Global variables====================================================================
Cheating_attempts = 0; // Counter for cheating attempts


//=============Functions====================================================================
// Blocks the exmam subbmit until all questions are answered
function validateForm() {
    var questions = document.getElementsByTagName('fieldset');
    
    for (var i = 0; i < questions.length; i++) {
        var inputs = questions[i].getElementsByTagName('input');
        var answered = false;
        for (var j = 0; j < inputs.length; j++) {
            if (inputs[j].checked) {
                answered = true;
                break;
            }
        }
        if (!answered) {
            alert('Please answer all questions before submitting the exam.');
            return false;
        }
    }

    send_values();
    return true;
}

//=================================================================================
//=================================================================================     

function send_values()
// Send the values toserver! All these values should be manualy excluded from question list
{    
    document.getElementById('minutes_input').value = document.getElementById('minutes').innerHTML;
    document.getElementById('seconds_input').value = document.getElementById('seconds').innerHTML;
    document.getElementById('cheating_attempts_input').value = Cheating_attempts; // Set the value of the hidden input field
}

//=================================================================================
// Function to load the exam form dynamically
function loadExam() {
    document.getElementById('notification').style.display = 'none'; // Hide the notification
    document.getElementById('exam-form').style.display = 'block'; // Show the exam form

    startTimer(); // Start the timer
}


//=================================================================================
//=================================================================================
// Stopper, on page buttom, dispalying the time spent on the exam    
var timer;
    var totalSeconds = 0;

    function startTimer() {
        timer = setInterval(setTime, 1000);
    }

    function setTime() {
        ++totalSeconds;
        document.getElementById("seconds").innerHTML = pad(totalSeconds % 60);
        document.getElementById("minutes").innerHTML = pad(parseInt(totalSeconds / 60));
    }

    function pad(val) {
        var valString = val + "";
        if (valString.length < 2) {
            return "0" + valString;
        } else {
            return valString;
        }
    }
//=================================================================================
function beep(duration=2000){
    //play beep alert sound. duration in milisec
    let ctx = new AudioContext(), osc = ctx.createOscillator();
    osc.connect(ctx.destination);
    osc.start();
    setTimeout(() => osc.stop(), duration); 
}

//=================================================================================
//========== Evets listeners=======================================================
// Starts when the page is loaded
window.onload = function() {
    //Should start when the page is loaded
    //Blocked by browser until the user interacts with the page
    //use loadExam() instead  
    
    
      
};
    

//=================================================================================
// Trying to prevent the user from using DevTools
document.addEventListener("keydown", function(event) {
    // Check for F12, Ctrl+Shift+I, Ctrl+Shift+J, and Ctrl+U
    if (
        event.key === "F12" || 
        (event.ctrlKey && event.shiftKey && (event.key === "I" || event.key === "J")) || 
        (event.ctrlKey && event.key === "U")
    ) {
        event.preventDefault(); // Prevent the default action
        alert("DevTools is disabled during the exam!");
    }
});

// Prevent the user from right-clicking- DevTools
document.addEventListener("contextmenu", function(event) {
    event.preventDefault();
    alert("Right-click is disabled during the exam!");
});


//=================================================================================
//Event triggered when the page loose focus
//Prevent the user from switching tabs
window.onblur = function() {
   

    // If the user lives the page- count it as a cheating attempt
    Cheating_attempts++;

    beep(2000)


};
    
