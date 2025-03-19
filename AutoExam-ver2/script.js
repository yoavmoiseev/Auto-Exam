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
//========== Evets listeners=======================================================
// Starts when the page is loaded
window.onload = function() {
            
    startTimer();  
};
//=================================================================================
//Event triggered when the page loose focus
//Prevent the user from switching tabs
window.onblur = function() {
    {
        let ctx = new AudioContext(), osc = ctx.createOscillator();
        osc.connect(ctx.destination);
        osc.start();
        setTimeout(() => osc.stop(), 2000); // Beep duration: 2 sec
    }

    // If the user lives the page- count it as a cheating attempt
    Cheating_attempts++;
    alert('Please stay focused on the exam!');

};
    
