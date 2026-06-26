const API_BASE = '';

// Assessments
let currentAssessment = null;
let selectedAnswers = {};

async function generateAssessment() {
    const skill = document.getElementById('assessment-skill').value;
    const difficulty = document.getElementById('assessment-difficulty').value;
    
    if (!skill) {
        alert('Please select a skill');
        return;
    }

    const content = document.getElementById('assessment-content');
    content.innerHTML = '<div class="loading"></div> Generating assessment...';

    try {
        const response = await fetch(`${API_BASE}/assessments/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ skill, difficulty, num_questions: 5 }),
        });

        currentAssessment = await response.json();
        selectedAnswers = {};
        
        if (!currentAssessment || !currentAssessment.questions) {
            content.innerHTML = '<p>Error generating assessment. Please try again.</p>';
            return;
        }
        displayAssessment(currentAssessment);
    } catch (err) {
        content.innerHTML = `<p>Error: ${err.message}</p>`;
    }
}

function displayAssessment(assessment) {
    const content = document.getElementById('assessment-content');
    
    let html = `<h2>${assessment.title}</h2>`;
    
    assessment.questions.forEach((q, idx) => {
        html += `
            <div class="quiz-question" id="question-${idx}">
                <p><strong>Q${idx + 1}:</strong> ${escapeHtml(q.text)}</p>
                <div class="quiz-options">
                    ${q.options.map((opt, optIdx) => `
                        <div class="quiz-option" 
                             onclick="selectAnswer(${idx}, ${optIdx})"
                             id="opt-${idx}-${optIdx}">
                            ${escapeHtml(opt)}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });

    html += `<button class="btn-primary" style="margin-top:16px" onclick="submitAssessment()">Submit Answers</button>`;
    content.innerHTML = html;
}

function selectAnswer(questionIdx, optionIdx) {
    document.querySelectorAll(`#question-${questionIdx} .quiz-option`).forEach(el => {
        el.classList.remove('selected');
    });
    document.getElementById(`opt-${questionIdx}-${optionIdx}`).classList.add('selected');
    selectedAnswers[questionIdx] = optionIdx;
}

async function submitAssessment() {
    if (!currentAssessment) return;
    
    const answers = currentAssessment.questions.map((_, idx) => selectedAnswers[idx] ?? -1);
    
    try {
        const response = await fetch(`${API_BASE}/assessments/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                employee_id: 'user1',
                assessment_id: currentAssessment.id,
                answers: answers,
                time_taken_minutes: 5.0,
            }),
        });

        const result = await response.json();
        
        // Show correct/incorrect answers
        currentAssessment.questions.forEach((q, idx) => {
            const selectedOpt = selectedAnswers[idx];
            if (selectedOpt !== undefined) {
                if (selectedOpt === q.correct_answer) {
                    document.getElementById(`opt-${idx}-${selectedOpt}`).classList.add('correct');
                } else {
                    document.getElementById(`opt-${idx}-${selectedOpt}`).classList.add('incorrect');
                    document.getElementById(`opt-${idx}-${q.correct_answer}`).classList.add('correct');
                }
            }
        });

        const scoreHtml = `
            <div class="results-container" style="margin-top:16px">
                <h3>Score: ${result.score.toFixed(1)}%</h3>
                <p>${result.passed ? '✅ Passed!' : '❌ Keep studying and try again.'}</p>
            </div>
        `;
        document.getElementById('assessment-content').innerHTML += scoreHtml;
    } catch (err) {
        alert('Error submitting: ' + err.message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
