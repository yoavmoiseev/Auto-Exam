/**
 * Exam Script - Client-side exam logic
 * Handles exam timer, questions, answers, proctoring
 */

class ExamSystem {
    constructor() {
        this.examId = this.getExamIdFromURL();
        this.timeRemaining = 60 * 60; // 60 minutes in seconds
        this.timerInterval = null;
        this.answers = {};
        this.cheatAttempts = 0;
        this.submitted = false;
        this.startTime = null;
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.studentName = null;
        this.init();
    }

    /**
     * Initialize exam system
     */
    async init() {
        this.setupEventListeners();
        this.setupCheatingDetection();
        
        // Load i18n
        if (typeof i18n !== 'undefined' && i18n.isReady) {
            this.updateTranslations();
        } else {
            setTimeout(() => this.updateTranslations(), 500);
        }
    }

    /**
     * Get exam ID/name from URL
     */
    getExamIdFromURL() {
        // Try to get exam name from query parameter
        const params = new URLSearchParams(window.location.search);
        const examName = params.get('name');
        if (examName) {
            return decodeURIComponent(examName);
        }
        
        // Fallback to path-based ID for backward compatibility
        const path = window.location.pathname;
        const parts = path.split('/');
        return decodeURIComponent(parts[parts.length - 1]);
    }

    /**
     * Update translations
     */
    updateTranslations() {
        if (typeof i18n === 'undefined') return;
        
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (key) {
                if (el.tagName === 'BUTTON') {
                    el.textContent = i18n.t(key);
                } else {
                    el.textContent = i18n.t(key);
                }
            }
        });
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Start exam button
        const startBtn = document.getElementById('start-btn');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startExam());
        }

        // Navigation buttons
        const prevBtn = document.getElementById('prev-btn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousQuestion());
        }

        const nextBtn = document.getElementById('next-btn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextQuestion());
        }

        // Submit exam button
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitExam());
        }

        // Answer changes
        document.addEventListener('change', (e) => {
            if (e.target.type === 'radio') {
                this.recordAnswer(e.target);
            }
        });
    }

    /**
     * Setup cheating detection
     */
    setupCheatingDetection() {
        // Prevent page refresh
        window.addEventListener('beforeunload', (e) => {
            if (!this.submitted) {
                this.logCheatAttempt('page_unload');
                e.preventDefault();
                e.returnValue = '';
            }
        });

        // Track visibility changes (tab switching)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.logCheatAttempt('tab_hidden');
            }
        });

        // Prevent copy-paste
        document.addEventListener('copy', (e) => {
            e.preventDefault();
            this.logCheatAttempt('copy_attempt');
        });

        document.addEventListener('paste', (e) => {
            e.preventDefault();
            this.logCheatAttempt('paste_attempt');
        });

        // Prevent right-click
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.logCheatAttempt('right_click');
        });

        // Detect DevTools
        this.detectDevTools();
    }

    /**
     * Detect DevTools opening
     */
    detectDevTools() {
        let lastCheck = Date.now();

        setInterval(() => {
            const elapsed = Date.now() - lastCheck;
            if (elapsed > 100 && elapsed < 200) {
                if (window.outerHeight - window.innerHeight > 150 ||
                    window.outerWidth - window.innerWidth > 150) {
                    this.logCheatAttempt('devtools_open');
                }
            }
            lastCheck = Date.now();
        }, 500);
    }

    /**
     * Log cheating attempt
     */
    logCheatAttempt(type) {
        this.cheatAttempts++;
        console.warn(`[Cheating Detection] ${type} (Attempt #${this.cheatAttempts})`);

        if (this.cheatAttempts > 5) {
            this.dismissExam(i18n.t('exam_dismissed'));
        }
    }

    /**
     * Start exam
     */
    async startExam() {
        const firstName = document.getElementById('first-name').value.trim();
        const lastName = document.getElementById('last-name').value.trim();

        if (!firstName || !lastName) {
            alert(i18n.t('student_name') + ' ' + i18n.t('required'));
            return;
        }

        this.studentName = { first: firstName, last: lastName };
        this.startTime = Date.now();

        // Hide pre-exam, show exam form
        document.getElementById('pre-exam').style.display = 'none';
        document.getElementById('exam-form').style.display = 'block';

        // Load exam questions
        await this.loadExamQuestions();

        // Display first question
        this.displayCurrentQuestion();

        // Start timer
        this.startTimer();
    }

    /**
     * Load exam questions from API
     */
    async loadExamQuestions() {
        try {
            // Ensure exam filename has .txt extension
            let examName = this.examId;
            if (!examName.endsWith('.txt')) {
                examName += '.txt';
            }

            const response = await fetch(`/api/exam/${encodeURIComponent(examName)}`);
            const data = await response.json();

            if (!data.success) {
                alert(i18n.t('error') + ': ' + data.message);
                window.location.href = '/';
                return;
            }

            this.questions = data.questions;
            document.getElementById('exam-form-title').textContent = data.filename;
            
            // Initialize answers object
            this.questions.forEach(q => {
                this.answers[q.id] = null;
            });

        } catch (error) {
            console.error('Error loading questions:', error);
            alert(i18n.t('error_uploading'));
            window.location.href = '/';
        }
    }

    /**
     * Display current question
     */
    displayCurrentQuestion() {
        if (this.currentQuestionIndex < 0 || this.currentQuestionIndex >= this.questions.length) {
            return;
        }

        const question = this.questions[this.currentQuestionIndex];
        const container = document.getElementById('questions-container');

        let optionsHtml = question.options.map(option => `
            <div class="option">
                <input type="radio" 
                       id="option_${question.id}_${option.letter}" 
                       name="question_${question.id}" 
                       value="${option.letter}"
                       ${this.answers[question.id] === option.letter ? 'checked' : ''}>
                <label for="option_${question.id}_${option.letter}">
                    <strong>${option.letter})</strong> ${option.text}
                </label>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="question-block">
                <div class="question-number">
                    ${i18n.t('question')} ${question.number}
                </div>
                <div class="question-text">
                    ${question.text}
                </div>
                <div class="options">
                    ${optionsHtml}
                </div>
            </div>
        `;

        // Update question counter
        document.getElementById('question-counter').textContent = 
            `${this.currentQuestionIndex + 1} / ${this.questions.length}`;

        // Update button visibility
        this.updateNavigationButtons();
    }

    /**
     * Update navigation buttons visibility
     */
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const submitBtn = document.getElementById('submit-btn');

        if (this.currentQuestionIndex === 0) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'block';
        }

        if (this.currentQuestionIndex === this.questions.length - 1) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'block';
        } else {
            nextBtn.style.display = 'block';
            submitBtn.style.display = 'none';
        }
    }

    /**
     * Navigate to previous question
     */
    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayCurrentQuestion();
        }
    }

    /**
     * Navigate to next question
     */
    nextQuestion() {
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.currentQuestionIndex++;
            this.displayCurrentQuestion();
        }
    }

    /**
     * Record student answer
     */
    recordAnswer(element) {
        const questionId = element.name.replace('question_', '');
        const answer = element.value;
        this.answers[questionId] = answer;
        console.log('Answer recorded:', questionId, answer);
    }

    /**
     * Start countdown timer
     */
    startTimer() {
        const timerElement = document.getElementById('timer');

        this.timerInterval = setInterval(() => {
            this.timeRemaining--;

            // Update display
            const minutes = Math.floor(this.timeRemaining / 60);
            const seconds = this.timeRemaining % 60;
            timerElement.textContent = 
                `${minutes}:${seconds.toString().padStart(2, '0')}`;

            // Add warning classes
            timerElement.classList.remove('warning', 'critical');
            if (this.timeRemaining < 60) {
                timerElement.classList.add('critical');
            } else if (this.timeRemaining < 300) {
                timerElement.classList.add('warning');
            }

            // Auto-submit at 0
            if (this.timeRemaining <= 0) {
                clearInterval(this.timerInterval);
                this.submitExam();
            }
        }, 1000);
    }

    /**
     * Submit exam
     */
    async submitExam() {
        if (this.submitted) return;
        
        const confirmSubmit = confirm(i18n.t('confirm_submit'));
        if (!confirmSubmit) return;

        this.submitted = true;
        clearInterval(this.timerInterval);

        try {
            const response = await fetch('/api/submit-exam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    exam_filename: this.examId,
                    student_name: this.studentName,
                    answers: this.answers,
                    cheating_attempts: this.cheatAttempts,
                    time_spent: Math.floor((Date.now() - this.startTime) / 1000)
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showResults(data);
            } else {
                alert(i18n.t('exam_failed') + ': ' + data.message);
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Error submitting exam:', error);
            alert(i18n.t('error'));
        }
    }

    /**
     * Show exam results
     */
    showResults(data) {
        // Hide exam form, show results
        document.getElementById('exam-form').style.display = 'none';
        document.getElementById('exam-results').style.display = 'block';

        const scorePercentage = data.score;
        const correct = data.correct;
        const total = data.total;

        // Determine grade color
        let gradeColor = '#dc3545'; // red
        if (scorePercentage >= 80) gradeColor = '#28a745'; // green
        else if (scorePercentage >= 60) gradeColor = '#ffc107'; // yellow

        document.getElementById('final-score').innerHTML = `
            <span style="color: ${gradeColor}; font-size: 48px; font-weight: bold;">
                ${scorePercentage.toFixed(1)}%
            </span>
            <p style="color: #666; font-size: 16px; margin-top: 10px;">
                ${correct} / ${total} ${i18n.t('correct_answer')}
            </p>
        `;

        document.getElementById('results-message').innerHTML = `
            <p style="font-size: 18px; margin: 20px 0;">
                ${this.studentName.first} ${this.studentName.last}
            </p>
            <p style="color: #666;">
                ${i18n.t('exam_submitted')}
            </p>
        `;
    }

    /**
     * Dismiss exam due to cheating
     */
    dismissExam(reason) {
        this.submitted = true;
        clearInterval(this.timerInterval);
        alert(reason);
        window.location.href = '/';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.examSystem = new ExamSystem();
});

