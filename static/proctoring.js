/**
 * Proctoring System - Two-Stage Exam with Focus Tracking
 * Stage 1: Pre-Exam Screen (warnings + name input)
 * Stage 2: Active Exam (with real-time proctoring)
 */

let examStarted = false;
let studentSessionId = null;
let examFocusGained = false;
let totalSeconds = 0;
let timerInterval = null;
let focusCheckInterval = null;

// ============================================================================
// STAGE 1: PRE-EXAM SCREEN - Initialization
// ============================================================================

function initializePreExamScreen() {
    const form = document.getElementById('pre-exam-form');
    if (form) {
        form.addEventListener('submit', handlePreExamSubmit);
    }
}

async function handlePreExamSubmit(e) {
    e.preventDefault();
    
    const firstName = document.getElementById('first-name').value.trim();
    const lastName = document.getElementById('last-name').value.trim();
    
    if (!firstName || !lastName) {
        alert(window.i18n?.t('enter_name_error') || 'Please enter your first and last name');
        return;
    }
    
    try {
        const examId = getExamIdFromURL();
        const response = await fetch(`/api/exam/${examId}/start-student`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            studentSessionId = data.student_session_id;
            examQuestions = data.exam_data.questions;
            const textDirection = data.exam_data.text_direction || 'ltr';
            
            // Store student names
            window.studentFirstName = firstName;
            window.studentLastName = lastName;
            
            // Apply RTL to entire page if Hebrew
            const container = document.querySelector('.exam-container');
            if (textDirection === 'rtl') {
                container.classList.add('rtl');
                document.body.style.direction = 'rtl';
            }
            
            // Hide pre-exam screen
            document.getElementById('pre-exam-screen').style.display = 'none';
            
            // Show exam screen
            document.getElementById('exam-screen').style.display = 'block';
            
            // Display questions (function from student_exam_session.html)
            if (typeof displayAllQuestions === 'function') {
                displayAllQuestions();
            }
            
            // Start timer (function from student_exam_session.html)
            if (typeof startTimer === 'function') {
                startTimer();
            }
            
            // Initialize proctoring
            initializeProctoring();
        } else {
            alert((window.i18n?.t('error_generic') || 'Error') + ': ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(window.i18n?.t('error_occurred') || 'An error occurred');
    }
}

// ============================================================================
// STAGE 2: PROCTORING SYSTEM - Focus Tracking
// ============================================================================

function initializeProctoring() {
    examStarted = true;
    
    // Event: When user gains focus (clicks on exam page)
    window.addEventListener('focus', handleWindowFocus);
    
    // Event: When user loses focus (switches tabs/windows)
    window.addEventListener('blur', handleWindowBlur);
    
    // Event: When user tries to leave page
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // Keyboard events: Block copy, paste, developer tools
    document.addEventListener('keydown', handleKeyboardEvent);
    
    // Context menu: Block right-click
    document.addEventListener('contextmenu', handleContextMenu);
    
    // Periodic check for focus
    focusCheckInterval = setInterval(checkFocusStatus, 5000);
}

function stopProctoring() {
    examStarted = false;
    
    // Remove all event listeners
    window.removeEventListener('focus', handleWindowFocus);
    window.removeEventListener('blur', handleWindowBlur);
    window.removeEventListener('beforeunload', handleBeforeUnload);
    document.removeEventListener('keydown', handleKeyboardEvent);
    document.removeEventListener('contextmenu', handleContextMenu);
    
    // Stop timers and intervals
    stopTimer();
    if (focusCheckInterval) {
        clearInterval(focusCheckInterval);
        focusCheckInterval = null;
    }
    
    console.log('Proctoring stopped - exam completed');
}

// ============================================================================
// FOCUS MANAGEMENT
// ============================================================================

function handleWindowFocus() {
    if (!examFocusGained) {
        examFocusGained = true;
        startTimer();
        
        logEvent('exam_focus_gained');
    }
}

function handleWindowBlur() {
    if (examFocusGained && examStarted) {
        logCheatingAttempt('focus_lost');
        playWarningBeep();
    }
}

function handleBeforeUnload(e) {
    if (examFocusGained && examStarted) {
        logCheatingAttempt('page_unload');
    }
}

function checkFocusStatus() {
    if (examFocusGained && examStarted && document.hidden) {
        logCheatingAttempt('window_minimized');
    }
}

// ============================================================================
// KEYBOARD AND INPUT BLOCKING
// ============================================================================

function handleKeyboardEvent(e) {
    // Do not block keyboard if exam is completed
    if (!examStarted) {
        return true;
    }
    
    // Block F12 (DevTools)
    if (e.key === 'F12') {
        e.preventDefault();
        logCheatingAttempt('devtools_f12');
        return false;
    }
    
    // Block Ctrl+Shift+I/J/K (DevTools)
    if (e.ctrlKey && e.shiftKey && ['I', 'J', 'K'].includes(e.key.toUpperCase())) {
        e.preventDefault();
        logCheatingAttempt('devtools_keyboard');
        return false;
    }
    
    // Block Ctrl+U (View Source)
    if (e.ctrlKey && e.key.toLowerCase() === 'u') {
        e.preventDefault();
        logCheatingAttempt('view_source');
        return false;
    }
    
    // Block Ctrl+Shift+Delete (Clear History - Firefox)
    if (e.ctrlKey && e.shiftKey && e.key === 'Delete') {
        e.preventDefault();
        logCheatingAttempt('clear_history');
        return false;
    }
    
    // Allow copy/paste within the exam (but log attempts to copy answers)
    // Block if trying to copy from outside the exam form
    // FIX v4: FULL BLOCK of Ctrl+C
    // REMARK: Previously only logged copy attempts, now completely blocks copying
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c') {
        e.preventDefault();
        logCheatingAttempt('copy_blocked');
        return false;
    }
    
    // Block Ctrl+V (Paste) - to prevent pasting from external sources
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'v') {
        logCheatingAttempt('paste_attempt');
        e.preventDefault();
        return false;
    }
}

function handleContextMenu(e) {
    // Do not block right-click if exam is completed
    if (!examStarted) {
        return true;
    }
    
    e.preventDefault();
    logCheatingAttempt('right_click');
    return false;
}

// ============================================================================
// TIMER FUNCTIONALITY
// ============================================================================

function startTimer() {
    totalSeconds = 0;
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    totalSeconds++;
    
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    
    const minutesDisplay = String(minutes).padStart(2, '0');
    const secondsDisplay = String(seconds).padStart(2, '0');
    
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = `${minutesDisplay}:${secondsDisplay}`;
    }
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
}

// ============================================================================
// LOGGING FUNCTIONS
// ============================================================================

function logCheatingAttempt(attemptType, details = null) {
    // Do not log if exam is not started or already completed
    if (!examStarted) {
        return;
    }
    
    const examId = getExamIdFromURL();
    
    fetch(`/api/exam/${examId}/log-cheating`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            student_session_id: studentSessionId,
            attempt_type: attemptType,
            details: details,
            timestamp: new Date().toISOString()
        })
    }).catch(error => console.error('Error logging cheating attempt:', error));
}

function logEvent(eventType, eventData = null) {
    const examId = getExamIdFromURL();
    
    fetch(`/api/exam/${examId}/log-event`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            student_session_id: studentSessionId,
            event_type: eventType,
            event_data: eventData,
            timestamp: new Date().toISOString()
        })
    }).catch(error => console.error('Error logging event:', error));
}

// ============================================================================
// UI FUNCTIONS
// ============================================================================

function showExam() {
    const preExamScreen = document.getElementById('pre-exam-screen');
    const examScreen = document.getElementById('exam-screen');
    
    if (preExamScreen) {
        preExamScreen.style.display = 'none';
    }
    if (examScreen) {
        examScreen.style.display = 'block';
    }
    
    logEvent('exam_displayed');
}

// ============================================================================
// SOUND ALERT
// ============================================================================

function playWarningBeep() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Two beeps to make it more noticeable
        const now = audioContext.currentTime;
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        // First beep
        gainNode.gain.setValueAtTime(0.3, now);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        
        oscillator.start(now);
        oscillator.stop(now + 0.3);
        
        // Second beep
        oscillator.frequency.value = 600;
        gainNode.gain.setValueAtTime(0.3, now + 0.4);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.7);
        
        oscillator.start(now + 0.4);
        oscillator.stop(now + 0.7);
    } catch (e) {
        console.log('Audio context not available');
    }
}

// ============================================================================
// EXAM SUBMISSION
// ============================================================================

async function submitExam(answers) {
    stopTimer();
    
    const examId = getExamIdFromURL();
    
    try {
        const response = await fetch(`/api/exam/${examId}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_session_id: studentSessionId,
                answers: answers,
                time_spent: totalSeconds
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showExamResults(data.score, data.message);
            logEvent('exam_submitted', { score: data.score });
        } else {
            alert((window.i18n?.t('error_submitting_exam') || 'Error submitting exam') + ': ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(window.i18n?.t('error_submitting_exam_generic') || 'An error occurred while submitting the exam');
    }
}

function showExamResults(score, message) {
    const examScreen = document.getElementById('exam-screen');
    const resultsDiv = document.getElementById('exam-results');
    
    if (examScreen) {
        examScreen.style.display = 'none';
    }
    
    if (resultsDiv) {
        document.getElementById('final-score').textContent = `Your Score: ${score}%`;
        document.getElementById('results-message').textContent = message;
        resultsDiv.style.display = 'block';
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function getExamIdFromURL() {
    const parts = window.location.pathname.split('/');
    return parts[parts.length - 1];
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initializePreExamScreen();
});
